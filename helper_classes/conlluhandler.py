import pandas as pd
class CoNLLUHandler():
    def __init__(self,headers=None,translator=None,source_lang='ta',dest_lang='en'):
        if headers==None:
            self.headers = ['ID','WORD','LEMMA','UPOS','XPOS','FEATS','HEAD','DEPREL','DEPS','MISC']
        else:
            self.headers = headers
        self.header_n = len(self.headers)
        self.tranlator = translator
        self.source_lang = source_lang
        self.dest_lang = dest_lang

    # def tokenize_sentences(self,para):
    #     return sent_tokenize(para)

    # def tokenize_words(self,sent):
    #     return indic_tokenize.trivial_tokenize(sent)

    def isEnglishWord(self,word):
        alph = 'abcdefghiklmnopqrstuvwxyz0123456789'
        word = word.lower()
        for l in alph:
            if l in word:
                return True
        return False

    #constructs the metadata information
    def getMetaData(self,text,index,source,sent_no=0,use_translator=False):
    #     print(text)
        if use_translator:
            translation = self.translator.translate(text,src=self.source_lang, dest=self.dest_lang)
            sent_text_en = ['# text_en = '+translation.text]
        else:
            sent_text_en = ['# text_en = ']
        sent_no = ['# sent_no = '+str(sent_no)]
        sent_id = ['# sent_id = '+str(index)]
        sent_text = ['# text = '+text]
        sent_translit = ['# translit = ']
        sent_source = ['# source = '+source]
        temp = [sent_no,sent_id,sent_text,sent_text_en,sent_translit,sent_source]
        return temp

    #constructs the tokenlevel information
    def getTokenData(self,text,Nan='_'):
        temp=[]
        tokens = self.tokenize_words(text)
        misc_space = 'SpaceAfter=No'
        n = len(tokens)
        
        for i in range(len(tokens)):
            token = tokens[i]
            t=[Nan]*10
            t[0]=i+1
            t[1]=token
            if i+1<n and self.isPunctuation(tokens[i+1]):
                t[-1]=misc_space
            temp.append(t)
        return temp
    
    def isPunctuation(self,char):
        puncs = '!,.?'
        return char in puncs
    
    #constructs the tokenlevel information using spacy
    def getTokenDataUsingSpacy(self,text,Nan,stanza_nlp):
        temp=[]
        sent = stanza_nlp(text)
        tokens = sent.to_dict()[0]
        misc_space = 'SpaceAfter=No'
        n = len(tokens)

        for i in range(len(tokens)):
            token_dict = tokens[i]
            idn = str(token_dict['id'])
            word = token_dict['text'] if 'text' in token_dict.keys() else Nan
            lemma = token_dict['lemma'] if 'lemma' in token_dict.keys() else Nan
            upos = token_dict['upos'] if 'upos' in token_dict.keys() else Nan
            xpos = token_dict['xpos'] if 'xpos' in token_dict.keys() else Nan
            feats = token_dict['feats'] if 'feats' in token_dict.keys() else Nan
            head = str(token_dict['head']) if 'head' in token_dict.keys() else Nan
            deprel = token_dict['deprel'] if 'deprel' in token_dict.keys() else Nan
            t = [idn,word,lemma,upos,xpos,feats,head,deprel,Nan]
            if i+1<n and self.isPunctuation(tokens[i+1]['text']):
                t.append(misc_space)
            else:
                t.append(Nan)
            temp.append(t)
        return temp
    
    def createCoNLLFormatDF(self,simple_df,source='',use_translator=False,use_spacy=False,df_start_row_no=0,df_end_row_no=500,sent_id_start=1,no_of_sents=10): 
        sent_id = sent_id_start
        row_no=0
        final_list = []
        value = None
        
        for index, row in simple_df.iterrows():
            if row_no>=df_start_row_no and row_no<=df_end_row_no:
                text = row['sentences']
                temp_row = [[value]*self.header_n]
                temp_row.extend(self.getMetaData(text,sent_id,source,use_translator))
                if use_spacy:
                    # temp_row.extend(getTokenDataUsingSpacy(text,value,stanza_nlp))
                    pass
                else:
                    temp_row.extend(self.getTokenData(text,value))
                final_list.extend(temp_row)

                sent_id+=1
                if sent_id==(sent_id_start+no_of_sents):
                    break
            row_no+=1
        
        df = pd.DataFrame(final_list,columns=self.headers)
        df.reset_index(drop=True, inplace=True)
        return df
    
    def createCoNLLFormatDFFromParas(self,paras_d,use_translator=False,use_spacy=False,sent_no_start=0): 
        n = len(paras_d['para'])
        final_list = []
        value = None
        
        for i in range(n):
            sentences = self.tokenize_sentences(paras_d['para'][i])
            para_id = paras_d['para_id'][i]
            para_source = paras_d['source'][i]
            sent_no = 0
            for sent in sentences:
                text = sent
                sent_id = para_id + '_' + str(sent_no)
                temp_row = [[value]*self.header_n]
                temp_row.extend(self.getMetaData(text,sent_id,para_source,sent_no_start,use_translator))
                if use_spacy:
                    pass
                    # temp_row.extend(getTokenDataUsingSpacy(text,value,stanza_nlp))
                else:
                    temp_row.extend(self.getTokenData(text))
                final_list.extend(temp_row)
                sent_no+=1
                sent_no_start+=1
        df = pd.DataFrame(final_list,columns=self.headers)
        df.reset_index(drop=True, inplace=True)
        return df
    
    def handleTokenRow(self,row):
        new_line = ''
        row_l = row.split(',')
