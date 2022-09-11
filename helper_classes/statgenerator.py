import pandas as pd
import matplotlib
import datetime

class StatGenerator:
    def __init__(self,records_df=None,data_range=None):
        self.records_df = records_df
        self.data_range = data_range
    
    def generateFieldStat(self,field_name):
        if field_name=='FEATS':
            morph_l = self.records_df['FEATS'].to_list()
            morph_feats = {}
            for feat in morph_l:
                if feat and feat!='':
                    tempf = feat.split('|')
                    for f in tempf:
                        if f in morph_feats.keys():
                            morph_feats[f]+=1
                        else:
                            morph_feats[f]=1
            morph_df = pd.DataFrame.from_dict({'FEATS':morph_feats.keys(),'COUNT':morph_feats.values()})
            return morph_df

        tags = self.records_df[field_name]
        tdict = tags.value_counts().to_dict()
        if None in tdict.keys():
            del tdict[None]
        if '' in tdict.keys():
            del tdict['']
        tvals = [str(c) for c in list(tdict.values())]
        tag_count = pd.DataFrame.from_dict({field_name:list(tdict.keys()),'COUNT':tvals})
        return tag_count
    
    def plotGraphFromDF(self,df,name):
        matplotlib.rcParams.update({'font.size': 26})
        fig = df.plot(kind='bar',figsize=(20, 16),x =name,y='COUNT', fontsize=22).get_figure()
        fig.savefig('static/'+name+'.png')
        # matplotlib.pyplot.close()
    
    def generateStats(self):
        dummy_pd = pd.DataFrame([[None]],columns=[''])
        td = datetime.datetime.now()
        ptd = td.strftime("%b %d %Y %H:%M:%S")
        date_l = [['',''],['Stats Created On: ',str(ptd)],['Sheet Range: ',self.data_range]]
        date_df = pd.DataFrame(date_l,columns = ['UPOS','COUNT'])
        pos_count = self.generateFieldStat('UPOS')
        # print(pos_count)
        pos_count["COUNT"] = pd.to_numeric(pos_count["COUNT"])
        self.plotGraphFromDF(pos_count,'UPOS')
        pos_count = pd.concat([pos_count,date_df],ignore_index=True)
        dep_count = self.generateFieldStat('DEPREL')
        dep_count["COUNT"] = pd.to_numeric(dep_count["COUNT"])
        self.plotGraphFromDF(dep_count,'DEPREL')
        morph_count = self.generateFieldStat('FEATS')
        morph_count["COUNT"] = pd.to_numeric(morph_count["COUNT"])
        self.plotGraphFromDF(morph_count,'FEATS')
        misc_count = self.generateFieldStat('MISC')
        misc_count["COUNT"] = pd.to_numeric(misc_count["COUNT"])
        self.plotGraphFromDF(misc_count,'MISC')
        result_df = pd.concat([pos_count,dummy_pd,dep_count,dummy_pd,morph_count,dummy_pd,misc_count], axis=1)
        result_df = result_df.fillna("")
        img_name_l = ['UPOS','DEPREL','FEATS','MISC']
        return result_df,img_name_l