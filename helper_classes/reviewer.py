from re import X
import pandas as pd
class Reviewer:
    def __init__(self,headers=['ID','WORD','LEMMA','UPOS','XPOS','FEATS','HEAD','DEPREL','DEPS','MISC'],transliterate_model=None):
        self.transl_model=transliterate_model
        self.headers = headers
        self.ner_tags = {}
        self.ner_leaves = None
        self.pos_tags = {}
        self.pos_leaves = None
        self.dep_tags = {}
        self.dep_leaves = None
        self.inc_spell = '(!)'
        self.seperator_token = ':'
    
    def load_tags_dict(self,filename=None,type=''):
        if(filename!=None):
            with open(filename,'r') as f:
                data = f.read()
            data_l = data.split('\n')
            dict = {}
            s = set("_")
            for d in data_l:
                tag_l = d.split(',')
                n = len(tag_l)
                n-=1
                if n==0:
                    dict[tag_l[0]] = tag_l[0]
                    s.add(tag_l[0])
                else:
                    s.add(tag_l[n])
                    while(n>0):
                        dict[tag_l[n]] = tag_l[n-1]
                        n-=1
                    dict[tag_l[n]] = tag_l[n]
            if type=='NER':
                self.ner_tags=dict
                self.ner_leaves=s
            elif type=='POS':
                self.pos_tags = dict
                self.pos_leaves=s
            elif type=='DEP':
                self.dep_tags=dict
                self.dep_leaves=s
        
    def validateTwoDFs(self,df1,df2):
        if len(df1)==len(df2):
            print('VALID: The dataframes are of same length')
        else:
            print('ERROR: The two dataframes should be of same length')
            print('Len of DF1: ',len(df1))
            print('Len of DF2: ',len(df2))
    
    def translitWordAndLemma(self,row):
        word = ''
        lemma = ''
        if '-' in str(row['ID']):
            word = row['WORD']
        else:
            word = row['WORD']
            lemma = row['LEMMA']
        trans_word =  self.transl_model.transliterate(word)
        trans_lemma =  self.transl_model.transliterate(lemma)
        misc = 'Translit='+trans_word
        if lemma and lemma!='' and lemma!='_':
            misc += '|'+'LTranslit='+trans_lemma
        if row['MISC']==None or (row['MISC']!=None and row['MISC']=='') or (row['MISC']!=None and row['MISC']=='_'):
            row['MISC'] = misc
        elif row['MISC'].find("Translit")!=-1:
            # as it is already present
            pass
        else:
            row['MISC'] = row['MISC']+'|'+misc