#         print(row_l)
        comma_present = False
        if(len(row_l)!=10):
            print(row_l)
            if('","' in row):
                row_l.remove('"')
                row_l.remove('"')
            else:
                row_l.remove('')
                row_l.remove('')
                row_l[1]=','
                row_l[2]=','
            comma=True
        index = row_l[0]
        token = row_l[1].strip()
        lemma = row_l[2].strip() if len(row_l[2].strip())>0 else '_'
        upos = row_l[3].strip() if len(row_l[3].strip())>0 else '_'
        xpos = row_l[4].strip() if len(row_l[4].strip())>0 else '_'
        feats = row_l[5].strip() if len(row_l[5].strip())>0 else '_'
        head = row_l[6].strip() if len(row_l[6].strip())>0 else '_'
        deprel = row_l[7].strip() if len(row_l[7].strip())>0 else '_'
        deps = row_l[8].strip() if len(row_l[8].strip())>0 else '_'
        if comma_present:
            misc = 'Translit=,|LTranslit=,'
        else:
            misc = row_l[9].strip() if len(row_l[9].strip())>0 else '_'
        new_line = index+'\t'+token+'\t'+lemma+'\t'+upos+'\t'+xpos+'\t'+feats+'\t'+head+'\t'+deprel+'\t'+deps+'\t'+misc
        return new_line
    
    def convertDFtoCoNLLUFile(self,df=None,csv_path=None,show_print_sttmts=False):
        if csv_path==None:
            csv_path = 'static/temp.csv'
            df.to_csv(csv_path,index=False)
        
        with open(csv_path,'r') as f:
            data =f.read()
            if show_print_sttmts:
                print('Glimpse of data read')
                print(data[:1000])
                print()
                
            #handles the empty or one element row
            data = data.replace('",,,,,,,,,','')
            data = data.replace(',,,,,,,,,','')
        #     data = data.replace(',','\t')
            data_l = data.split('\n')
            data = '\n'.join(data_l[1:])
            
            if show_print_sttmts:
                print('Text after replacement is =')
                print(data[:500])
                print()
            reconstruced_data = []

            segments = data.split('\n\n')
            for segment in segments:
                new_seg = ['\n']
                for row in segment.split('\n'):
                    print(row)
                    if(len(row)==0):
                        continue
                    elif(row.strip()[0]=='#' or '#' in row[:5]):
                        new_seg.append(row)
                    else:
                        new_seg.append(self.handleTokenRow(row))
                reconstruced_data.extend(new_seg)

        new_data = '\n'.join(reconstruced_data[1:])
        new_data = new_data.replace('\n\n','\n')
        return new_data