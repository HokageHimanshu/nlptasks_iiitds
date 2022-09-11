from sklearn.metrics import cohen_kappa_score
import pandas as pd
import datetime

class InterAnnotatorAgreement:
    def __init__(self):
        pass    
    
    def validateDfs(self,df1,df2):
        return len(df1)==len(df2)
    
    def calculateIAA(self,df1,df2,field_name):
        X = self.retrieveAnnotations(df1,df2,field_name=field_name)
        score = cohen_kappa_score(X['label1'], X['label2'])
        score  = round(score,4)
        return score
    
    def retrieveAnnotations(self,df1,df2,field_name='UPOS'):
        n = len(df1)
        label1=[]
        label2=[]
        sent_no_l=[]
        sent_no=-1
        for i in range(n):
            row1 = df1.iloc[i]
            row2 = df2.iloc[i]
            if row1['ID'] and 'sent_id' in row1['ID']:
                sent_no = row1['ID'].split('=')[1].strip()
            elif(row1['ID'] and row2['ID'] and row1['ID'].isdigit() and row2['ID'].isdigit()):
                label1.append(row1[field_name])
                label2.append(row2[field_name])
                sent_no_l.append(sent_no)
        return pd.DataFrame.from_dict({'sent_id':sent_no_l,'label1':label1,'label2':label2})
    
    def retrieveAnnotationsUsingPD(self,df1,df2,field_name='UPOS'):
        label1 = list(df1[field_name].dropna())
        label2 = list(df2[field_name].dropna())
        return [label1,label2]
    
    def calcScoresBetweenDfsAndReviewSheet(self,sheet1_pd,sheet2_pd,review_pd):
        td = datetime.datetime.now()
        ptd = td.strftime("%b %d %Y %H:%M:%S")
        score_table_dict = {}
        score_table_dict['headers'] = ['IAA Type']
        df1 = sheet1_pd
        df2 = review_pd
        print(self.validateDfs(df1,df2))
        features = ['UPOS','XPOS','DEPREL','HEAD']
        score_table_dict['headers'].extend(features)
        name = 'IAA Between Sheet 1 and Review Sheet'
        fans = [['',''],[name,' '],['Created on: '+str(ptd),''],['','']]
        ans = []
        temprow = [name]
        for feature in features:
            score = self.calculateIAA(df1,df2,feature)
            ans.append([feature,score])
            temprow.append(score)
        score_table_dict['row1'] = temprow
        ans.extend(fans)
        ina_df_r1 = pd.DataFrame(ans,columns={'FEATURE','IAA_SCORE'})

        df1 = sheet2_pd
        df2 = review_pd
        print(self.validateDfs(df1,df2))
        name = 'IAA Between Sheet 2 and Review Sheet'
        fans = [['',''],[name,' '],['Created on: '+str(ptd),''],['','']]
        ans=[]
        temprow = [name]
        for feature in features:
            score = self.calculateIAA(df1,df2,feature)
            ans.append([feature,score])
            temprow.append(score)
        score_table_dict['row2'] = temprow
        ans.extend(fans)
        ina_df_r2 = pd.DataFrame(ans,columns={'FEATURE','IAA_SCORE'})

        df1 = sheet1_pd
        df2 = sheet2_pd
        print(self.validateDfs(df1,df2))
        name = 'IAA Between Sheet 1 and Sheet 2'
        fans = [['',''],[name,' '],['Created on: '+str(ptd),''],['','']]
        ans = []
        temprow = [name]
        for feature in features:
            score = self.calculateIAA(df1,df2,feature)
            ans.append([feature,score])
            temprow.append(score)
        score_table_dict['row3'] = temprow
        ans.extend(fans)
        ina_df_12 = pd.DataFrame(ans,columns={'FEATURE','IAA_SCORE'})

        dummy_pd = pd.DataFrame([[None]],columns=[''])
        result_df = pd.concat([ina_df_r1,dummy_pd,ina_df_r2,dummy_pd,ina_df_12], axis=1)
        result_df = result_df.fillna("")
        return result_df,score_table_dict