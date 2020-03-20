#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!/usr/bin/python 
# -*- coding: utf-8 -*-

import sys
import os

sys.path.append(os.path.abspath(r'C:\Users\Mma4\Desktop\DanalysisProcess'))

import pyodbc
import pandas as pd
import numpy as np
import pandas as pd
from pyecharts import Pie,Timeline,Bar,Overlap,Line,Page
import random
import numpy as np
from pandas import DataFrame,Series
from pyecharts import configure
import time
import re
import warnings
from Tool import time_value,Raw_Data,replace_str,key_grouper
from pyecharts import configure

warnings.filterwarnings("ignore")

from price_Missing_SQL import get_updated_raw_data
get_updated_raw_data()




class price_ratio():
    
    def __init__(self):
        
        self.data = pd.read_csv(r"C:\Users\Mma4\Desktop\DanalysisProcess\price failure 3M with ongoing.csv")

    def processor(self):
        
        df_key_price,All_result_combine_updated,TaskownerUserName = self.dataprocess()
        
        df_Ratio2,df_Ratio,All_result_combine_updated,df_FailureType_updated0,FailureType_list,numerator_columns_list,names,label_color,denomonator_columns_list,df_Ratio_1,df_Ratio_2,length_date = self.dataprossce1(df_key_price,All_result_combine_updated,TaskownerUserName)
        
        timeline = self.datagraph(df_Ratio2,df_Ratio,All_result_combine_updated,df_FailureType_updated0,FailureType_list,numerator_columns_list,names,label_color,denomonator_columns_list,df_Ratio_1,df_Ratio_2,length_date)
        
        timeline_two = self.datagraph1(df_Ratio2,df_Ratio,All_result_combine_updated,df_FailureType_updated0,FailureType_list,numerator_columns_list,names,label_color,denomonator_columns_list,df_Ratio_1,df_Ratio_2,length_date)
        
        self.finalgraph(timeline,timeline_two)

    def dataprocess(self):
        
        df_key_price = self.data

        DoneFailureUserName = df_key_price.DoneFailureUserName.to_list()
        TaskownerUserName = df_key_price.TaskownerUserName.to_list()
        df_key_price.DoneFailureUserName = replace_str(DoneFailureUserName,'@xxxxxxx.com','')  # List,需要Remove的字符串
        df_key_price.TaskownerUserName = replace_str(TaskownerUserName,'@xxxxxxx.com','')  # List,需要Remove的字符串

        df_key_price.to_csv(r'C:\Users\Mma4\Desktop\DanalysisProcess\price_Owner_Ratio.csv')

        df_key_price.rename(columns = {'FailureGenerateTime2':'FailureGenerateTime'}, inplace = True)


        Name_list_all = list(set(df_key_price.TaskownerUserName.to_list()))

        Owner=Name_list_all


        TaskownerUserName_list = Owner

        df_key_price.ActionTime = pd.to_datetime(df_key_price.ActionTime)

        df_key_price.FailureGenerateTime = pd.to_datetime(df_key_price.FailureGenerateTime1)

        denomonator_follow_list = df_key_price.TaskownerUserName

        denomonator_follow_list = [x if x in TaskownerUserName_list else "other" for x in denomonator_follow_list] 

        df_key_price.TaskownerUserName = denomonator_follow_list 

        ###########------------------------分子----------------------------###########------------------------分子----------------------------

        result_ongoing_histroical = key_grouper(df = df_key_price,index = 'ActionTime', 
                                    level_1 = 'DoneFailureUserName',level_2 ='DoneType',fre = 'D')

        result_ongoing_histroical_Updated = result_ongoing_histroical.T

        # ## --------------------------分母------------------------------------### --------------------------分母----------------------------------


        result_ongoing_histroical_denomonator = key_grouper(df = df_key_price,index = 'FailureGenerateTime', 
                                    level_1 = 'TaskownerUserName',level_2 ='FailureType',fre = 'D')

        result_ongoing_histroical_denomonator_Updated = result_ongoing_histroical_denomonator.T


        #------------------------------------------------------定义参数---------------------------------------------------------------
        All_result_combine = pd.concat([result_ongoing_histroical_denomonator_Updated,result_ongoing_histroical_Updated],axis = 0)
        try:
            All_result_combine = All_result_combine.drop(['Null'], axis=1)
        except:
            pass
        All_result_combine_T = All_result_combine.T

        All_result_combine.sort_index(inplace = True)
        Timeline_list = All_result_combine.columns

        All_result_combine_T['Weekdays'] = All_result_combine_T.index.to_series().dt.dayofweek

        result_Sum_weekdays = All_result_combine_T[All_result_combine_T.Weekdays!=6]  # 不要周日
        result_Sum_weekdays = result_Sum_weekdays[result_Sum_weekdays.Weekdays!=5]# 不要周6
        All_result_combine = result_Sum_weekdays.T

        All_result_combine.reset_index().to_excel(r'C:\Users\Mma4\Desktop\DanalysisProcess\price_Owner2_test.xls')
        All_result_combine_updated = pd.read_excel(r'C:\Users\Mma4\Desktop\DanalysisProcess\price_Owner2_test.xls', index_col=0)
        All_result_combine_updated = All_result_combine_updated[All_result_combine_updated.TaskownerUserName.isin(Owner)]
        
        return df_key_price,All_result_combine_updated,TaskownerUserName


    def dataprossce1(self,df_key_price,All_result_combine_updated,TaskownerUserName):

        df_key_price_name_sort = df_key_price.groupby(TaskownerUserName)['InvestmentId'].count().sort_values(ascending=False)

        price_name_sort_list = replace_str(df_key_price_name_sort.index,'@xxxxxx.com','')

        price_name_sort_list = pd.DataFrame(price_name_sort_list)
        price_name_sort_list.columns = ['TaskownerUserName']

        All_result_combine_updated = price_name_sort_list.merge(All_result_combine_updated, on='TaskownerUserName', how='left')


        numerator_columns_list = df_key_price.DoneType.to_list()#.unique()
        numerator_columns_list = list(set(numerator_columns_list))  ## 分子的columns list

        denomonator_columns_list = df_key_price.FailureType.to_list()#.unique()
        denomonator_columns_list = list(set(denomonator_columns_list)) ## 分母的columns list
        #All_result_combine['gianfelice.meli']
        Name_key = All_result_combine_updated.TaskownerUserName.unique()
        # Type_key = All_result_combine_updated.FailureType.unique()
        All_result_combine_updated.head()
        # Type_key
        Name_key = pd.DataFrame( Name_key,columns =['TaskownerUserName'])

        label_color = ["#c23531",
        "#2f4554","#61a0a8","#d48265","#749f83","#ca8622","#bda29a","#6e7074","#546570",
        "#c4ccd3","#f05b72","#ef5b9c","#f47920","#905a3d","#fab27b","#2a5caa",
        "#444693","#726930","#b2d235","#6d8346","#ac6767","#1d953f","#6950a1","#918597"]

        FailureType_list = [x for x in All_result_combine_updated.FailureType.unique()]

        #print(FailureType_list)
        names = globals()
        combine_numerator= pd.DataFrame()
        combine_denomonator= pd.DataFrame()

        for j in range(len(FailureType_list)):  

            names['df_FailureType' + str(j) ]  =All_result_combine_updated[All_result_combine_updated.FailureType == FailureType_list[j]] 
            names['df_FailureType_updated' + str(j) ] = Name_key.merge( names['df_FailureType' + str(j) ], on='TaskownerUserName', how='left')
            names['df_FailureType_updated' + str(j) ] = names['df_FailureType_updated' + str(j) ].fillna(0)

            names['df_FailureType_updated' + str(j) ].FailureType = [x if x!= 0 else FailureType_list[j] for x in names['df_FailureType_updated' + str(j) ].FailureType]
            names['legened_name' + str(j) ] = names['df_FailureType' + str(j) ].FailureType.values[0]
            names['Bar_Y_All_Values' + str(j) ]= names['df_FailureType_updated' + str(j) ].drop(['TaskownerUserName','FailureType'],axis = 1)

            length_date = len(names['Bar_Y_All_Values' + str(j) ].columns)
            length_name = len(names['legened_name' + str(j) ])

            for l in range(len(names['Bar_Y_All_Values' + str(j) ].columns)) : 

                names['Bar_Y' + str(j) + str(l)] =  names['Bar_Y_All_Values' + str(j) ][ names['Bar_Y_All_Values' + str(j) ].columns[l]] 

            for L in range(len(df_FailureType_updated0.TaskownerUserName.to_list())): 

                names['Bar_time_Y' + str(j) + str(L) ] = names['df_FailureType_updated' + str(j) ].iloc[:,3:].values[L]

            if names['legened_name' + str(j) ] in numerator_columns_list:
                combine_numerator = pd.concat([combine_numerator,names['df_FailureType_updated' + str(j)]])

            if names['legened_name' + str(j) ] in denomonator_columns_list:   
                combine_denomonator = pd.concat([combine_denomonator,names['df_FailureType_updated' + str(j)]])


        combine_numerator = combine_numerator[df_FailureType_updated0.columns]
        combine_denomonator = combine_denomonator[df_FailureType_updated0.columns]
        combine_numerator_2 = combine_numerator[combine_numerator.FailureType.isin(['HistoricalFailure_System','OngoingFailure_System'])]

        Ratio_1_numerator = combine_numerator.groupby('TaskownerUserName').sum()
        Ratio_1_numerator = Ratio_1_numerator.reindex(price_name_sort_list.TaskownerUserName)  

        Ratio_2_numerator = combine_numerator_2.groupby('TaskownerUserName').sum()
        Ratio_2_numerator = Ratio_2_numerator.reindex(price_name_sort_list.TaskownerUserName) 

        Ratio_1_denomonator = combine_denomonator.groupby('TaskownerUserName').sum()
        Ratio_1_denomonator =Ratio_1_denomonator.reindex(price_name_sort_list.TaskownerUserName)
        df_Ratio = (Ratio_1_numerator/Ratio_1_denomonator)
         ## 处理 没有分母导致无限大的情况
        df_Ratio =df_Ratio.replace([np.inf, -np.inf], np.nan).fillna(0)

        df_Ratio2 = (Ratio_2_numerator/Ratio_1_denomonator)
         ## 处理 没有分母导致无限大的情况
        df_Ratio2 =df_Ratio2.replace([np.inf, -np.inf], np.nan).fillna(0)

        df_Ratio_1 = df_Ratio.T.astype(float)
        df_Ratio_2 = df_Ratio2.T.astype(float)

        ## 避免了 时间长度不一

        if len(df_Ratio_1.index)- len(All_result_combine_updated.iloc[:,3:].columns)>0:

            df_Ratio_1 = df_Ratio_1.iloc[len(df_Ratio_1.index)- len(All_result_combine_updated.iloc[:,3:].columns):,:]
            df_Ratio_2 = df_Ratio_2.iloc[len(df_Ratio_2.index)- len(All_result_combine_updated.iloc[:,3:].columns):,:]
        if len(df_Ratio_1.index)- len(All_result_combine_updated.iloc[:,3:].columns)<0:
            All_result_combine_updated = All_result_combine_updated.iloc[len(All_result_combine_updated.iloc[:,3:].columns)- len(df_Ratio_1.index):,:]

        return df_Ratio2,df_Ratio,All_result_combine_updated,df_FailureType_updated0,FailureType_list,numerator_columns_list,names,label_color,denomonator_columns_list,df_Ratio_1,df_Ratio_2,length_date