#         misc_l = misc.split('|')
#         misc_l.sort()
#         row['MISC']= '|'.join(misc_l)
        return row
    
    def sortOrderMorphFeats(self,feats,isMultiword):
        if isMultiword:
            return '_'
        if feats==None or (feats!=None and feats==''):
            return self.inc_spell + '_'
        if not isMultiword and feats=='_':
            return self.inc_spell + '_'
        feats_l = feats.split('|')
        for i in range(len(feats_l)):
            x = feats_l[i].split('=')
            if(len(x)<=1):
                return self.inc_spell + feats
            feats_l[i] =  x[0].capitalize() + '=' + x[1].capitalize()
        feats_l.sort()
        return '|'.join(feats_l)
    
    
    def formatXPOS(self,xpos,isMultiword):
        # if upos==None or xpos==None or (xpos!=None and (str(xpos).strip()=='' or '_' in str(xpos))):
        #     return None
        if xpos==None or (xpos!=None and str(xpos).strip()=='') or (xpos!=None and xpos.find('_')==0):
            if isMultiword:
                return '_'
            return '_'
        if xpos.find(self.seperator_token) > 0:
            return xpos
        if self.pos_leaves!=None:
            if xpos not in self.pos_leaves:
                xpos = self.inc_spell + xpos
                return xpos
            cur = xpos
            newxpos = cur
            while self.pos_tags[cur]!=cur:
                cur = self.pos_tags[cur]
                newxpos = cur+self.seperator_token+newxpos
            newxpos = newxpos.upper()
            return newxpos
    
    def formatUPOS(self,upos,xpos,isMultiword):
        if xpos==None or (xpos!=None and str(xpos).strip()=='') or (xpos!=None and xpos.find('_')==0):
            if isMultiword:
                return '_'
            if upos!=None:
                return self.inc_spell+upos
            return self.inc_spell
        upos_tag_from_xpos = xpos.split('_')[0]
        if upos!=None and str(upos).strip()!='' and str(upos)!='_':
            if upos!=upos_tag_from_xpos:
                return self.inc_spell+upos
        return upos_tag_from_xpos
    
    def addUnderScoreToToken(self,row):
        for header in self.headers:
            if row[header]==None or (row[header]!=None and str(row[header]).strip()=='') :
                row[header]='_'
        return row
    
    def formatNER(self,nerr):
        if "=" not in nerr:
            return 'ERROR' 
        ner = nerr.split("=")[1]
        bio = ner.split('_')[0]
        ner_name = ner.split('_')[1]
        ner_name = ner_name.upper()
        if self.ner_leaves!=None and ner_name not in self.ner_leaves:
            return self.inc_spell+nerr
        cur_ner = ner_name
        full_ner = cur_ner
        while self.ner_tags[cur_ner]!=cur_ner:
            cur_ner  = self.ner_tags[cur_ner]
            full_ner = cur_ner+'_'+full_ner
        return 'Entity='+bio+'_'+full_ner
    
    def formatRow(self,row):
        if self.getTypeOfSent(row)=='token':
            isMultiword = False
            if row['ID']==None or (row['ID']!=None and row['ID'] in ["","_"]):
                row['ID']=self.inc_spell
            elif '-' in row['ID']:
                isMultiword=True
            try:
                row['FEATS'] = self.sortOrderMorphFeats(row['FEATS'],isMultiword)
            except:
                row['FEATS'] = self.inc_spell+str(row['FEATS'])
            try:
                row['XPOS']= self.formatXPOS(row['XPOS'],isMultiword)
            except:
                row['XPOS'] = self.inc_spell + str(row['XPOS'])
            try:
                row['UPOS'] = self.formatUPOS(row['UPOS'],row['XPOS'],isMultiword)
            except:
                row['UPOS'] = self.inc_spell+str(row['UPOS'])
            if row['LEMMA']:
                if isMultiword:
                    row['LEMMA']='_'
                elif row['LEMMA']!=None and row['LEMMA']=='_':
                    row['LEMMA']=self.inc_spell + '_'
            if row['HEAD']:
                if isMultiword:
                    row['HEAD']='_'
                elif row['HEAD']!=None and row['HEAD']=='_':
                    row['HEAD']=self.inc_spell + '_'
            if row['DEPREL']:
                row['DEPREL'] = row['DEPREL'].lower()
                row['DEPREL'] = row['DEPREL'].replace(' ','')
                dep = row['DEPREL'].split(':')
                if len(dep)>1:
                    dep_name = dep[1]
                else:
                    dep_name = dep[0]
                if not isMultiword and dep_name=='_':
                    row['DEPREL'] = self.inc_spell + dep_name
                elif self.dep_leaves!=None and dep_name not in self.dep_leaves:
                    row['DEPREL'] = self.inc_spell + row['DEPREL'] 
            if row['MISC']==None or (row['MISC']!=None and (str(row['MISC']).strip()=='' or str(row['MISC'])=='_')):
                row['MISC'] ='_'
            else:
                misc_l = row['MISC'].split('|')
                error = False
                for i in range(len(misc_l)):
                    if 'Entity' in misc_l[i]:
                        try:
                            x = self.formatNER(misc_l[i])
                        except:
                            x==self.inc_spell
                            # error = True
                        if x==self.inc_spell:
                            error = True
                        else:
                            misc_l[i] = x
                row["MISC"] = "|".join(misc_l)
                if error:
                    row["MISC"] = self.inc_spell+row["MISC"]
            row = self.addUnderScoreToToken(row)
            row = self.translitWordAndLemma(row)
        return row
    
    def formConflictText(self,sent_id,line_no,header,val1,val2):
        con = 'SENT_ID = '+sent_id+': Conflict present at line '+str(line_no) +' under column '+header
        con+='\n'+'Val in sheet 1:'+str(val1)+'\nVal in sheet 2:'+str(val2)
        return con
    
    def getTypeOfSent(self,row):
        if row['ID']==None or (row['ID']!=None and row['ID']==''):
            return 'blank'
        elif row['ID']!='' and '#'==str(row['ID'])[0]:
            return 'metadata'
        return 'token'
    
    def formatOneSheet(self,df):
        review_df=df.copy()
        n = len(review_df)
        sent_txt = ''
        for i in range(n):
            review_r = review_df.iloc[i]
            if self.getTypeOfSent(review_r)=='metadata':
                if '# text =' in str(review_r['ID']):
                    sent_txt=str(review_r['ID']).split('=')[1].strip()
                elif '# translit' in str(review_r['ID']):
                    review_r['ID']='# translit = '+self.transl_model.transliterate(sent_txt)
                elif '# text_en' in str(review_r['ID']):
                    if '=' not in str(review_r['ID']) or ('=' in str(review_r['ID']) and str(review_r['ID']).split('=')[1].strip()==''):
                        review_r['ID'] = self.inc_spell + str(review_r['ID'])
            review_r = self.formatRow(review_r)
