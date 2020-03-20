#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!/usr/bin/env python
# coding: utf-8

##====================================import

import sys
import os
import numpy as np
import matplotlib
import pandas as pd
import time as tm
import calendar
import datetime as dt
from pandas import DataFrame
import pyecharts
from pyecharts import Bar
from pyecharts import Line
from pyecharts import Grid 
import random
from pandas import DataFrame,Series
from pyecharts import configure
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from pyecharts import Page,Overlap
from pyecharts import Line, Pie, Kline, Radar,Timeline
from datetime import date
import multiprocessing
from time import sleep
import win32com.client as win32
import pyodbc
from tqdm import tqdm_notebook
from tqdm import tqdm

configure(global_theme='darksalmon')

pd.set_option('display.max_columns', 500)

sys.path.append(os.path.abspath(r"C:\Users\Mma4\Desktop\FailuresReport"))

from Toolbox import time_value
from Price_Failure_Model import Pre_Failure

##=============================================raw file

df_raw = pd.read_csv(r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\P&D_failure\denominator_inscope.csv')

df_raw2 = pd.read_csv(r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\P&D_failure\denominator_outofscope.csv')

##=============================================add header for df_raw

header_string = 'FileId,DeliveryId,InvestmentId,DataUnit,ZoneId,ValidationCodeId,ActionType,ActionUserID,DeliveryId,FailureTaskGeneratedTime,TaskDoneTime,Taskowner,TaskownerUserName,FileUserID,ProcessTime,FailureType,workday'
header_list = header_string.split(sep = ',')

try:
    df_raw.columns = header_list
except:
    pass



#dataset_Scope = pd.read_csv(r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\P&D_failure\denominator_inscope.csv')
#dataset_Out_Scope = pd.read_csv(r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\P&D_failure\denominator_outofscope.csv')

Holiday = pd.read_excel(r'C:\Users\Mma4\Desktop\FailuresReport\2019 Market Holiday List-Yearly QA Full list.xlsx')
CountryId =  pd.read_csv(r'C:\Users\Mma4\Desktop\FailuresReport\performanceId and CountryId.csv')

Pre_value = Pre_Failure(dataset_Scope = df_raw,dataset_Out_Scope= df_raw2,Holiday = Holiday, CountryId = CountryId)


##========================================define

@time_value

class bar_graph:
    
    def __init__(self,df_raw,df_raw2,freqency):
        
        self.df = df_raw
        self.df2 = df_raw2[df_raw2.loc[:,'FailureGenerationType'] == 'outofscope'].copy()
        self.freqency = freqency


    def graphing(self):
        
        df = self.df
        df2 = self.df2
        # df3 = self.df3
        frequency = self.freqency

        if frequency == 'daily':
            dateSearch = pd.to_datetime(df_raw.FailureTaskGeneratedTime.max()) 
            #datetime.now()

        elif frequency == 'weekly':
            dateSearch = pd.to_datetime(df_raw.FailureTaskGeneratedTime.max()) - timedelta(weeks=1)
            #datetime.now() - timedelta(weeks=1)

        elif frequency == 'monthly':
            dateSearch = pd.to_datetime(df_raw.FailureTaskGeneratedTime.max()) - relativedelta(months=1)
            #datetime.now() - relativedelta(months=1)

        elif frequency == 'quarterly':
            dateSearch = pd.to_datetime(df_raw.FailureTaskGeneratedTime.max()) - relativedelta(months=3)
            #datetime.now() - relativedelta(months=3)

        df.loc[:, 'FailureTaskGeneratedTime'] = pd.to_datetime(df.loc[:, 'FailureTaskGeneratedTime']).copy()
        df2.loc[:, 'FailureTaskGeneratedTime'] = pd.to_datetime(df2.loc[:, 'FailureTaskGeneratedTime']).copy()

        df.loc[:, 'FailureTaskGeneratedDate'] = df.loc[:, 'FailureTaskGeneratedTime'].map(lambda x: x.date()).copy()
        df2.loc[:, 'FailureTaskGeneratedDate'] = df2.loc[:, 'FailureTaskGeneratedTime'].map(lambda x: x.date()).copy()

        if frequency == 'daily':
            df = df[df.loc[:, 'FailureTaskGeneratedDate'] == dateSearch.date()].copy()
            df2 = df2[df2.loc[:, 'FailureTaskGeneratedDate'] == dateSearch.date()].copy()

        else:
            df = df[(dateSearch.date() <= df.loc[:, 'FailureTaskGeneratedDate']) & (df.loc[:, 'FailureTaskGeneratedDate'] <= datetime.now().date())].copy()
            df2 = df2[(dateSearch.date() <= df2.loc[:, 'FailureTaskGeneratedDate']) & (df2.loc[:, 'FailureTaskGeneratedDate'] <= datetime.now().date())].copy()

        # -----------------------------count weekend to SZ

        df_copy = df.copy()
        df2_copy = df2.copy()

        weekend_inscope = df_copy['InvestmentId'][df_copy.loc[:, 'workday'] == 'weekend'].count()
        weekend_outofscope = df2_copy['InvestmentId'][df2_copy.loc[:, 'workday'] == 'weekend'].count()

        df = df[df.loc[:, 'workday'] == 'weekday']
        df2 = df2[df2.loc[:, 'workday'] == 'weekday']

        # ---------------------------------

        df_time_list = []
        df_time_list2 = []
        time_list_name = []

        # You can set your time here:

        if tm.localtime().tm_isdst == 1:
            time_set = datetime.now().strftime("%Y/%m/%d 19/30/00")
            print("Now is Summer time")
        else:
            time_set = datetime.now().strftime("%Y/%m/%d 18/30/00")
            print("Now is Winter time")

        # --------------------------

        time_set = dt.datetime.strptime(time_set, "%Y/%m/%d %H/%M/%S")

        for i in range(24):
            df_time_list.append(time_set.strftime("%I:%M%p"))
            df_time_list2.append(time_set.strftime("df2_%I_%M%p"))
            time_list_name.append(time_set.strftime("%H:%M"))
            time_set = time_set + timedelta(hours=1)

        df.loc[:,'FailureTaskGeneratedTime'] = pd.to_datetime(df.loc[:,'FailureTaskGeneratedTime']).copy()
        df.loc[:,'FailureTaskGeneratedTime'].dropna(inplace=True)
        df.loc[:,'FailureTaskGeneratedTime_time'] = df.loc[:,'FailureTaskGeneratedTime'].apply(lambda x: x.strftime("%d:%H:%M:%S")).copy()
        date_series = df.groupby('FailureTaskGeneratedTime_time')['InvestmentId'].count()

        df2.loc[:,'FailureTaskGeneratedTime'] = pd.to_datetime(df2.loc[:,'FailureTaskGeneratedTime']).copy()
        df2.loc[:,'FailureTaskGeneratedTime'].dropna(inplace=True)
        df2.loc[:,'FailureTaskGeneratedTime_time'] = df2.loc[:,'FailureTaskGeneratedTime'].apply(lambda x: x.strftime("%d:%H:%M:%S")).copy()
        date_series2 = df2.groupby('FailureTaskGeneratedTime_time')['InvestmentId'].count()

        timezone_list = list(date_series.index)
        timezone_list = [dt.datetime.strptime(x, "%d:%H:%M:%S") for x in timezone_list]
        timez_list = [x.strftime("%H:%M") for x in timezone_list]
        day_list = [x.strftime("%d") for x in timezone_list]
        day_num = len(set(day_list))

        timezone_list2 = list(date_series2.index)
        timezone_list2 = [dt.datetime.strptime(x, "%d:%H:%M:%S") for x in timezone_list2]
        timez_list2 = [x.strftime("%H:%M") for x in timezone_list2]
        day_list2 = [x.strftime("%d") for x in timezone_list2]
        day_num2 = len(set(day_list2))

        time_list = []

        for i in range(len(timez_list)):
            time_list.append(dt.time(int(timez_list[i].split(':')[0]), int(timez_list[i].split(':')[1])))

        time_list2 = []

        for i in range(len(timez_list2)):
            time_list2.append(dt.time(int(timez_list2[i].split(':')[0]), int(timez_list2[i].split(':')[1])))

        time_list = np.array(time_list)
        date_series.index = time_list
        date_frame = date_series.to_frame()
        date_frame = date_frame.reset_index()

        time_list2 = np.array(time_list2)
        date_series2.index = time_list2
        date_frame2 = date_series2.to_frame()
        date_frame2 = date_frame2.reset_index()

        average_list = []
        average_list2 = []

        # ---------------------------------------------making & count dataframe by date

        if len(df_time_list) == len(time_list_name):
            for i in range(0, len(df_time_list)):

                if i + 1 > len(df_time_list) - 1:
                    globals()[df_time_list[i]] = date_frame[
                        (dt.time(int(time_list_name[i].split(':')[0]), 30) <= date_frame['index']) & (
                                    date_frame['index'] < dt.time(int(time_list_name[0].split(':')[0]), 30))]
                    globals()[df_time_list2[i]] = date_frame2[
                        (dt.time(int(time_list_name[i].split(':')[0]), 30) <= date_frame2['index']) & (
                                    date_frame2['index'] < dt.time(int(time_list_name[0].split(':')[0]), 30))]

                elif i == 5:
                    globals()[df_time_list[i]] = date_frame[
                        (dt.time(int(time_list_name[i].split(':')[0]), 30) <= date_frame['index']) | (
                                    date_frame['index'] < dt.time(int(time_list_name[i + 1].split(':')[0]), 30))]
                    globals()[df_time_list2[i]] = date_frame2[
                        (dt.time(int(time_list_name[i].split(':')[0]), 30) <= date_frame2['index']) | (
                                    date_frame2['index'] < dt.time(int(time_list_name[i + 1].split(':')[0]), 30))]

                else:
                    globals()[df_time_list[i]] = date_frame[
                        (dt.time(int(time_list_name[i].split(':')[0]), 30) <= date_frame['index']) & (
                                    date_frame['index'] < dt.time(int(time_list_name[i + 1].split(':')[0]), 30))]
                    globals()[df_time_list2[i]] = date_frame2[
                        (dt.time(int(time_list_name[i].split(':')[0]), 30) <= date_frame2['index']) & (
                                    date_frame2['index'] < dt.time(int(time_list_name[i + 1].split(':')[0]), 30))]

                # ---------------------------------------------make the cake to "average_list"

                globals()[df_time_list[i]] = globals()[df_time_list[i]]['InvestmentId'].sum()
                globals()[df_time_list2[i]] = globals()[df_time_list2[i]]['InvestmentId'].sum()

                average_list.append(globals()[df_time_list[i]])
                average_list2.append(globals()[df_time_list2[i]])

        average_array = np.array(average_list)
        average_array[np.isnan(average_array)] = 0
        average_list_inscope = [int(x) for x in list(average_array)]

        average_array2 = np.array(average_list2)
        average_array2[np.isnan(average_array2)] = 0
        average_list_outofscope = [int(x) for x in list(average_array2)]

        average_list_inscope[0] = average_list_inscope[0] + weekend_inscope
        average_list_outofscope[0] = average_list_outofscope[0] + weekend_outofscope

        try:
            average_inscope = list(np.array(average_list_inscope) // day_num)
            average_outofscope = list(np.array(average_list_outofscope) // day_num)
        except:
            pass

        #------------------------------------------cut the cake for sz, mardrid and mumbai

        sz_average_list_inscope = average_list_inscope.copy()
        sz_average_list_inscope[int(len(df_time_list) / 3):] = [0] * (len(df_time_list) - int(len(df_time_list) / 3))
        mardrid_average_list_inscope = average_list_inscope.copy()
        mardrid_average_list_inscope[:int(len(df_time_list) / 3)] = [0] * (int(len(df_time_list) / 3))
        mardrid_average_list_inscope[int(len(df_time_list) * 2 / 3):] = [0] * (int(len(df_time_list) / 3))
        mumbai_average_list_inscope = average_list_inscope.copy()
        mumbai_average_list_inscope[:int(len(df_time_list) * 2 / 3)] = [0] * (len(df_time_list) - int(len(df_time_list) / 3))

        sz_average_list_outofscope = average_list_outofscope.copy()
        sz_average_list_outofscope[int(len(df_time_list) / 3):] = [0] * (len(df_time_list) - int(len(df_time_list) / 3))
        mardrid_average_list_outofscope = average_list_outofscope.copy()
        mardrid_average_list_outofscope[:int(len(df_time_list) / 3)] = [0] * (int(len(df_time_list) / 3))
        mardrid_average_list_outofscope[int(len(df_time_list) * 2 / 3):] = [0] * (int(len(df_time_list) / 3))
        mumbai_average_list_outofscope = average_list_outofscope.copy()
        mumbai_average_list_outofscope[:int(len(df_time_list) * 2 / 3)] = [0] * (len(df_time_list) - int(len(df_time_list) / 3))


        if len(np.array(average_list_inscope)) == len(np.array(average_list_outofscope)):
            total_list = list(np.array(average_list_inscope) + np.array(average_list_outofscope))
            
        if len(Pre_value)>len(np.array(average_list_inscope)):
            pre_total_list = Pre_value[len(Pre_value)-len(np.array(average_list_inscope)):].tolist()
                                                          
        if len(Pre_value)==len(np.array(average_list_inscope)):
            pre_total_list = Pre_value.tolist()
            
                                                          
        # ------------------------------------------cut the cake for sz, mardrid and mumbai second graph

        bar1 = Bar(title = 'Failure Total (%s) from %s to %s'%(frequency,dateSearch.strftime('%Y-%m-%d'),datetime.now().strftime('%Y-%m-%d')))

        bar1.add("%s"%'SZ', df_time_list,sz_average_list_inscope, is_stack=True,is_label_show=False,is_label_emphasis = True,legend_pos = "88%",legend_orient = 'vertical')
        bar1.add("%s"%'outofscope', df_time_list,sz_average_list_outofscope, is_stack=True,is_label_show=False,is_label_emphasis = True,legend_pos = "88%",legend_orient = 'vertical')

        bar2 = Bar()
        bar2.add("%s"%'Madrid', df_time_list,mardrid_average_list_inscope, is_stack=True,is_label_show=False,is_label_emphasis = True)
        bar2.add("%s"%'outofscope', df_time_list,mardrid_average_list_outofscope, is_stack=True,is_label_show=False,is_label_emphasis = True)

        bar3 = Bar()
        bar3.add("%s"%'Mumbai', df_time_list,mumbai_average_list_inscope, is_stack=True,is_label_show=False,is_label_emphasis = True)
        bar3.add("%s"%'outofscope', df_time_list,mumbai_average_list_outofscope, is_stack=True,is_label_show=False,is_label_emphasis = True)

        line =Line('failure_line',background_color = 'white',title_text_size = 20,width = '100%')
        line.add("Actual",df_time_list,total_list)
        line.add("Prediction",df_time_list,pre_total_list,is_more_utils = True,is_splitline_show = False,
               is_label_show = False,is_smooth=False,line_color = [' red'],
               legend_pos = 'left',legend_orient = 'vertical',line_type = 'dotted',line_width  = '2')

        overlap = Overlap(width='100%',height=360)
        overlap.add(bar1)
        overlap.add(bar2)
        overlap.add(bar3)
        overlap.add(line)

        # ------------------------------------------cut the cake for sz, mardrid and mumbai second graph

        sz_avg_list_inscope = average_inscope.copy()
        sz_avg_list_inscope[int(len(df_time_list) / 3):] = [0] * (len(df_time_list) - int(len(df_time_list) / 3))
        mardrid_avg_list_inscope = average_inscope.copy()
        mardrid_avg_list_inscope[:int(len(df_time_list) / 3)] = [0] * (int(len(df_time_list) / 3))
        mardrid_avg_list_inscope[int(len(df_time_list) * 2 / 3):] = [0] * (int(len(df_time_list) / 3))
        mumbai_avg_list_inscope = average_inscope.copy()
        mumbai_avg_list_inscope[:int(len(df_time_list) * 2 / 3)] = [0] * (len(df_time_list) - int(len(df_time_list) / 3))

        sz_avg_list_outofscope = average_outofscope.copy()
        sz_avg_list_outofscope[int(len(df_time_list) / 3):] = [0] * (len(df_time_list) - int(len(df_time_list) / 3))
        mardrid_avg_list_outofscope = average_outofscope.copy()
        mardrid_avg_list_outofscope[:int(len(df_time_list) / 3)] = [0] * (int(len(df_time_list) / 3))
        mardrid_avg_list_outofscope[int(len(df_time_list) * 2 / 3):] = [0] * (int(len(df_time_list) / 3))
        mumbai_avg_list_outofscope = average_outofscope.copy()
        mumbai_avg_list_outofscope[:int(len(df_time_list) * 2 / 3)] = [0] * (len(df_time_list) - int(len(df_time_list) / 3))


        if len(np.array(average_inscope)) == len(np.array(average_outofscope)):
            avg_num = list(np.array(average_inscope) + np.array(average_outofscope))
            


        # ------------------------------------------cut the cake for sz, mardrid and mumbai second graph

        bar1 = Bar(title = 'Failure Average (%s) from %s to %s'%(frequency,dateSearch.strftime('%Y-%m-%d'),datetime.now().strftime('%Y-%m-%d')))

        bar1.add("%s"%'SZ', df_time_list,sz_avg_list_inscope, is_stack=True,is_label_show=False,is_label_emphasis = True,legend_pos = "88%",legend_orient = 'vertical')
        bar1.add("%s"%'outofscope', df_time_list,sz_avg_list_outofscope, is_stack=True,is_label_show=False,is_label_emphasis = True,legend_pos = "88%",legend_orient = 'vertical')

        bar2 = Bar()
        bar2.add("%s"%'Madrid', df_time_list,mardrid_avg_list_inscope, is_stack=True,is_label_show=False,is_label_emphasis = True)
        bar2.add("%s"%'outofscope', df_time_list,mardrid_avg_list_outofscope, is_stack=True,is_label_show=False,is_label_emphasis = True)

        bar3 = Bar()
        bar3.add("%s"%'Mumbai', df_time_list,mumbai_avg_list_inscope, is_stack=True,is_label_show=False,is_label_emphasis = True)
        bar3.add("%s"%'outofscope', df_time_list,mumbai_avg_list_outofscope, is_stack=True,is_label_show=False,is_label_emphasis = True)

        line =Line('failure_line',background_color = 'white',title_text_size = 20,width = '100%') # total
        line.add("Actual",df_time_list,avg_num)

        overlap2 = Overlap(width='100%',height=360)
        overlap2.add(bar1)
        overlap2.add(bar2)
        overlap2.add(bar3)
        overlap2.add(line)


        return overlap,overlap2,frequency

##============================running
if __name__ == '__main__':

    timeline = Timeline(is_auto_play=False, timeline_bottom=0,width = '100%')
    timeline2 = Timeline(is_auto_play=False, timeline_bottom=0, width='100%')

    frequency_list = ['daily','weekly','monthly','quarterly']

    for i in frequency_list:

        frequency = i

        print("is doing " + i)

        overlap,overlap2,frequency = bar_graph(df_raw,df_raw2,frequency).graphing()

        timeline.add(overlap, frequency)
        timeline2.add(overlap2, frequency)

page = Page()
page.add(timeline)
page.add(timeline2)
page.render(r'C:\Users\Mma4\Desktop\FailuresReport\Report.html')
print('Task Done')


# In[7]:


# #Old Version============================================================================================================

# # coding: utf-8

# # In[1]:


# #!/usr/bin/env python
# # coding: utf-8

# ##====================================import


# import numpy as np
# import matplotlib
# import pandas as pd
# import time as tm
# import calendar
# import datetime as dt
# from pandas import DataFrame
# import pyecharts
# from pyecharts import Bar
# from pyecharts import Line
# from pyecharts import Grid 
# import random
# from pandas import DataFrame,Series
# from pyecharts import configure
# from datetime import datetime,timedelta
# from dateutil.relativedelta import relativedelta
# from pyecharts import Page,Overlap
# from pyecharts import Line, Pie, Kline, Radar,Timeline

# from datetime import date
# import pretty_errors
# import sys

# import multiprocessing
# from time import sleep

# import win32com.client as win32

# import pyodbc


# from tqdm import tqdm_notebook
# from tqdm import tqdm

# configure(global_theme='darksalmon')

# pd.set_option('display.max_columns', 500)


# # In[2]:


# class bar_graph():
    
#     def __init__(self,frequency,df_raw,df2_raw):
        
#         self.frequency = frequency
#         self.df_raw = df_raw
#         self.df2_raw = df2_raw


#     def data_processor(self):
        
#         df = self.df_raw
#         df2 = self.df2_raw
#         frequency = self.frequency

#         if frequency == 'daily':
#             dateSearch = datetime.now()

#         elif frequency == 'weekly':
#             dateSearch = datetime.now() - timedelta(weeks=1)

#         elif frequency == 'monthly':
#             dateSearch = datetime.now() - relativedelta(months=1)

#         elif frequency == 'quarterly':
#             dateSearch = datetime.now() - relativedelta(months=3)

#         df.loc[:, 'FailureTaskGeneratedTime'] = pd.to_datetime(df.loc[:, 'FailureTaskGeneratedTime']).copy()
#         df2.loc[:, 'FailureTaskGeneratedTime'] = pd.to_datetime(df2.loc[:, 'FailureTaskGeneratedTime']).copy()

#         df.loc[:, 'FailureTaskGeneratedDate'] = df.loc[:, 'FailureTaskGeneratedTime'].map(lambda x: x.date()).copy()
#         df2.loc[:, 'FailureTaskGeneratedDate'] = df2.loc[:, 'FailureTaskGeneratedTime'].map(lambda x: x.date()).copy()

#         if frequency == 'daily':
#             df = df[df.loc[:, 'FailureTaskGeneratedDate'] == dateSearch.date()].copy()
#             df2 = df2[df2.loc[:, 'FailureTaskGeneratedDate'] == dateSearch.date()].copy()

#         else:
#             df = df[(dateSearch.date() <= df.loc[:, 'FailureTaskGeneratedDate']) & (df.loc[:, 'FailureTaskGeneratedDate'] <= datetime.now().date())].copy()
#             df2 = df2[(dateSearch.date() <= df2.loc[:, 'FailureTaskGeneratedDate']) & (df2.loc[:, 'FailureTaskGeneratedDate'] <= datetime.now().date())].copy()

#         # -----------------------------count weekend to SZ

#         df_copy = df.copy()
#         df2_copy = df2.copy()

#         weekend_inscope = df_copy['InvestmentId'][df_copy.loc[:, 'workday'] == 'weekend'].count()
#         weekend_outofscope = df2_copy['InvestmentId'][df2_copy.loc[:, 'workday'] == 'weekend'].count()

#         df = df[df.loc[:, 'workday'] == 'weekday']
#         df2 = df2[df2.loc[:, 'workday'] == 'weekday']

#         # ---------------------------------

#         df_time_list = []
#         df_time_list2 = []
#         time_list_name = []

#         # You can set your time here:

#         if tm.localtime().tm_isdst == 1:
#             time_set = datetime.now().strftime("%Y/%m/%d 19/30/00")
#             print("Now is Summer time")
#         else:
#             time_set = datetime.now().strftime("%Y/%m/%d 18/30/00")
#             print("Now is Winter time")

#         # --------------------------

#         time_set = dt.datetime.strptime(time_set, "%Y/%m/%d %H/%M/%S")

#         for i in range(24):
#             df_time_list.append(time_set.strftime("%I:%M%p"))
#             df_time_list2.append(time_set.strftime("df2_%I_%M%p"))
#             time_list_name.append(time_set.strftime("%H:%M"))
#             time_set = time_set + timedelta(hours=1)

#         df.loc[:,'FailureTaskGeneratedTime'] = pd.to_datetime(df.loc[:,'FailureTaskGeneratedTime']).copy()
#         df.loc[:,'FailureTaskGeneratedTime'].dropna(inplace=True)
#         df.loc[:,'FailureTaskGeneratedTime_time'] = df.loc[:,'FailureTaskGeneratedTime'].apply(lambda x: x.strftime("%d:%H:%M:%S")).copy()
#         date_series = df.groupby('FailureTaskGeneratedTime_time')['InvestmentId'].count()

#         df2.loc[:,'FailureTaskGeneratedTime'] = pd.to_datetime(df2.loc[:,'FailureTaskGeneratedTime']).copy()
#         df2.loc[:,'FailureTaskGeneratedTime'].dropna(inplace=True)
#         df2.loc[:,'FailureTaskGeneratedTime_time'] = df2.loc[:,'FailureTaskGeneratedTime'].apply(lambda x: x.strftime("%d:%H:%M:%S")).copy()
#         date_series2 = df2.groupby('FailureTaskGeneratedTime_time')['InvestmentId'].count()

#         timezone_list = list(date_series.index)
#         timezone_list = [dt.datetime.strptime(x, "%d:%H:%M:%S") for x in timezone_list]
#         timez_list = [x.strftime("%H:%M") for x in timezone_list]
#         day_list = [x.strftime("%d") for x in timezone_list]
#         day_num = len(set(day_list))

#         timezone_list2 = list(date_series2.index)
#         timezone_list2 = [dt.datetime.strptime(x, "%d:%H:%M:%S") for x in timezone_list2]
#         timez_list2 = [x.strftime("%H:%M") for x in timezone_list2]
#         day_list2 = [x.strftime("%d") for x in timezone_list2]
#         day_num2 = len(set(day_list2))

#         time_list = []

#         for i in range(len(timez_list)):
#             time_list.append(dt.time(int(timez_list[i].split(':')[0]), int(timez_list[i].split(':')[1])))

#         time_list2 = []

#         for i in range(len(timez_list2)):
#             time_list2.append(dt.time(int(timez_list2[i].split(':')[0]), int(timez_list2[i].split(':')[1])))

#         time_list = np.array(time_list)
#         date_series.index = time_list
#         date_frame = date_series.to_frame()
#         date_frame = date_frame.reset_index()

#         time_list2 = np.array(time_list2)
#         date_series2.index = time_list2
#         date_frame2 = date_series2.to_frame()
#         date_frame2 = date_frame2.reset_index()

#         average_list = []
#         average_list2 = []

#         # ---------------------------------------------making & count dataframe by date

#         if len(df_time_list) == len(time_list_name):
#             for i in range(0, len(df_time_list)):

#                 if i + 1 > len(df_time_list) - 1:
#                     globals()[df_time_list[i]] = date_frame[
#                         (dt.time(int(time_list_name[i].split(':')[0]), 30) <= date_frame['index']) & (
#                                     date_frame['index'] < dt.time(int(time_list_name[0].split(':')[0]), 30))]
#                     globals()[df_time_list2[i]] = date_frame2[
#                         (dt.time(int(time_list_name[i].split(':')[0]), 30) <= date_frame2['index']) & (
#                                     date_frame2['index'] < dt.time(int(time_list_name[0].split(':')[0]), 30))]

#                 elif i == 5:
#                     globals()[df_time_list[i]] = date_frame[
#                         (dt.time(int(time_list_name[i].split(':')[0]), 30) <= date_frame['index']) | (
#                                     date_frame['index'] < dt.time(int(time_list_name[i + 1].split(':')[0]), 30))]
#                     globals()[df_time_list2[i]] = date_frame2[
#                         (dt.time(int(time_list_name[i].split(':')[0]), 30) <= date_frame2['index']) | (
#                                     date_frame2['index'] < dt.time(int(time_list_name[i + 1].split(':')[0]), 30))]

#                 else:
#                     globals()[df_time_list[i]] = date_frame[
#                         (dt.time(int(time_list_name[i].split(':')[0]), 30) <= date_frame['index']) & (
#                                     date_frame['index'] < dt.time(int(time_list_name[i + 1].split(':')[0]), 30))]
#                     globals()[df_time_list2[i]] = date_frame2[
#                         (dt.time(int(time_list_name[i].split(':')[0]), 30) <= date_frame2['index']) & (
#                                     date_frame2['index'] < dt.time(int(time_list_name[i + 1].split(':')[0]), 30))]

#                 # ---------------------------------------------make the cake to "average_list"

#                 globals()[df_time_list[i]] = globals()[df_time_list[i]]['InvestmentId'].sum()
#                 globals()[df_time_list2[i]] = globals()[df_time_list2[i]]['InvestmentId'].sum()

#                 average_list.append(globals()[df_time_list[i]])
#                 average_list2.append(globals()[df_time_list2[i]])

#         average_array = np.array(average_list)
#         average_array[np.isnan(average_array)] = 0
#         average_list_inscope = [int(x) for x in list(average_array)]

#         average_array2 = np.array(average_list2)
#         average_array2[np.isnan(average_array2)] = 0
#         average_list_outofscope = [int(x) for x in list(average_array2)]

#         average_list_inscope[0] = average_list_inscope[0] + weekend_inscope
#         average_list_outofscope[0] = average_list_outofscope[0] + weekend_outofscope

#         try:
#             average_inscope = list(np.array(average_list_inscope) // day_num)
#             average_outofscope = list(np.array(average_list_outofscope) // day_num)
#         except:
#             pass
         
#         self.average_list_inscope = average_list_inscope
#         self.average_list_outofscope = average_list_outofscope
#         self.df_time_list = df_time_list
        
#         self.average_inscope = average_inscope
#         self.average_outofscope = average_inscope
        
#         self.dateSearch = dateSearch
        
        
#     def graphing_total(self):
        
#         average_list_inscope = self.average_list_inscope
        
#         average_list_outofscope = self.average_list_outofscope
        
#         df_time_list =  self.df_time_list

#         #------------------------------------------cut the cake for sz, mardrid and mumbai

#         sz_average_list_inscope = average_list_inscope.copy()
#         sz_average_list_inscope[int(len(df_time_list) / 3):] = [0] * (len(df_time_list) - int(len(df_time_list) / 3))
#         mardrid_average_list_inscope = average_list_inscope.copy()
#         mardrid_average_list_inscope[:int(len(df_time_list) / 3)] = [0] * (int(len(df_time_list) / 3))
#         mardrid_average_list_inscope[int(len(df_time_list) * 2 / 3):] = [0] * (int(len(df_time_list) / 3))
#         mumbai_average_list_inscope = average_list_inscope.copy()
#         mumbai_average_list_inscope[:int(len(df_time_list) * 2 / 3)] = [0] * (len(df_time_list) - int(len(df_time_list) / 3))

#         sz_average_list_outofscope = average_list_outofscope.copy()
#         sz_average_list_outofscope[int(len(df_time_list) / 3):] = [0] * (len(df_time_list) - int(len(df_time_list) / 3))
#         mardrid_average_list_outofscope = average_list_outofscope.copy()
#         mardrid_average_list_outofscope[:int(len(df_time_list) / 3)] = [0] * (int(len(df_time_list) / 3))
#         mardrid_average_list_outofscope[int(len(df_time_list) * 2 / 3):] = [0] * (int(len(df_time_list) / 3))
#         mumbai_average_list_outofscope = average_list_outofscope.copy()
#         mumbai_average_list_outofscope[:int(len(df_time_list) * 2 / 3)] = [0] * (len(df_time_list) - int(len(df_time_list) / 3))


#         if len(np.array(average_list_inscope)) == len(np.array(average_list_outofscope)):
#             total_list = list(np.array(average_list_inscope) + np.array(average_list_outofscope))



#         # ------------------------------------------cut the cake for sz, mardrid and mumbai second graph

#         bar1 = Bar(title = 'Failure Total (%s) from %s to %s'%(self.frequency,self.dateSearch.strftime('%Y-%m-%d'),datetime.now().strftime('%Y-%m-%d')))

#         bar1.add("%s"%'SZ', df_time_list,sz_average_list_inscope, is_stack=True,is_label_show=False,is_label_emphasis = True,legend_pos = "88%",legend_orient = 'vertical')
#         bar1.add("%s"%'outofscope', df_time_list,sz_average_list_outofscope, is_stack=True,is_label_show=False,is_label_emphasis = True,legend_pos = "88%",legend_orient = 'vertical')

#         bar2 = Bar()
#         bar2.add("%s"%'Madrid', df_time_list,mardrid_average_list_inscope, is_stack=True,is_label_show=False,is_label_emphasis = True)
#         bar2.add("%s"%'outofscope', df_time_list,mardrid_average_list_outofscope, is_stack=True,is_label_show=False,is_label_emphasis = True)

#         bar3 = Bar()
#         bar3.add("%s"%'Mumbai', df_time_list,mumbai_average_list_inscope, is_stack=True,is_label_show=False,is_label_emphasis = True)
#         bar3.add("%s"%'outofscope', df_time_list,mumbai_average_list_outofscope, is_stack=True,is_label_show=False,is_label_emphasis = True)

#         line =Line('failure_line',background_color = 'white',title_text_size = 20,width = '100%')
#         line.add("Actual",df_time_list,total_list)

#         overlap = Overlap(width='100%',height=360)
#         overlap.add(bar1)
#         overlap.add(bar2)
#         overlap.add(bar3)
#         overlap.add(line)

#         return overlap

#     # ------------------------------------------cut the cake for sz, mardrid and mumbai second graph
        
#     def graphing_avg(self):
        
#         average_inscope = self.average_inscope
        
#         average_outofscope = self.average_outofscope
        
#         df_time_list =  self.df_time_list

#         sz_avg_list_inscope = average_inscope.copy()
#         sz_avg_list_inscope[int(len(df_time_list) / 3):] = [0] * (len(df_time_list) - int(len(df_time_list) / 3))
#         mardrid_avg_list_inscope = average_inscope.copy()
#         mardrid_avg_list_inscope[:int(len(df_time_list) / 3)] = [0] * (int(len(df_time_list) / 3))
#         mardrid_avg_list_inscope[int(len(df_time_list) * 2 / 3):] = [0] * (int(len(df_time_list) / 3))
#         mumbai_avg_list_inscope = average_inscope.copy()
#         mumbai_avg_list_inscope[:int(len(df_time_list) * 2 / 3)] = [0] * (len(df_time_list) - int(len(df_time_list) / 3))

#         sz_avg_list_outofscope = average_outofscope.copy()
#         sz_avg_list_outofscope[int(len(df_time_list) / 3):] = [0] * (len(df_time_list) - int(len(df_time_list) / 3))
#         mardrid_avg_list_outofscope = average_outofscope.copy()
#         mardrid_avg_list_outofscope[:int(len(df_time_list) / 3)] = [0] * (int(len(df_time_list) / 3))
#         mardrid_avg_list_outofscope[int(len(df_time_list) * 2 / 3):] = [0] * (int(len(df_time_list) / 3))
#         mumbai_avg_list_outofscope = average_outofscope.copy()
#         mumbai_avg_list_outofscope[:int(len(df_time_list) * 2 / 3)] = [0] * (len(df_time_list) - int(len(df_time_list) / 3))


#         if len(np.array(average_inscope)) == len(np.array(average_outofscope)):
#             avg_num = list(np.array(average_inscope) + np.array(average_outofscope))

#         # ------------------------------------------cut the cake for sz, mardrid and mumbai second graph

#         bar1 = Bar(title = 'Failure Average (%s) from %s to %s'%(self.frequency,self.dateSearch.strftime('%Y-%m-%d'),datetime.now().strftime('%Y-%m-%d')))

#         bar1.add("%s"%'SZ', df_time_list,sz_avg_list_inscope, is_stack=True,is_label_show=False,is_label_emphasis = True,legend_pos = "88%",legend_orient = 'vertical')
#         bar1.add("%s"%'outofscope', df_time_list,sz_avg_list_outofscope, is_stack=True,is_label_show=False,is_label_emphasis = True,legend_pos = "88%",legend_orient = 'vertical')

#         bar2 = Bar()
#         bar2.add("%s"%'Madrid', df_time_list,mardrid_avg_list_inscope, is_stack=True,is_label_show=False,is_label_emphasis = True)
#         bar2.add("%s"%'outofscope', df_time_list,mardrid_avg_list_outofscope, is_stack=True,is_label_show=False,is_label_emphasis = True)

#         bar3 = Bar()
#         bar3.add("%s"%'Mumbai', df_time_list,mumbai_avg_list_inscope, is_stack=True,is_label_show=False,is_label_emphasis = True)
#         bar3.add("%s"%'outofscope', df_time_list,mumbai_avg_list_outofscope, is_stack=True,is_label_show=False,is_label_emphasis = True)

#         line =Line('failure_line',background_color = 'white',title_text_size = 20,width = '100%')
#         line.add("Actual",df_time_list,avg_num)

#         overlap2 = Overlap(width='100%',height=360)
#         overlap2.add(bar1)
#         overlap2.add(bar2)
#         overlap2.add(bar3)
#         overlap2.add(line)


#         return overlap2


# # In[3]:


# ##============================running
# if __name__ == '__main__':

#     timeline = Timeline(is_auto_play=False, timeline_bottom=0,width = '100%')
#     timeline2 = Timeline(is_auto_play=False, timeline_bottom=0, width='100%')

#     frequency_list = ['daily','weekly','monthly','quarterly']

#     for i in frequency_list:

#         frequency = i
        
#         df_raw = pd.read_csv(r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\P&D_failure\denominator_inscope.csv')
#         df2_raw = pd.read_csv(r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\P&D_failure\denominator_outofscope.csv')
#         df2_raw = df2_raw[df2_raw.loc[:,'FailureGenerationType'] == 'outofscope'].copy()
        
#         header_string = 'FileId,DeliveryId,InvestmentId,DataUnit,ZoneId,ValidationCodeId,ActionType,ActionUserID,DeliveryId,FailureTaskGeneratedTime,TaskDoneTime,Taskowner,TaskownerUserName,FileUserID,ProcessTime,FailureType,workday'
#         header_list = header_string.split(sep = ',')
        
#         try:
#             df_raw.columns = header_list
#         except:
#             pass

#         print("is doing " + i)
        
#         bar_graphing = bar_graph(frequency,df_raw,df2_raw)
        
#         bar_graphing.data_processor()

#         overlap = bar_graphing.graphing_total()
#         overlap2 = bar_graphing.graphing_avg()

#         timeline.add(overlap, frequency)
#         timeline2.add(overlap2, frequency)

#     timeline.render(path=r'C:\Users\Mma4\Desktop\FailureTotalTimeline.html')
#     timeline2.render(path=r'C:\Users\Mma4\Desktop\FailureAverageTimeline.html')