#------------------------------------------------------图1---------------------------------------------------------------

    def datagraph(self,df_Ratio2,df_Ratio,All_result_combine_updated,df_FailureType_updated0,FailureType_list,numerator_columns_list,names,label_color,denomonator_columns_list,df_Ratio_1,df_Ratio_2,length_date):

        Bar_time_x =[x.strftime('%m-%d')for x in All_result_combine_updated.iloc[:,3:].columns]
        configure(global_theme='darksalmon')   

        for L2 in range(len(df_FailureType_updated0.TaskownerUserName.to_list())):
            ## -----------------14:40---------------

            bar_Done0 = Bar(title = df_FailureType_updated0.TaskownerUserName.to_list()[L2],subtitle = 'Workload',
            title_pos = 'center',height = 360,width='100%') 

            for j0 in range(len(FailureType_list)):
                for j1 in range(len(numerator_columns_list)):
                    if  names['legened_name' + str(j0)] == numerator_columns_list[j1]:
                        #print(numerator_columns_list[j3])
                        bar_Done0.add(names['legened_name' + str(j0) ],Bar_time_x,names['Bar_time_Y' + str(j0) + str(L2) ],is_splitline_show = False,
                                              is_stack=True,is_label_show=False,xaxis_rotate = 25,xaxis_margin = 5,
                                              legend_pos = 'left',legend_orient = 'vertical',is_more_utils = True,
                                              is_toolbox_show=True,bar_category_gap = '35%',label_color = label_color,yaxis_label_textsize=10,
                                              is_datazoom_show = True,datazoom_type="slider",datazoom_range=[80,100])
                else :
                    pass

            bar_task0 = Bar(title = df_FailureType_updated0.TaskownerUserName.to_list()[L2],subtitle = 'Workload',
                title_pos = 'center',height = 360,width='100%') 

            for j0 in range(len(FailureType_list)):
                for j1 in range(len(denomonator_columns_list)):
                    if  names['legened_name' + str(j0)] == denomonator_columns_list[j1]:
                        #print(denomonator_columns_list[j3])
                        bar_task0.add(names['legened_name' + str(j0) ],Bar_time_x,names['Bar_time_Y' + str(j0) + str(L2) ],is_splitline_show = False,
                                              is_stack=True,is_label_show=False,xaxis_rotate = 25,xaxis_margin = 5,
                                              legend_pos = 'left',legend_orient = 'vertical',is_more_utils = True,
                                              is_toolbox_show=True,bar_category_gap = '35%',label_color = label_color,yaxis_label_textsize=10,
                                              is_datazoom_show = True,datazoom_type="slider",datazoom_range=[80,100])

                else :
                    pass

            line_ratio =Line('',background_color = 'white',title_text_size = 20,title_pos = 'center')

            line_ratio.add("Completeness Ratio 1",Bar_time_x,df_Ratio_1[df_FailureType_updated0.TaskownerUserName.to_list()[L2]].to_list()
                       ,is_more_utils = True,is_splitline_show = False,is_label_show = False,is_smooth=True,mark_line=['average'],
                       line_color = [' black'],legend_pos = 'left',legend_orient = 'vertical',line_type = 'dotted',line_width  = '2')

            line_ratio.add("Completeness Ratio 2",Bar_time_x,df_Ratio_2[df_FailureType_updated0.TaskownerUserName.to_list()[L2]].to_list(),
                           is_label_show = False,is_smooth=True,mark_line=['average'],is_splitline_show = False,
                           is_fill = True,area_opacity=0.1,is_more_utils = True,line_color = ['red'],
                           legend_pos = 'left',legend_orient = 'vertical',area_color='#000') #area_opacity=0.0001 #is_fill = True,  

            mark_line = []
            for mark_list in np.array(df_Ratio_1[df_FailureType_updated0.TaskownerUserName.to_list()[L2]].to_list())*0+1:
                mark_line.append(mark_list)

            line_ratio.add("Completeness Ratio 2",Bar_time_x,mark_line,
                           is_label_show = False,is_smooth=True,is_splitline_show = False,
                           is_more_utils = True,line_color = ['Blue'],
                           legend_pos = 'left',legend_orient = 'vertical') #area_opacity=0.0001 #is_fill = True,


            overlap_all_1 = Overlap("Wrokload",width = '100%')
            overlap_all_1.add(bar_task0)
            overlap_all_1.add(bar_Done0) 
            overlap_all_1.add(line_ratio,yaxis_index=1, is_add_yaxis=True)

            names['overlap_all_1' + str(L2)]  = overlap_all_1

        print("Done")

        timeline =  Timeline(timeline_bottom = 0,is_auto_play = False,width= '100%',is_timeline_show = True)  #mark_point = [{'coord': [x[0], y2_t[0]], 'name': 'total'}

        for L2 in range(len(df_FailureType_updated0.TaskownerUserName.to_list())): # 這裏是大L

            timeline.add( names['overlap_all_1' + str(L2)],df_FailureType_updated0.TaskownerUserName.to_list()[L2])

        return timeline


    def datagraph1(self,df_Ratio2,df_Ratio,All_result_combine_updated,df_FailureType_updated0,FailureType_list,numerator_columns_list,names,label_color,denomonator_columns_list,df_Ratio_1,df_Ratio_2,length_date):

        Max = All_result_combine_updated.iloc[:,3:].values.max()## 取所有天的最大值作为y轴的最大值
        configure(global_theme='darksalmon')   
        Bar_X =df_FailureType_updated0.TaskownerUserName.to_list()
        for m in range(length_date-30, length_date) :

            ## -----------------13:40---------------
            bar_Done = Bar(title = Bar_Y_All_Values0.columns[m].strftime('%m-%d'),subtitle = 'Workload',
            title_pos = 'center',height = 360,width='100%') 

            for j2 in range(len(FailureType_list)):
                for j3 in range(len(numerator_columns_list)):
                    if  names['legened_name' + str(j2) ] == numerator_columns_list[j3]:
                        #print(numerator_columns_list[j3])
                        bar_Done.add(names['legened_name' + str(j2) ],Bar_X,names['Bar_Y' + str(j2) + str(m)],is_splitline_show = False,
                                              is_stack=True,is_label_show=False,xaxis_rotate = 25,xaxis_margin = 5,
                                              legend_pos = '73%',is_more_utils = True,yaxis_max =Max,
                                              is_toolbox_show=True,bar_category_gap = '35%',label_color = label_color,yaxis_label_textsize=10,
                                              is_datazoom_extra_show=True,datazoom_extra_type="slider",datazoom_extra_range=[0, 10])
                        #,legend_orient = 'vertical'
                else :
                    pass



            bar_task = Bar(title = Bar_Y_All_Values0.columns[m].strftime('%m-%d'),subtitle = 'Workload',
                title_pos = 'center',height = 360,width='100%') 

            for j2 in range(len(FailureType_list)):
                for j3 in range(len(denomonator_columns_list)):
                    if  names['legened_name' + str(j2) ] == denomonator_columns_list[j3]:
                        #print(denomonator_columns_list[j3])
                        bar_task.add(names['legened_name' + str(j2) ],Bar_X,names['Bar_Y' + str(j2) + str(m)],is_splitline_show = False,
                                              is_stack=True,is_label_show=False,xaxis_rotate = 25,xaxis_margin = 5,legend_orient = 'vertical',
                                              legend_pos = '73%',is_more_utils = True,yaxis_max =Max,
                                              is_toolbox_show=True,bar_category_gap = '35%',label_color = label_color,yaxis_label_textsize=10,
                                              is_datazoom_extra_show=True,datazoom_extra_type="slider",datazoom_extra_range=[0, 10])
                        #legend_top = 'bottom',

                else :
                    pass

            line_ratio_2 =Line('',background_color = 'white',title_text_size = 20,title_pos = 'center')

            line_ratio_2.add("Completeness Ratio 1",Bar_X,df_Ratio[Bar_Y_All_Values0.columns[m]].to_list()
                       ,is_more_utils = True,is_splitline_show = False,is_label_show = False,is_smooth=True,mark_line=['average'],
                       line_color = [' black'],legend_pos = 'left',line_type = 'dotted',line_width  = '2') #legend_orient = 'vertical',

            line_ratio_2.add("Completeness Ratio 2",Bar_X,df_Ratio2[Bar_Y_All_Values0.columns[m]].to_list(),
                           is_label_show = False,is_smooth=True,mark_line=['average'],is_splitline_show = False,
                           is_fill = True,area_opacity=0.1,is_more_utils = True,line_color = ['red'],
                           legend_pos = '73%',area_color='#000') #area_opacity=0.0001 #is_fill = True,  ,legend_orient = 'vertical'

            mark_line = []
            for mark_list in np.array(df_Ratio2[Bar_Y_All_Values0.columns[m]].to_list())*0+1:
                mark_line.append(mark_list)

            line_ratio_2.add("Completeness Ratio 2",Bar_X,mark_line,
                           is_label_show = False,is_smooth=True,is_splitline_show = False,
                           is_more_utils = True,line_color = ['Blue'],
                           legend_pos = '73%') #area_opacity=0.0001 #is_fill = True,  #,legend_orient = 'vertical'


            overlap_all = Overlap("Keynes",width = '100%')
            overlap_all.add(bar_task)
            overlap_all.add(bar_Done) 
            overlap_all.add(line_ratio_2,yaxis_index=1, is_add_yaxis=True)


            names['overlap_all' + str(m)]  = overlap_all
            #names['overlap_all' + str(m)].render("Test%s.html"%m)
        print("Done")

        timeline_two =  Timeline(timeline_bottom = 0,is_auto_play = False,width= '100%',is_timeline_show = True)  #mark_point = [{'coord': [x[0], y2_t[0]], 'name': 'total'}

        for k3 in range(length_date-30, length_date) :

            timeline_two.add( names['overlap_all' + str(k3)],Bar_Y_All_Values0.columns[k3].strftime('%m-%d'))


        return timeline_two



    def finalgraph(self,timeline,timeline_two):
        page= Page()
        page.add(timeline_two)
        page.add(timeline)
        page.render(r'C:\Users\Mma4\Desktop\DanalysisProcess\Price_Report.html')


# In[3]:


if __name__ == '__main__':
    
    process_report = price_ratio()
    
    process_report.processor()
    