#             if self.getTypeOfSent(review_r)=='token':
#                 review_r = self.addUnderScoreToToken(review_r)
            review_df.iloc[i] = review_r
        return review_df
    
    def reviewTwoSheets(self,df1,df2):
        review_df = df1.copy()
        second_df = df2.copy()
        sent_txt=''
        sent_no=''
        sent_id = ''
        n = len(review_df)
        conflicts = []
        
        for i in range(n):
            review_r = review_df.iloc[i]
            sec_r = second_df.iloc[i]
            review_r = self.formatRow(review_r)
            sec_r = self.formatRow(sec_r)
            
            for header in self.headers:
                if header=='ID' and self.getTypeOfSent(review_r)=='metadata':
                    if '# text =' in str(review_r[header]):
                        sent_txt=str(review_r[header]).split('=')[1].strip()
                    elif '# translit' in str(review_r[header]):
                        review_r[header]='# translit = '+self.transl_model.transliterate(sent_txt)
                    elif '# sent_id' in str(review_r[header]):
                        sent_id = review_r[header].split('=')[1].strip()
                elif review_r[header]!=sec_r[header]:
                    conflicts.append(self.formConflictText(sent_id,i+1,header,review_r[header],sec_r[header]))
                    review_r[header] = '(!)'+str(review_r[header])+' :: '+str(sec_r[header])
            
            # adding the translit and ltranslit for word and lemma
            if self.getTypeOfSent(review_r)=='token':
                review_r = self.translitWordAndLemma(review_r)
            review_df.iloc[i] = review_r
        return review_df,conflicts
    
    def convertDFtoDict(self,review_df):
        n = len(review_df)
#         reviewer = Reviewer()
        reviewdict = dict()
        metadata_l = []
        token_l = []
        sid = ''
        for i in range(n):
            review_r = review_df.iloc[i]
            # review_r = self.formatRow(review_r)
            if self.getTypeOfSent(review_r)=='blank' and sid!='':
                reviewdict[sid] = {'metadata':metadata_l,'tokens':token_l}
                metadata_l = []
                token_l = []
                sid = ''
            elif self.getTypeOfSent(review_r)=='blank':
                pass
            elif self.getTypeOfSent(review_r)=='metadata':
                first_token = str(review_r['ID'])
                mname = first_token.split('=')[0].strip()
                val = first_token.split('=')[1].strip()
                if mname == '# sent_id':
                    sid = val
                metadata_l.append(review_r.tolist())
            else:
                token_l.append(review_r.tolist())
        if metadata_l!=[] and token_l!=[] and sid!='':
            reviewdict[sid] = {'metadata':metadata_l,'tokens':token_l}
        return reviewdict
    
    def compareTwoListTokenValues(self,l1,l2,name1,name2,sid):
        n = len(l1)
        conflicts = []
        for i in range(n):
            if l1[i][1]!=l2[i][1]:
                conflict = 'Token Value Conflict (sent id:'+sid+') : '+name1+'('+l1[i][0]+'th token: '+l1[i][1]+')'
                conflict +=' and '+name2+'('+l2[i][0]+'th token: '+l2[i][1]+')'
                conflicts.append(conflict)
        return conflicts
    
    def findConflictsBtwTwoSheets(self,record_df_list):
        rdict1 = self.convertDFtoDict(record_df_list[0])
        ids1 = list(rdict1.keys())

        rdict2 = self.convertDFtoDict(record_df_list[1])
        ids2 = list(rdict2.keys())

        conflicts_l = []
        for i in range(len(ids2)):
            sid = ids2[i]
            if sid in ids1:
                if len(rdict1[sid]['tokens'])!=len(rdict2[sid]['tokens']):
                    conflict = 'Sentence id = '+sid+' has conflict in two sheets'
                    conflict += ' and with sheet 1 token count = '+str(len(rdict1[sid]['tokens']))
                    conflict += ' and with sheet 2 token count = '+str(len(rdict2[sid]['tokens']))
                    conflicts_l.append(conflict)
                else:
                    cons = self.compareTwoListTokenValues(rdict1[sid]['tokens'],rdict2[sid]['tokens'],'Sheet1','Sheet2',sid)
                    conflicts_l.extend(cons)
        return conflicts_l

    def findConflictsBtwTwoSheetsAndReviewSheet(self,record_df_list,review_df):
        review_dict = self.convertDFtoDict(review_df)
        rids = list(review_dict.keys())

        rdict1 = self.convertDFtoDict(record_df_list[0])
        ids1 = list(rdict1.keys())

        rdict2 = self.convertDFtoDict(record_df_list[1])
        ids2 = list(rdict2.keys())

        conflicts_l = []
        for i in range(len(rids)):
            sid = rids[i]
            if sid in ids1:
                if len(review_dict[sid]['tokens'])!=len(rdict1[sid]['tokens']):
                    conflict = 'Sentence id = '+sid+' has conflict in two sheets'
                    conflict += ' with review sheet token count = '+str(len(review_dict[sid]['tokens']))
                    conflict += ' and with sheet 1 token count = '+str(len(rdict1[sid]['tokens']))
                    conflicts_l.append(conflict)
                else:
                    cons = self.compareTwoListTokenValues(review_dict[sid]['tokens'],rdict1[sid]['tokens'],'Review Sheet','Sheet1',sid)
                    conflicts_l.extend(cons)
            if sid in ids2:
                if len(review_dict[sid]['tokens'])!=len(rdict2[sid]['tokens']):
                    conflict = 'Sentence id = '+sid+' has conflict in two sheets'
                    conflict += ' with review sheet token count = '+str(len(review_dict[sid]['tokens']))
                    conflict += ' and  with sheet 2 token count = '+str(len(rdict2[sid]['tokens']))
                    conflicts_l.append(conflict)
                else:
                    cons = self.compareTwoListTokenValues(review_dict[sid]['tokens'],rdict2[sid]['tokens'],'Review Sheet','Sheet2',sid)
                    conflicts_l.extend(cons)
        return conflicts_l
    
    def extractSampleExamplesDfFromSheets(self,record_df_list,review_df):
        review_dict = self.convertDFtoDict(review_df)
        rids = list(review_dict.keys())

        rdict1 = self.convertDFtoDict(record_df_list[0])
        ids1 = list(rdict1.keys())

        rdict2 = self.convertDFtoDict(record_df_list[1])
        ids2 = list(rdict2.keys())
        blank = ['','','','','','','','','','']
        review_l = []
        sheet1_l = []
        sheet2_l = []
        message_l = []
        for i in range(len(rids)):
            sid = rids[i]
            review_l.extend(review_dict[sid]['metadata'])
            review_l.extend(review_dict[sid]['tokens'])
            review_l.append(blank)

            if sid in ids1:
                if len(review_dict[sid]['tokens'])==len(rdict1[sid]['tokens']):
                    sheet1_l.extend(review_dict[sid]['metadata'])
                    sheet1_l.extend(rdict1[sid]['tokens'])
                    sheet1_l.append(blank)
                else:
                    message = 'Sid:'+sid+', Review sheet (token nos='+str(len(review_dict[sid]['tokens']))
                    message +=') and in Sheet 1 (token nos='+ str(len(rdict1[sid]['tokens'])) + ')'
                    message_l.append(message)
            else:
                message = sid +' present in Review Sheet not found in Sheet 1'
                message_l.append(message)
            if sid in ids2:
                if len(review_dict[sid]['tokens'])==len(rdict2[sid]['tokens']):
                    sheet2_l.extend(review_dict[sid]['metadata'])
                    sheet2_l.extend(rdict2[sid]['tokens'])
                    sheet2_l.append(blank)
                else:
                    print('See the tokens in review =')
                    print(review_dict[sid]['tokens'])
                    message = 'Sid:'+sid+', Review sheet (token nos='+str(len(review_dict[sid]['tokens']))
                    message +=') and in Sheet 2 (token nos='+ str(len(rdict2[sid]['tokens'])) + ')'
                    message_l.append(message)
            else:
                message = sid +' present in Review Sheet not found in Sheet 1'
                message_l.append(message)
        sheet1_pd = pd.DataFrame(sheet1_l,columns = self.headers)
        sheet2_pd = pd.DataFrame(sheet2_l,columns = self.headers)
        newreview_pd = pd.DataFrame(review_l,columns = self.headers)
        return sheet1_pd,sheet2_pd,newreview_pd,message_l
    
    def formListfromDictSheet(self,dict,index = 1,review_ids=None):
        ids = dict.keys()
        tot_l = []
        blank = ['','','','','','','','','','']
        for id in dict:
            if (review_ids==None or id not in review_ids):
                dict[id]['metadata'][0][0] = '# sent_no = '+str(index)
                tot_l.extend(dict[id]['metadata'])
                tot_l.extend(dict[id]['tokens'])
                tot_l.append(blank)
                index+=1
        return tot_l,index
    
    def formDfFromSheets(self,record_df_list,review_df,index=1):
        review_dict = self.convertDFtoDict(review_df)
        rids = list(review_dict.keys())

        rdict1 = self.convertDFtoDict(record_df_list[0])
        rdict2 = self.convertDFtoDict(record_df_list[1])

        comp_l = []
        review_l,index = self.formListfromDictSheet(review_dict,index)
        sheet1_l,index = self.formListfromDictSheet(rdict1,index,rids)
        sheet2_l,index = self.formListfromDictSheet(rdict2,index,rids)
        comp_l.extend(review_l)
        comp_l.extend(sheet1_l)
        comp_l.extend(sheet2_l)

        complete_df = pd.DataFrame(comp_l,columns = self.headers)
        return complete_df,index
    
    def check_multiwords(self,data_df):
        multiwords_d = dict()
        no = 0 
        sent_id= ''
        multiword_text = ''
        for index,row in data_df.iterrows():
            if self.getTypeOfSent(row)=='metadata' and '# sent_id' in str(row['ID']):
                sent_id = row['ID'].split('=')[1].strip()
            if self.getTypeOfSent(row)=='token':
                if row['ID']!=None and '-' in row['ID']:
                    mword_id = row['ID']
                    mword = row['WORD']
                    x,y = mword_id.split('-') 
                    no = int(y.strip()) - int(x.strip()) + 1
                    multiword_text = row['WORD'] + ' segmented into :'
                    first=True
                elif no>0:
                    if first:
                        multiword_text += ' '+row['WORD']
                        first=False
                    else:
                        multiword_text += ' + '+row['WORD']
                    no-=1
                else:
                    if multiword_text!='':
                        if sent_id in multiwords_d:
                            multiwords_d[sent_id].append(multiword_text)
                        else:
                            multiwords_d[sent_id]= [multiword_text]
                    multiword_text = ''
        return multiwords_d