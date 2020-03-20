#!/usr/bin/env python
# coding: utf-8

# In[1]:


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

#----------------------------------------------------------分割线-----------------------------------------------------------

from bokeh.io import output_file, show, output_notebook, push_notebook
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, LabelSet  # Dataframe处理，hover组件
from bokeh.layouts import row, column, gridplot  #布局相关部件
from bokeh.models.widgets import Tabs, Panel
from bokeh.palettes import Spectral6  # 导入colormap
from bokeh.transform import linear_cmap
from bokeh.models import LinearAxis, Range1d
from tqdm import tqdm_notebook
from tqdm import tqdm


# In[2]:


def login_sql():
    connecting_string = '''
    Driver={SQL Server Native Client 11.0};
    Server=xxxxxx\xxxxxx;
    Database=;
    Uid=xxxxxx\xxxxxx;
    Pwd=;
    Trusted_Domain=;
    Trusted_Connection=yes;
    MARS_Connection=yes'''
    connection = pyodbc.connect(connecting_string)
    return connection


# In[3]:


def send_mail(t):
    
    suject = "成功啦,第%s次,时间%s" % (t,datetime.now())

    outlook = win32.Dispatch('Outlook.Application')

    mail_item = outlook.CreateItem(0) # 0: olMailItem

    mail_item.Recipients.Add("xxxxxx@xxxxxxx.com")
    mail_item.Recipients.Add("xxxxxx@xxxxxxx.com")
    mail_item.Recipients.Add("xxxxxx@xxxxxxx.com")

    mail_item.Subject = suject

    mail_item.BodyFormat = 2          # 2: Html format
    html2 = '<tr align="center">'
    #html2 = root.replace('<table border="1"', '<table border="1"bordercolor="#66CCFF" >')
    html2 = html2.replace('2019-', '')
    html2 = html2.replace(':00:00', '')
    html2 = html2.replace('.0', '') 
    html2 = html2.replace('<td>0</td>', '<td>---</td>')
    html2 = html2.replace(':00', '')
    html2 = html2.replace('<td>NaN</td>', '<td>---</td>')
    html2 = html2.replace('Accum', 'Missing <br/> data no. <br/>at each hour')  # 
    html2 = html2.replace('Decrease', 'Decreased <br/> missing no. <br/> from last hour') 
    html2 = html2.replace('ExpectedTime', 'US.') 

    mail_item.HTMLBody  = html2
    
    mail_item.Attachments.Add(r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\TNA\Failure_5cats.html')
    mail_item.Attachments.Add(r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\TNA\Failure_Daily.html')
    mail_item.Attachments.Add(r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\TNA\Failure_Page.html')
    mail_item.Attachments.Add(r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\TNA\TNA_Hourly.html')
    mail_item.Attachments.Add(r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\TNA\TNA_Daily.html')
    mail_item.Attachments.Add(r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\TNA\Prediction.html')
    
    mail_item.Send()


# In[4]:


def send_mail_failure(e):
    suject = "报错啦,原因:%s,时间%s" % (e,datetime.now())

    outlook = win32.Dispatch('Outlook.Application')

    mail_item = outlook.CreateItem(0) # 0: olMailItem

    mail_item.Recipients.Add("xxxxxx@xxxxxxx.com")
    mail_item.Recipients.Add("xxxxxx@xxxxxxx.com")
    mail_item.Recipients.Add("xxxxxx@xxxxxxx.com")

    mail_item.Subject = suject

    mail_item.BodyFormat = 2          # 2: Html format
    html2 = '<tr align="center">'
    #html2 = root.replace('<table border="1"', '<table border="1"bordercolor="#66CCFF" >')
    html2 = html2.replace('2019-', '')
    html2 = html2.replace(':00:00', '')
    html2 = html2.replace('.0', '') 
    html2 = html2.replace('<td>0</td>', '<td>---</td>')
    html2 = html2.replace(':00', '')
    html2 = html2.replace('<td>NaN</td>', '<td>---</td>')
    html2 = html2.replace('Accum', 'Missing <br/> data no. <br/>at each hour')  # 
    html2 = html2.replace('Decrease', 'Decreased <br/> missing no. <br/> from last hour') 
    html2 = html2.replace('ExpectedTime', 'US.') 

    mail_item.HTMLBody  = html2
    
    mail_item.Send()


# In[5]:


def time_interval():
    timenow = datetime.now()
    time_nexthour = timenow + relativedelta(hours = 1)
    time_20 = time_nexthour.strftime("%Y/%m/%d %H/20/%S")
    time_20 = dt.datetime.strptime(time_20, "%Y/%m/%d %H/%M/%S")
    time_interval = time_20 - timenow
    return time_interval.seconds - 300


# In[6]:


def run_python():
    print('python_running')
    
    sql11 = '''
    declare @T1 smalldatetime  
    set @T1 = convert(char(100),getdate(),120)  
    --declare @T2 smalldatetime 
    --set @T2=convert(date,case datename(dw,@T1) when 'Saturday' then @T1-1 when 'Sunday' then  @T1-2 else @T1 end,112)



    ;WITH SummaryFile AS
    (select K.InvestmentId,K.EffectiveDate, convert(float,substring(K.DataDetail_2,1,charindex(';',K.DataDetail_2)-1) ) as  TNA, 
    min(K.ActionTime) as FailureGeneratedTime,K.ValidationCodeId,K.CountryId
    from
    (select f.InvestmentId, f.EffectiveDate, f.ActionTime, f.DataDetail, f.ValidationCodeId,ss.CountryId,
    SUBSTRING(DataDetail,charindex(';TNA:',DataDetail)+5,len(DataDetail)-charindex(';TNA:',DataDetail)) as  DataDetail_2
    from LogData_GPMainDB.dbo.PerformanceFailureDataSourceTracking f
    join SecurityData.dbo.InvestmentPerformanceId  as ip with (nolock)  on f.InvestmentId=ip.PerformanceId10Char
    join SecurityData.dbo.SecuritySearch as ss with(nolock) on ss.SecId=ip.InvestmentId 
    where f.DataUnit = 701
    and f.ActionTime > convert(char(100),dateadd(hour,-1,@T1),120)  --调时间区间
    and f.ActionTime <= @T1
    and charindex(';TNA:',DataDetail)!=0
    and f.ValidationCodeId !=0
    --and f.InvestmentId = '0P00000GTE'
    and datename(dw,ActionTime)!='Saturday'  --排除周末
    and datename(dw,ActionTime)!='Sunday'
    )K
    group by K.InvestmentId,K.EffectiveDate,convert(float,substring(K.DataDetail_2,1,charindex(';',K.DataDetail_2)-1) ),K.ValidationCodeId,K.CountryId
    )


    select J.InvestmentId, J.EffectiveDate, J.ValidationCodeId, J.ActionType_Real, J.ActionTime_Real, 
    CONVERT(varchar,ActionTime_Real,23) as Date, CONVERT(varchar,ActionTime_Real,24) as Hour, 
    J.TNA, J.FailureGeneratedTime,J.CountryId,
    case 
    when (J.ActionType_Real !=1 and J.ActionTime_Real>DATEADD(HOUR,1,J.FailureGeneratedTime)) then '0'  
    when (J.ActionType_Real !=1 and J.ActionTime_Real<=DATEADD(HOUR,1,J.FailureGeneratedTime)) then '1'
    else '0' end   as  ActionStatus_OneHour,
    case
    when (J.ActionType_Real !=1 and J.ActionTime_Real>DATEADD(HOUR,24,J.FailureGeneratedTime)) then '0'  
    when (J.ActionType_Real !=1 and J.ActionTime_Real<=DATEADD(HOUR,24,J.FailureGeneratedTime)) then '1'  
    else '0' end   as  ActionStatus_24Hour,
    case
    when (J.ActionType_Real !=1 and DATEDIFF(day,J.ActionTime_Real,J.FailureGeneratedTime)=0 and (datepart(hour,J.ActionTime_Real)-datepart(hour,J.FailureGeneratedTime))=0) then 1  
    else 0 end   as  Complete_OneHour,
    case
    when (J.ActionType_Real !=1 and DATEDIFF(day,J.ActionTime_Real,J.FailureGeneratedTime)=0 ) then 1  
    else 0 end   as  Complete_24Hour,
    case 
    when DATEDIFF(DAY,J.EffectiveDate, J.ActionTime_Real) <=7  then 'OngoingFailure' 
    else 'HistoricalFailure' end as FailureType,
    case 
    when J.ActionType_Real in (3,7,8)  then 1
    else 0 end as Operation,
    case 
    when (CONVERT(varchar,J.FailureGeneratedTime,24)>='04:00:00' and CONVERT(varchar,J.FailureGeneratedTime,24)<'12:00:00')  then 1
    when (CONVERT(varchar,J.FailureGeneratedTime,24)>='12:00:00' and CONVERT(varchar,J.FailureGeneratedTime,24)<'20:00:00')  then 2
    else 3 end as TimeZone,
    case 
    when DATEDIFF(hour,J.FailureGeneratedTime,convert(char(100),getdate(),120))<1 then 1
    when (DATEDIFF(hour,J.FailureGeneratedTime,convert(char(100),getdate(),120))>=1 and DATEDIFF(hour,J.FailureGeneratedTime,convert(char(100),getdate(),120))<24) then 2
    when (DATEDIFF(hour,J.FailureGeneratedTime,convert(char(100),getdate(),120))>=24 and DATEDIFF(hour,J.FailureGeneratedTime,convert(char(100),getdate(),120))<168) then 3
    when (DATEDIFF(hour,J.FailureGeneratedTime,convert(char(100),getdate(),120))>=168 and DATEDIFF(hour,J.FailureGeneratedTime,convert(char(100),getdate(),120))<720) then 4
    else 5 end as Un_handledFailureCategory
    from (
    select distinct H.DataUnit,G.ValidationCodeId,H.ActionType,H.ActionTime,H.UserId,H.FileId, 
    G.InvestmentId,G.EffectiveDate,G.TNA, G.CountryId, 
    case when H.ActionTime is not null then H.ActionTime else G.FailureGeneratedTime end as ActionTime_Real, 
    G.FailureGeneratedTime,
    case when H.ActionType is not null then H.ActionType  else 1 end as ActionType_Real
    from
    (select f.InvestmentId,f.ActionTime,f.DataUnit,f.EffectiveDate,f.ValidationCodeId,f.ActionType,
    f.UserId,f.FileId,f.DataDetail,ss.CountryId,
    SUBSTRING(f.DataDetail,charindex(';TNA:',f.DataDetail)+5,len(f.DataDetail)-charindex(';TNA:',f.DataDetail))  as  DataDetail_2
    from LogData_GPMainDB.dbo.PerformanceFailureDataSourceTracking f WITH (NOLOCK)
    join SecurityData.dbo.InvestmentPerformanceId  as ip with (nolock)  on f.InvestmentId=ip.PerformanceId10Char
    join SecurityData.dbo.SecuritySearch as ss with(nolock) on ss.SecId=ip.InvestmentId 
    join SupportData_DMWkspaceDB.dbo.InvestmentDataReadiness as idr with (nolock)  on ip.PerformanceId10Char = idr.InvestmentId
    where f.DataUnit = 701
    and charindex(';TNA:',DataDetail)!=0
    and f.ActionTime > convert(char(100),dateadd(hour,-1,@T1),120)  --调时间区间
    and f.ActionTime <= @T1
    --and ActionTime >= '2019-10-04'
    and f.ActionType in (3,7,8)
    and f.ValidationCodeId !=0
    and ss.CountryId = 'LUX'
    --and f.InvestmentId ='0P00000GTE'
    and ss.Status=1 and idr.DataReadiness=9
    and datename(dw,ActionTime)!='Saturday'
    and datename(dw,ActionTime)!='Sunday'
     ) H
    right join SummaryFile   G  on  H.InvestmentId=G.InvestmentId and H.EffectiveDate=G.EffectiveDate and TNA = G.TNA and G.ValidationCodeId=H.ValidationCodeId

    )J
    '''
    new = pd.read_sql(sql11,connection)

    Rawdata= pd.read_csv(r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\TNA\RawData.csv')

    Rawdata = Rawdata.loc[:,['InvestmentId','EffectiveDate', 'ValidationCodeId', 'ActionType_Real','ActionTime_Real', 'Date', 
                      'Hour', 'TNA', 'FailureGeneratedTime','CountryId', 'ActionStatus_OneHour', 'ActionStatus_24Hour',
                      'Complete_OneHour', 'Complete_24Hour', 'FailureType', 'Operation','TimeZone', 'Un_handledFailureCategory']]

    #--------------------------有SQL用这句----------------------

    new.columns=Rawdata.columns


    #--------------------------有SQL用这句----------------------

    df_merge= pd.concat([Rawdata,new],axis=0,sort=False).drop_duplicates()
    
    df_merge.dropna(inplace = True)

    df_merge.to_csv(r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\TNA\RawData.csv')

    #     raw_data = pd.read_csv(r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\RawData.csv')

    #     raw_data = raw_data.loc[:,['InvestmentId', 'EffectiveDate', 'ValidationCodeId', 'ActionType_Real',
    #        'ActionTime_Real', 'Date', 'Hour', 'TNA', 'FailureGeneratedTime',
    #        'CountryId', 'ActionStatus_OneHour', 'ActionStatus_24Hour',
    #        'Complete_OneHour', 'Complete_24Hour', 'FailureType', 'Operation',
    #        'TimeZone', 'Un_handledFailureCategory', 'difftime', 'marker', 'day',
    #        'Time']]

    #     df= raw_data
    
    
    with tqdm_notebook(total=100) as pbar:
        pbar.update(50)

    return df_merge
        


# In[7]:


def mason_cats(df_merge):
    df = df_merge

    df['FailureGeneratedTime'] = pd.to_datetime(df['FailureGeneratedTime'])
    df['difftime'] = dt.datetime.now() - df['FailureGeneratedTime']
    df['marker'] = df['difftime'].astype('timedelta64[m]').apply(lambda x: 'a' if x <= 60 else ('b' if 60 < x <= 1440 else ('c' if 1440 < x <= 10080 else ('d' if 10080 < x <= 43200 else ('e' if 43200 < x else None)))))

    list_loop1 = ['a','b','c','d','e']
    list_loop2 = ['df_a','df_b','df_c','df_d','df_e']

    for i in range(len(list_loop1)):
        globals()[list_loop2[i]] = df[df.marker == list_loop1[i]]

    #----------------------------------------------------------分割线-----------------------------------------------------------

    FailureType_tz1_ongoing_a = int(df_a.FailureType[(df_a.FailureType == 'OngoingFailure')&(df_a.TimeZone == 1)].count())
    FailureType_tz1_history_a = int(df_a.FailureType[df_a.TimeZone == 1].count() - df_a.FailureType[(df_a.FailureType == 'OngoingFailure')&(df_a.TimeZone == 1)].count())
    FailureType_tz2_ongoing_a = int(df_a.FailureType[(df_a.FailureType == 'OngoingFailure')&(df_a.TimeZone == 2)].count())
    FailureType_tz2_history_a = int(df_a.FailureType[df_a.TimeZone == 2].count() - df_a.FailureType[(df_a.FailureType == 'OngoingFailure')&(df_a.TimeZone == 2)].count())
    FailureType_tz3_ongoing_a = int(df_a.FailureType[(df_a.FailureType == 'OngoingFailure')&(df_a.TimeZone == 3)].count())
    FailureType_tz3_history_a = int(df_a.FailureType[df_a.TimeZone == 3].count() - df_a.FailureType[(df_a.FailureType == 'OngoingFailure')&(df_a.TimeZone == 3)].count())

    FailureType_tz1_ongoing_b = int(df_b.FailureType[(df_b.FailureType == 'OngoingFailure')&(df_b.TimeZone == 1)].count())
    FailureType_tz1_history_b = int(df_b.FailureType[df_b.TimeZone == 1].count() - df_b.FailureType[(df_b.FailureType == 'OngoingFailure')&(df_b.TimeZone == 1)].count())
    FailureType_tz2_ongoing_b = int(df_b.FailureType[(df_b.FailureType == 'OngoingFailure')&(df_b.TimeZone == 2)].count())
    FailureType_tz2_history_b = int(df_b.FailureType[df_b.TimeZone == 2].count()- df_b.FailureType[(df_b.FailureType == 'OngoingFailure')&(df_b.TimeZone == 2)].count())
    FailureType_tz3_ongoing_b = int(df_b.FailureType[(df_b.FailureType == 'OngoingFailure')&(df_b.TimeZone == 3)].count())
    FailureType_tz3_history_b = int(df_b.FailureType[df_b.TimeZone == 3].count()- df_b.FailureType[(df_b.FailureType == 'OngoingFailure')&(df_b.TimeZone == 3)].count())

    FailureType_tz1_ongoing_c = int(df_c.FailureType[(df_c.FailureType == 'OngoingFailure')&(df_c.TimeZone == 1)].count())
    FailureType_tz1_history_c = int(df_c.FailureType[df_c.TimeZone == 1].count()- df_c.FailureType[(df_c.FailureType == 'OngoingFailure')&(df_c.TimeZone == 1)].count())
    FailureType_tz2_ongoing_c = int(df_c.FailureType[(df_c.FailureType == 'OngoingFailure')&(df_c.TimeZone == 2)].count())
    FailureType_tz2_history_c = int(df_c.FailureType[df_c.TimeZone == 2].count()- df_c.FailureType[(df_c.FailureType == 'OngoingFailure')&(df_c.TimeZone == 2)].count())
    FailureType_tz3_ongoing_c = int(df_c.FailureType[(df_c.FailureType == 'OngoingFailure')&(df_c.TimeZone == 3)].count())
    FailureType_tz3_history_c = int(df_c.FailureType[df_c.TimeZone == 3].count()- df_c.FailureType[(df_c.FailureType == 'OngoingFailure')&(df_c.TimeZone == 3)].count())

    FailureType_tz1_ongoing_d = int(df_d.FailureType[(df_d.FailureType == 'OngoingFailure')&(df_d.TimeZone == 1)].count())
    FailureType_tz1_history_d = int(df_d.FailureType[df_d.TimeZone == 1].count()- df_d.FailureType[(df_d.FailureType == 'OngoingFailure')&(df_d.TimeZone == 1)].count())
    FailureType_tz2_ongoing_d = int(df_d.FailureType[(df_d.FailureType == 'OngoingFailure')&(df_d.TimeZone == 2)].count())
    FailureType_tz2_history_d = int(df_d.FailureType[df_d.TimeZone == 2].count()- df_d.FailureType[(df_d.FailureType == 'OngoingFailure')&(df_d.TimeZone == 2)].count())
    FailureType_tz3_ongoing_d = int(df_d.FailureType[(df_d.FailureType == 'OngoingFailure')&(df_d.TimeZone == 3)].count())
    FailureType_tz3_history_d = int(df_d.FailureType[df_d.TimeZone == 3].count()- df_d.FailureType[(df_d.FailureType == 'OngoingFailure')&(df_d.TimeZone == 3)].count())

    FailureType_tz1_ongoing_e = int(df_e.FailureType[(df_e.FailureType == 'OngoingFailure')&(df_e.TimeZone == 1)].count())
    FailureType_tz1_history_e = int(df_e.FailureType[df_e.TimeZone == 1].count()- df_e.FailureType[(df_e.FailureType == 'OngoingFailure')&(df_e.TimeZone == 1)].count())
    FailureType_tz2_ongoing_e = int(df_e.FailureType[(df_e.FailureType == 'OngoingFailure')&(df_e.TimeZone == 2)].count())
    FailureType_tz2_history_e = int(df_e.FailureType[df_e.TimeZone == 2].count()- df_e.FailureType[(df_e.FailureType == 'OngoingFailure')&(df_e.TimeZone == 2)].count())
    FailureType_tz3_ongoing_e = int(df_e.FailureType[(df_e.FailureType == 'OngoingFailure')&(df_e.TimeZone == 3)].count())
    FailureType_tz3_history_e = int(df_e.FailureType[df_e.TimeZone == 3].count()- df_e.FailureType[(df_e.FailureType == 'OngoingFailure')&(df_e.TimeZone == 3)].count())

    #----------------------------------------------------------分割线----------------------------------------------------------- 

    FailureType_tz1_total_a = int(df_a.FailureType[df_a.TimeZone == 1].count())
    FailureType_tz2_total_a = int(df_a.FailureType[df_a.TimeZone == 2].count())
    FailureType_tz3_total_a = int(df_a.FailureType[df_a.TimeZone == 3].count())

    FailureType_tz1_total_b = int(df_b.FailureType[df_b.TimeZone == 1].count())
    FailureType_tz2_total_b = int(df_b.FailureType[df_b.TimeZone == 2].count())
    FailureType_tz3_total_b = int(df_b.FailureType[df_b.TimeZone == 3].count())

    FailureType_tz1_total_c = int(df_c.FailureType[df_c.TimeZone == 1].count())
    FailureType_tz2_total_c = int(df_c.FailureType[df_c.TimeZone == 2].count())
    FailureType_tz3_total_c = int(df_c.FailureType[df_c.TimeZone == 3].count())

    FailureType_tz1_total_d = int(df_d.FailureType[df_d.TimeZone == 1].count())
    FailureType_tz2_total_d = int(df_d.FailureType[df_d.TimeZone == 2].count())
    FailureType_tz3_total_d = int(df_d.FailureType[df_d.TimeZone == 3].count())

    FailureType_tz1_total_e = int(df_e.FailureType[df_e.TimeZone == 1].count())
    FailureType_tz2_total_e = int(df_e.FailureType[df_e.TimeZone == 2].count())
    FailureType_tz3_total_e = int(df_e.FailureType[df_e.TimeZone == 3].count())

    #----------------------------------------------------------分割线----------------------------------------------------------- 

    x = ['A<=1H','1H<B<=24H','1D<C<=7D','7D<D<30D','E>30D']

    x1 = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]


    y1 = [FailureType_tz1_ongoing_a, FailureType_tz1_ongoing_b, FailureType_tz1_ongoing_c,FailureType_tz1_ongoing_d,FailureType_tz1_ongoing_e]
    y2 = [FailureType_tz1_history_a, FailureType_tz1_history_b, FailureType_tz1_history_c,FailureType_tz1_history_d,FailureType_tz1_history_e]

    y3 = [FailureType_tz2_ongoing_a, FailureType_tz2_ongoing_b, FailureType_tz2_ongoing_c,FailureType_tz2_ongoing_d,FailureType_tz2_ongoing_e]
    y4 = [FailureType_tz2_history_a, FailureType_tz2_history_b, FailureType_tz2_history_c,FailureType_tz2_history_d,FailureType_tz2_history_e]

    y5 = [FailureType_tz3_ongoing_a, FailureType_tz3_ongoing_b, FailureType_tz3_ongoing_c,FailureType_tz3_ongoing_d,FailureType_tz3_ongoing_e]
    y6 = [FailureType_tz3_history_a, FailureType_tz3_history_b, FailureType_tz3_history_c,FailureType_tz3_history_d,FailureType_tz3_history_e]

    y1_t = [FailureType_tz1_total_a,FailureType_tz1_total_b,FailureType_tz1_total_c,FailureType_tz1_total_d,FailureType_tz1_total_e]
    y2_t = [FailureType_tz2_total_a,FailureType_tz2_total_b,FailureType_tz2_total_c,FailureType_tz2_total_d,FailureType_tz2_total_e]
    y3_t = [FailureType_tz3_total_a,FailureType_tz3_total_b,FailureType_tz3_total_c,FailureType_tz3_total_d,FailureType_tz3_total_e]

    y_test = [FailureType_tz1_total_a,FailureType_tz1_total_b,FailureType_tz1_total_c,FailureType_tz1_total_d,FailureType_tz1_total_e,FailureType_tz2_total_a,FailureType_tz2_total_b,FailureType_tz2_total_c,FailureType_tz2_total_d,FailureType_tz2_total_e,FailureType_tz3_total_a,FailureType_tz3_total_b,FailureType_tz3_total_c,FailureType_tz3_total_d,FailureType_tz3_total_e]

    #----------------------------------------------------------分割线----------------------------------------------------------- 


    bar1 = Bar(title = f"Un-handle failures from {df['FailureGeneratedTime'].min().date()} to {df['FailureGeneratedTime'].max().date()} ")

    bar1.add("Mumbai_Ongoing", x, y1, is_stack=True, is_datazoom_show = True,legend_orient = 'vertical',legend_pos = "10%",legend_top = "50") #,is_label_show=True
    bar1.add("Mumbai_History", x, y2, is_stack=True, is_datazoom_show = True,legend_orient = 'vertical',legend_pos = "10%",legend_top = "50",is_label_show=False, mark_point = [{'coord': [x[0], y1_t[0]], 'name': 'total'},{'coord': [x[1], y1_t[1]], 'name': 'total'},{'coord': [x[2], y1_t[2]], 'name': 'total'},{'coord': [x[3], y1_t[3]], 'name': 'total'},{'coord': [x[4], y1_t[4]], 'name': 'total'}],mark_point_textcolor='black',mark_point_symbolsize=[0.1,50])

    bar2 = Bar(title = 'Failure')
    bar2.add("Shenzhen_Ongoing", x, y3, is_stack=True,is_label_show=False)
    bar2.add("Shenzhen_History", x, y4, is_stack=True,is_label_show=False, mark_point = [{'coord': [x[0], y2_t[0]], 'name': 'total'},{'coord': [x[1], y2_t[1]], 'name': 'total'},{'coord': [x[2], y2_t[2]], 'name': 'total'},{'coord': [x[3], y2_t[3]], 'name': 'total'},{'coord': [x[4], y2_t[4]], 'name': 'total'}],mark_point_textcolor='black',mark_point_symbolsize=[0.1,50])

    bar3 = Bar(title = 'Failure')
    bar3.add("Madrid_Ongoing", x, y5, is_stack=True,is_label_show=False) #
    bar3.add("Madrid_History", x, y6, is_stack=True, is_label_show=False, mark_point = [{'coord': [x[0], y3_t[0]], 'name': 'total'},{'coord': [x[1], y3_t[1]], 'name': 'total'},{'coord': [x[2], y3_t[2]], 'name': 'total'},{'coord': [x[3], y3_t[3]], 'name': 'total'},{'coord': [x[4], y3_t[4]], 'name': 'total'}],mark_point_textcolor='black',mark_point_symbolsize=[0.1,50]) #


    overlap = Overlap(width='100%',height=360)
    overlap.add(bar1)
    overlap.add(bar2)
    overlap.add(bar3)

    overlap.render(path=r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\TNA\Failure_5cats.html')

    print(overlap)


    with tqdm_notebook(total=100) as pbar:

        pbar.update(60)



# In[8]:


def nick_false_alarm(df_merge):

    df = df_merge

    df= df[(df.ActionType_Real >1)]
    df= df[(df.FailureType == 'OngoingFailure')]



    page = Page()

    dfpie=pd.pivot_table(df,index=["ValidationCodeId"],values='InvestmentId',aggfunc='count')

    dfpie2=dfpie.sort_values(by=["InvestmentId"],ascending=False)

    dfpietop5=dfpie2.head(5)
    #dfpietop5
    #取饼图legend
    dfpietop5T = dfpietop5.T

    list_namepie = []

    for name in dfpietop5T:

        if name!= 'ValidationCodeId':

            list_namepie.append(name)

    #list_namepie

    attr_pie = list_namepie 
    pie = Pie("BizRule", "Yearly",title_pos='center', width=360)
    pie.add("Top 5", attr_pie, dfpietop5T.values[0],         
    is_label_show=True, radius=[35, 70], rosetype='radius',legend_pos='left', label_text_color=None, legend_orient='vertical')

    #pie.render('pie.html') 


    df.ActionTime_Real = pd.DatetimeIndex(df.ActionTime_Real)
    df_ID =df
    df_ID.index = pd.DatetimeIndex(df_ID.index)
    df_ID = df_ID.reset_index()
    grouper = df_ID.groupby([pd.Grouper('ActionTime_Real'), 'ValidationCodeId'])
    result = grouper['ActionTime_Real'].count().unstack('ValidationCodeId').fillna(0)
    result = result.resample('M').sum()
    result = result.iloc[-13:-1,:]
    result.loc['Sum'] = result.apply(lambda x: x.sum(), axis=0)
    result = result.T
    result = result.sort_values(by=['Sum'],ascending=False)
    result = result.T
    #result['Sum'] = result.apply(lambda x: x.sum(), axis=1)
    result_Dynamic = result.iloc[:-1,:]
    result_Dynamic
    result_Dynamic2 = result_Dynamic.iloc[:,:10]
    result_Dynamic2.values[0]
    # 把Bizrule 的名字 一一提取出来
    list_nameDynamic = []
    for name in result_Dynamic2.columns:
        if name!= 'ActionTime_Real':
            list_nameDynamic.append(name)


    result_Dynamic3 = result_Dynamic2.reset_index()
    result_Dynamic3.ActionTime_Real = result_Dynamic3.ActionTime_Real.apply(lambda x: x.strftime('%y-%m-%d'))

    #动态图Dynamic
    attr_Dynamic = list_nameDynamic

    pie_1 = Pie("TNA Failure", "Monthly",title_pos='center')
    pie_1.add("Top 10", attr_Dynamic, result_Dynamic3.iloc[:,1:].values[0],
    is_label_show=True, radius=[35, 70], rosetype='radius',legend_pos='left', label_text_color=None, legend_orient='vertical')

    pie_2 = Pie("TNA Failure", "Monthly",title_pos='center')
    pie_2.add("Top 10", attr_Dynamic, result_Dynamic3.iloc[:,1:].values[1],
    is_label_show=True, radius=[35, 70], rosetype='radius',legend_pos='left', label_text_color=None, legend_orient='vertical')

    pie_3 = Pie("TNA Failure", "Monthly",title_pos='center')
    pie_3.add("Top 10", attr_Dynamic, result_Dynamic3.iloc[:,1:].values[2],
    is_label_show=True, radius=[35, 70], rosetype='radius',legend_pos='left', label_text_color=None, legend_orient='vertical')

    pie_4 = Pie("TNA Failure", "Monthly",title_pos='center')
    pie_4.add("Top 10", attr_Dynamic, result_Dynamic3.iloc[:,1:].values[3],
    is_label_show=True, radius=[35, 70], rosetype='radius',legend_pos='left', label_text_color=None, legend_orient='vertical')

    pie_5 = Pie("TNA Failure", "Monthly",title_pos='center')
    pie_5.add("Top 10", attr_Dynamic, result_Dynamic3.iloc[:,1:].values[4],
    is_label_show=True, radius=[35, 70], rosetype='radius',legend_pos='left', label_text_color=None, legend_orient='vertical')

    pie_6 = Pie("TNA Failure", "Monthly",title_pos='center')
    pie_6.add("Top 10", attr_Dynamic, result_Dynamic3.iloc[:,1:].values[5],
    is_label_show=True, radius=[35, 70], rosetype='radius',legend_pos='left', label_text_color=None, legend_orient='vertical')

    pie_7 = Pie("TNA Failure", "Monthly",title_pos='center')
    pie_7.add("Top 10", attr_Dynamic, result_Dynamic3.iloc[:,1:].values[6],
    is_label_show=True, radius=[35, 70], rosetype='radius',legend_pos='left', label_text_color=None, legend_orient='vertical')

    pie_8 = Pie("TNA Failure", "Monthly",title_pos='center')
    pie_8.add("Top 10", attr_Dynamic, result_Dynamic3.iloc[:,1:].values[7],
    is_label_show=True, radius=[35, 70], rosetype='radius',legend_pos='left', label_text_color=None, legend_orient='vertical')

    pie_9 = Pie("TNA Failure", "Monthly",title_pos='center')
    pie_9.add("Top 10", attr_Dynamic, result_Dynamic3.iloc[:,1:].values[8],
    is_label_show=True, radius=[35, 70], rosetype='radius',legend_pos='left', label_text_color=None, legend_orient='vertical')

    pie_10 = Pie("TNA Failure", "Monthly",title_pos='center')
    pie_10.add("Top 10", attr_Dynamic, result_Dynamic3.iloc[:,1:].values[9],
    is_label_show=True, radius=[35, 70], rosetype='radius',legend_pos='left', label_text_color=None, legend_orient='vertical')

    pie_11 = Pie("TNA Failure", "Monthly",title_pos='center')
    pie_11.add("Top 10", attr_Dynamic, result_Dynamic3.iloc[:,1:].values[10],
    is_label_show=True, radius=[35, 70], rosetype='radius',legend_pos='left', label_text_color=None, legend_orient='vertical')

    pie_12 = Pie("TNA Failure", "Monthly",title_pos='center')
    pie_12.add("Top 10", attr_Dynamic, result_Dynamic3.iloc[:,1:].values[11],
    is_label_show=True, radius=[35, 70], rosetype='radius',legend_pos='left', label_text_color=None, legend_orient='vertical')


    timeline_Dynamic = Timeline(is_auto_play=False, timeline_bottom=0,width = 360)
    timeline_Dynamic.add(pie_1, result_Dynamic3.values[0,0])
    timeline_Dynamic.add(pie_2, result_Dynamic3.values[1,0])
    timeline_Dynamic.add(pie_3, result_Dynamic3.values[2,0])
    timeline_Dynamic.add(pie_4, result_Dynamic3.values[3,0])
    timeline_Dynamic.add(pie_5, result_Dynamic3.values[4,0])
    timeline_Dynamic.add(pie_6, result_Dynamic3.values[5,0])
    timeline_Dynamic.add(pie_7, result_Dynamic3.values[6,0])
    timeline_Dynamic.add(pie_8, result_Dynamic3.values[7,0])
    timeline_Dynamic.add(pie_9, result_Dynamic3.values[8,0])
    timeline_Dynamic.add(pie_10,result_Dynamic3.values[9,0])
    timeline_Dynamic.add(pie_11, result_Dynamic3.values[10,0])
    timeline_Dynamic.add(pie_12, result_Dynamic3.values[11,0])

    #daily 线型图

    configure(output_image=True) 

    #取Top 5 Failure
    result_line = result_Dynamic.iloc[:,:5]

    #line的名字

    Linelist_name = []
    for name in result_line:
        if name!= 'ActionTime':
            Linelist_name.append(name)

    result_line2 = result_line.reset_index()
    result_line2.ActionTime_Real = result_line2.ActionTime_Real.apply(lambda x: x.strftime('%y-%m-%d'))
    result_line2
    result_line3 = result_line2.T
    result_line3

    #line的时间 x轴
    time = result_line3.values[0]
    df_falsealarmdaily= df[(df.ActionType_Real >=7)]
    df_falsealarmdaily

    df_falsealarmdaily.index = pd.DatetimeIndex(df_falsealarmdaily.index)
    df_falsealarmdaily = df_falsealarmdaily.reset_index()

    grouper_falsealarmdaily = df_falsealarmdaily.groupby([pd.Grouper('ActionTime_Real'), 'ValidationCodeId'])
    result_falsealarmdaily = grouper_falsealarmdaily['ActionTime_Real'].count().unstack('ValidationCodeId').fillna(0)
    result_falsealarmdaily = result_falsealarmdaily.resample('M').sum()
    #不取当月不到月末的数据
    result_falsealarmdaily = result_falsealarmdaily.iloc[-13:-1,:]
    result_falsealarmdaily.loc['Sum'] = result_falsealarmdaily.apply(lambda x: x.sum(), axis=0)

    #取和line一样的Top 5 Failure
    result_falsealarmdaily = result_falsealarmdaily.T
    result_falsealarmdaily = result_falsealarmdaily.sort_values(by=['Sum'],ascending=False)
    result_falsealarmdaily = result_falsealarmdaily.T
    #result_falsealarmdaily['Sum'] = result_falsealarmdaily.apply(lambda x: x.sum(), axis=1)
    result_falsealarmdaily = result_falsealarmdaily.iloc[:-1,:]

    Lineorder_name = []
    for name in result_Dynamic2:
        if name!= 'ActionTime':
            Lineorder_name.append(name)

    order = Lineorder_name
    result_falsealarmdaily = result_falsealarmdaily[order]
    result_falsealarmdaily = result_falsealarmdaily.iloc[:,:5]
    result_falsealarmdaily2 = result_falsealarmdaily.reset_index()
    result_falsealarmdaily2.ActionTime_Real = result_falsealarmdaily2.ActionTime_Real.apply(lambda x: x.strftime('%y-%m-%d'))
    result_falsealarmdaily2
    result_falsealarmdaily3 = result_falsealarmdaily2.T
    result_falsealarmdaily3
    #line的值  y轴
    v1 = result_line3.values[1]
    v2 = result_line3.values[2]
    v3 = result_line3.values[3]
    v4 = result_line3.values[4]
    v5 = result_line3.values[5]

    v11 = result_falsealarmdaily3.values[1]
    v22 = result_falsealarmdaily3.values[2]
    v33 = result_falsealarmdaily3.values[3]
    v44 = result_falsealarmdaily3.values[4]
    v55 = result_falsealarmdaily3.values[5]
    for i in range(5):
        Linelist_name[i] = str(Linelist_name[i])

    line1 =Line('Biz Rule',background_color = 'white',title_text_size = 25)
    line1.add(Linelist_name[0],time,v1,is_label_show = True,is_smooth=True,mark_line=['average'],is_fill = True)
    line1.add(Linelist_name[0],time,v11,is_label_show = True,is_smooth=True,is_fill = True,area_opacity=0.1)

    line2 =Line('Biz Rule',background_color = 'white',title_text_size = 25)
    line2.add(Linelist_name[1],time,v2,is_label_show = True,is_smooth=True,mark_line=['average'],is_fill = True)
    line2.add(Linelist_name[1],time,v22,is_label_show = True,is_smooth=True,is_fill = True,area_opacity=0.1)

    line3 =Line('Biz Rule',background_color = 'white',title_text_size = 25)
    line3.add(Linelist_name[2],time,v3,is_label_show = True,is_smooth=True,mark_line=['average'],is_fill = True)
    line3.add(Linelist_name[2],time,v33,is_label_show = True,is_smooth=True,is_fill = True,area_opacity=0.1)

    line4 =Line('Biz Rule',background_color = 'white',title_text_size = 25)
    line4.add(Linelist_name[3],time,v4,is_label_show = True,is_smooth=True,mark_line=['average'],is_fill = True)
    line4.add(Linelist_name[3],time,v44,is_label_show = True,is_smooth=True,is_fill = True,area_opacity=0.1)

    line5 =Line('Biz Rule',background_color = 'white',title_text_size = 25)
    line5.add(Linelist_name[4],time,v5,is_label_show = True,is_smooth=True,mark_line=['average'],is_fill = True)
    line5.add(Linelist_name[4],time,v55,is_label_show = True,is_smooth=True,is_fill = True,area_opacity=0.1)

    # #page.add_chart(line)

    timeline_line = Timeline(is_auto_play=False, timeline_bottom=0,width = '100%')
    timeline_line.add(line1, Linelist_name[0])
    timeline_line.add(line2, Linelist_name[1])
    timeline_line.add(line3, Linelist_name[2])
    timeline_line.add(line4, Linelist_name[3])
    timeline_line.add(line5, Linelist_name[4])

    timeline_line



    time = dt.datetime.now() - relativedelta(months = +1)
    time = time.strftime("%m/%d/%Y")
        #first_time = dt.strptime(time, '%m/%d/%y')
    first_time = dt.datetime.strptime(time, "%m/%d/%Y").date()
    df_hourlyongoing = df[pd.to_datetime(df.Date)>=first_time]

    grouper_hourlyongoing = df_hourlyongoing.groupby([pd.Grouper('ActionTime_Real'), 'ValidationCodeId'])
    result_hourlyongoing = grouper_hourlyongoing['ActionTime_Real'].count().unstack('ValidationCodeId').fillna(0)
    result_hourlyongoing = result_hourlyongoing.resample('D').sum()


    new_time = []
    for time in result_hourlyongoing.index:

        new_time.append(time.isoweekday())
    new_time
    result_hourlyongoing.insert(0, 'weekday',new_time)
    result_hourlyongoing=result_hourlyongoing[~result_hourlyongoing['weekday'].isin([6])]
    result_hourlyongoing=result_hourlyongoing[~result_hourlyongoing['weekday'].isin([7])]
    result_hourlyongoing = result_hourlyongoing.drop('weekday', 1)

    result_hourlyongoing.loc['Sum'] = result_hourlyongoing.apply(lambda x: x.sum(), axis=0)
    result_hourlyongoing = result_hourlyongoing.T
    result_hourlyongoing = result_hourlyongoing.sort_values(by=['Sum'],ascending=False)
    result_hourlyongoing = result_hourlyongoing.T
    #result_hourlyongoing['Sum'] = result_hourlyongoing.apply(lambda x: x.sum(), axis=1)
    result_hourlyongoingline = result_hourlyongoing.iloc[:-1,:]
    result_hourlyongoingline2 = result_hourlyongoingline.iloc[:,:5]
    #result_hourlyongoingline2

    #hourly 线型图

    configure(output_image=True) 



    Linelisthourly_name = []
    for name in result_hourlyongoingline2:
        if name!= 'ActionTime':
            Linelisthourly_name.append(name)


    result_hourlyongoingline3 = result_hourlyongoingline2.reset_index()
    result_hourlyongoingline3.ActionTime_Real = result_hourlyongoingline3.ActionTime_Real.apply(lambda x: x.strftime('%m-%d'))
    result_hourlyongoingline3
    result_hourlyongoingline4 = result_hourlyongoingline3.T

    time_hourly = result_hourlyongoingline4.values[0]
    result_hourlyongoingline4


    hourlyongoinglineorder_name = []
    for name in result_hourlyongoingline2:
        if name!= 'ActionTime':
            hourlyongoinglineorder_name.append(name)

    order = hourlyongoinglineorder_name


    #取hourly的falsealarm

    df_falsealarmhourly= df_hourlyongoing[(df_hourlyongoing.ActionType_Real >=7)]
    grouper_falsealarmhourly = df_falsealarmhourly.groupby([pd.Grouper('ActionTime_Real'), 'ValidationCodeId'])
    result_falsealarmhourly = grouper_falsealarmhourly['ActionTime_Real'].count().unstack('ValidationCodeId').fillna(0)
    result_falsealarmhourly = result_falsealarmhourly.resample('D').sum()


    new_time = []
    for time in result_falsealarmhourly.index:

        new_time.append(time.isoweekday())
    new_time
    result_falsealarmhourly.insert(0, 'weekday',new_time)
    result_falsealarmhourly=result_falsealarmhourly[~result_falsealarmhourly['weekday'].isin([6])]
    result_falsealarmhourly=result_falsealarmhourly[~result_falsealarmhourly['weekday'].isin([7])]
    result_falsealarmhourly = result_falsealarmhourly.drop('weekday', 1)

    #result_falsealarmhourly.loc['Sum'] = result_falsealarmhourly.apply(lambda x: x.sum(), axis=0)
    #result_falsealarmhourly = result_falsealarmhourly.T
    #result_falsealarmhourly = result_falsealarmhourly.sort_values(by=['Sum'],ascending=False)
    #result_falsealarmhourly  = result_falsealarmhourly.T
    #result_hourlyongoing['Sum'] = result_hourlyongoing.apply(lambda x: x.sum(), axis=1)
    #result_hourlyongoingline = result_hourlyongoing.iloc[:-1,:]
    #result_hourlyongoingline2 = result_hourlyongoingline.iloc[:,:5]
    #result_falsealarmhourly
    #result_hourlyongoingline

    #取一样的failure 顺序
    hourlyongoinglineorder_name = []
    for name in result_hourlyongoingline2:
        if name!= 'ActionTime':
            hourlyongoinglineorder_name.append(name)

    order = hourlyongoinglineorder_name
    result_falsealarmhourly = result_falsealarmhourly[order]
    #result_falsealarmhourly = result_falsealarmhourly[:,:5]
    result_falsealarmhourly2 = result_falsealarmhourly.reset_index()
    result_falsealarmhourly2.ActionTime_Real = result_falsealarmhourly2.ActionTime_Real.apply(lambda x: x.strftime('%m-%d'))
    result_falsealarmhourly3 = result_falsealarmhourly2.T


    vhourly1 = result_hourlyongoingline4.values[1]
    vhourly2 = result_hourlyongoingline4.values[2]
    vhourly3 = result_hourlyongoingline4.values[3]
    vhourly4 = result_hourlyongoingline4.values[4]
    vhourly5 = result_hourlyongoingline4.values[5]

    vhourly11 = result_falsealarmhourly3.values[1]
    vhourly22 = result_falsealarmhourly3.values[2]
    vhourly33 = result_falsealarmhourly3.values[3]
    vhourly44 = result_falsealarmhourly3.values[4]
    vhourly55 = result_falsealarmhourly3.values[5]

    for i in range(5):
        Linelisthourly_name[i] = str(Linelisthourly_name[i])


    line_hourly1 =Line('Biz Rule',background_color = 'white',title_text_size = 25)
    line_hourly1.add(Linelisthourly_name[0],time_hourly,vhourly1,is_label_show = True,is_smooth=True,mark_line=['average'],is_fill = True)
    line_hourly1.add(Linelisthourly_name[0],time_hourly,vhourly11,is_label_show = True,is_smooth=True,is_fill = True,area_opacity=0.1)

    line_hourly2 =Line('Biz Rule',background_color = 'white',title_text_size = 25)
    line_hourly2.add(Linelisthourly_name[1],time_hourly,vhourly2,is_label_show = True,is_smooth=True,mark_line=['average'],is_fill = True)
    line_hourly2.add(Linelisthourly_name[1],time_hourly,vhourly22,is_label_show = True,is_smooth=True,is_fill = True,area_opacity=0.1)
    line_hourly3 =Line('Biz Rule',background_color = 'white',title_text_size = 25)
    line_hourly3.add(Linelisthourly_name[2],time_hourly,vhourly3,is_label_show = True,is_smooth=True,mark_line=['average'],is_fill = True)
    line_hourly3.add(Linelisthourly_name[2],time_hourly,vhourly33,is_label_show = True,is_smooth=True,is_fill = True,area_opacity=0.1)

    line_hourly4 =Line('Biz Rule',background_color = 'white',title_text_size = 25)
    line_hourly4.add(Linelisthourly_name[3],time_hourly,vhourly4,is_label_show = True,is_smooth=True,mark_line=['average'],is_fill = True)
    line_hourly4.add(Linelisthourly_name[3],time_hourly,vhourly44,is_label_show = True,is_smooth=True,is_fill = True,area_opacity=0.1)
    line_hourly5 =Line('Biz Rule',background_color = 'white',title_text_size = 25)
    line_hourly5.add(Linelisthourly_name[4],time_hourly,vhourly5,is_label_show = True,is_smooth=True,mark_line=['average'],is_fill = True)
    line_hourly5.add(Linelisthourly_name[4],time_hourly,vhourly55,is_label_show = True,is_smooth=True,is_fill = True,area_opacity=0.1)

    timeline_ongoing_line = Timeline(is_auto_play=False, timeline_bottom=-5,width = '100%')
    timeline_ongoing_line.add(line_hourly1, Linelisthourly_name[0])
    timeline_ongoing_line.add(line_hourly2, Linelisthourly_name[1])
    timeline_ongoing_line.add(line_hourly3, Linelisthourly_name[2])
    timeline_ongoing_line.add(line_hourly4, Linelisthourly_name[3])
    timeline_ongoing_line.add(line_hourly5, Linelisthourly_name[4])
    timeline_ongoing_line
    #page.add_chart(line_hourly)

    page.add(pie)
    page.add(timeline_Dynamic)
    page.add(timeline_line)
    page.add(timeline_ongoing_line)


    page.render(path=r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\TNA\Failure_Page.html')


    with tqdm_notebook(total=100) as pbar:
        pbar.update(70)
               
               
    return attr_pie
               
    


# In[ ]:


def mason_failure(df_merge,attr_pie):

    df = df_merge

    df= df[(df.ActionType_Real >1)]
    df.Date = pd.to_datetime(df.Date)
    df.ActionTime_Real = pd.to_datetime(df.ActionTime_Real)

    #----------------------------------------------------------分割线-----------------------------------------------------------

    time_list1 = df.groupby(pd.Grouper(key = 'Date', freq='M'))['Date'].first()
    time_list_end = df.groupby(pd.Grouper(key = 'Date', freq='M'))['Date'].last()

    time_list_begin = []
    for i in time_list1:
        time_list_begin.append(i.replace(day=1))

    time_month_list = []
    graph_list = []

    x = 1
    while x <= min(len(time_list1),12):
        time_month_list.append('df_m'+str(x))
        graph_list.append('graph'+str(x))
        x += 1

    time_list_begin = time_list_begin[-min(len(time_list1),13):-1]   
    time_list_end = time_list_end[-min(len(time_list1),13):-1]

    for i in range(0,min(len(time_list1),12)):
         globals()[time_month_list[i]]= df[(time_list_begin[i]<=df['Date'])&(df['Date']<=time_list_end[i])]

    #----------------------------------------------------------分割线-----------------------------------------------------------

    df_yearly_avg1 = pd.DataFrame()
    df_yearly_avg2 = pd.DataFrame()
    date_name_list = []

    for i in range(0,min(len(time_list1),12)):
        df_hourlyongoing = globals()[time_month_list[i]]
        month_name = str(df_hourlyongoing.iloc[0,4].strftime('%m')) + '月'
        date_name = str(df_hourlyongoing.iloc[0,4].strftime('%y')) + '年' + str(df_hourlyongoing.iloc[0,4].strftime('%m')) + '月'
        grouper_hourlyongoing =df_hourlyongoing.groupby([pd.Grouper('ActionTime_Real'), 'ValidationCodeId'])
        grouper_hourlyongoing = df_hourlyongoing.groupby([pd.Grouper('ActionTime_Real'), 'ValidationCodeId'])
        result_hourlyongoing = grouper_hourlyongoing['ActionTime_Real'].count().unstack('ValidationCodeId').fillna(0)
        result_hourlyongoing = result_hourlyongoing.resample('D').sum()
        result_hourlyongoing.loc['Sum'] = result_hourlyongoing.apply(lambda x: x.sum(), axis=0)
        result_hourlyongoing = result_hourlyongoing.T
        result_hourlyongoing = result_hourlyongoing.sort_values(by=['Sum'],ascending=False)
        result_hourlyongoing = result_hourlyongoing.T
        result_hourlyongoingline = result_hourlyongoing.iloc[:-1,:]
        result_hourlyongoingline.columns = result_hourlyongoingline.columns.astype(str)
        attr_pie1 = [str(i) for i in attr_pie]

        result_hourlyongoingline2 = result_hourlyongoingline[attr_pie1]


        #hourly 线型图
        configure(output_image=True) 

        Linelisthourly_name = []
        for name in result_hourlyongoingline2:
            if name!= 'ActionTime':
                Linelisthourly_name.append(name)

        result_hourlyongoingline3 = result_hourlyongoingline2.reset_index()
        result_hourlyongoingline3.ActionTime_Real = result_hourlyongoingline3.ActionTime_Real.apply(lambda x: x.strftime('%d'))
        result_hourlyongoingline4 = result_hourlyongoingline3.T

        time_hourly = result_hourlyongoingline4.values[0]
        time_hourly = list(map(str,map(int,time_hourly)))


        result_hourlyongoingline
        hourlyongoinglineorder_name = []
        for name in result_hourlyongoingline2:
            if name!= 'ActionTime':
                hourlyongoinglineorder_name.append(name)

        order = hourlyongoinglineorder_name
        #取hourly的falsealarm

        df_falsealarmhourly= df_hourlyongoing[(df_hourlyongoing.ActionType_Real >=7)]
        grouper_falsealarmhourly = df_falsealarmhourly.groupby([pd.Grouper('ActionTime_Real'), 'ValidationCodeId'])
        result_falsealarmhourly = grouper_falsealarmhourly['ActionTime_Real'].count().unstack('ValidationCodeId').fillna(0)
        result_falsealarmhourly = result_falsealarmhourly.resample('D').sum()


        #取一样的failure 顺序
        hourlyongoinglineorder_name = []
        for name in result_hourlyongoingline2:
            if name!= 'ActionTime':
                hourlyongoinglineorder_name.append(name)

        order = hourlyongoinglineorder_name

        result_falsealarmhourly.columns = result_falsealarmhourly.columns.astype(str)
        result_falsealarmhourly = result_falsealarmhourly[order]
        result_falsealarmhourly2 = result_falsealarmhourly.reset_index()
        result_falsealarmhourly2.ActionTime_Real = result_falsealarmhourly2.ActionTime_Real.apply(lambda x: x.strftime('%d'))
        result_falsealarmhourly3 = result_falsealarmhourly2.T

        time_hourly1 = result_falsealarmhourly3.values[0]
        time_hourly1 = list(map(str,map(int,time_hourly1)))

        vhourly1 = result_hourlyongoingline4.values[1]
        vhourly2 = result_hourlyongoingline4.values[2]
        vhourly3 = result_hourlyongoingline4.values[3]
        vhourly4 = result_hourlyongoingline4.values[4]
        vhourly5 = result_hourlyongoingline4.values[5]

        vhourly11 = result_falsealarmhourly3.values[1]
        vhourly22 = result_falsealarmhourly3.values[2]
        vhourly33 = result_falsealarmhourly3.values[3]
        vhourly44 = result_falsealarmhourly3.values[4]
        vhourly55 = result_falsealarmhourly3.values[5]


        add1 = dict(zip(time_hourly,vhourly1))
        add2 = dict(zip(time_hourly,vhourly2))
        add3 = dict(zip(time_hourly,vhourly3))
        add4 = dict(zip(time_hourly,vhourly4))
        add5 = dict(zip(time_hourly,vhourly5))

        add11 = dict(zip(time_hourly1,vhourly11))
        add22 = dict(zip(time_hourly1,vhourly22))
        add33 = dict(zip(time_hourly1,vhourly33))
        add44 = dict(zip(time_hourly1,vhourly44))
        add55 = dict(zip(time_hourly1,vhourly55))



        df_yearly_avg1 = df_yearly_avg1.append([add1,add2,add3,add4,add5], ignore_index=True,verify_integrity=True)
        df_yearly_avg2 = df_yearly_avg2.append([add11,add22,add33,add44,add55], ignore_index=True,verify_integrity=True)


        for j in range(5):
            Linelisthourly_name[j] = str(Linelisthourly_name[j])


        line_hourly1 =Line('Biz Rules: '+f'{date_name}',background_color = 'white',title_text_size = 20)
        line_hourly1.add(Linelisthourly_name[0],time_hourly,vhourly1,is_label_show = True,is_smooth=True,mark_line=['average'],is_fill = True,area_opacity=0.0001,legend_selectedmode='single',is_splitline_show = False)
        line_hourly1.add(Linelisthourly_name[0],time_hourly1,vhourly11,is_label_show = True,is_smooth=True,is_fill = True,area_opacity=0.1,legend_selectedmode='single',is_splitline_show = False)

        line_hourly2 =Line('Biz Rules: '+f'{date_name}',background_color = 'white',title_text_size = 20)
        line_hourly2.add(Linelisthourly_name[1],time_hourly,vhourly2,is_label_show = True,is_smooth=True,mark_line=['average'],is_fill = True,area_opacity=0.0001,legend_selectedmode='single',is_splitline_show = False)
        line_hourly2.add(Linelisthourly_name[1],time_hourly1,vhourly22,is_label_show = True,is_smooth=True,is_fill = True,area_opacity=0.1,legend_selectedmode='single',is_splitline_show = False)

        line_hourly3 =Line('Biz Rules: '+f'{date_name}',background_color = 'white',title_text_size = 20)
        line_hourly3.add(Linelisthourly_name[2],time_hourly,vhourly3,is_label_show = True,is_smooth=True,mark_line=['average'],is_fill = True,area_opacity=0.0001,legend_selectedmode='single',is_splitline_show = False)
        line_hourly3.add(Linelisthourly_name[2],time_hourly1,vhourly33,is_label_show = True,is_smooth=True,is_fill = True,area_opacity=0.1,legend_selectedmode='single',is_splitline_show = False)

        line_hourly4 =Line('Biz Rules: '+f'{date_name}',background_color = 'white',title_text_size = 20)
        line_hourly4.add(Linelisthourly_name[3],time_hourly,vhourly4,is_label_show = True,is_smooth=True,mark_line=['average'],is_fill = True,area_opacity=0.0001,legend_selectedmode='single',is_splitline_show = False)
        line_hourly4.add(Linelisthourly_name[3],time_hourly1,vhourly44,is_label_show = True,is_smooth=True,is_fill = True,area_opacity=0.1,legend_selectedmode='single',is_splitline_show = False)

        line_hourly5 =Line('Biz Rules: '+f'{date_name}',background_color = 'white',title_text_size = 20)
        line_hourly5.add(Linelisthourly_name[4],time_hourly,vhourly5,is_label_show = True,is_smooth=True,mark_line=['average'],is_fill = True,area_opacity=0.0001,legend_selectedmode='single',is_splitline_show = False)
        line_hourly5.add(Linelisthourly_name[4],time_hourly1,vhourly55,is_label_show = True,is_smooth=True,is_fill = True,area_opacity=0.1,legend_selectedmode='single',is_splitline_show = False)

        date_name_list.append(date_name)

        overlap = Overlap()
        overlap.add(line_hourly1)
        overlap.add(line_hourly2)
        overlap.add(line_hourly3)
        overlap.add(line_hourly4)
        overlap.add(line_hourly5)

        globals()[graph_list[i]] = overlap



    #----------------------------------------------------------分割线-----------------------------------------------------------

    df_yearly_avg1.loc['Average'] = df_yearly_avg1.apply(lambda x: x.mean(), axis=0)
    df_yearly_avg2.loc['Average'] = df_yearly_avg2.apply(lambda x: x.mean(), axis=0)

    df_yearly_avg1.loc['Total'] = df_yearly_avg1.apply(lambda x: x.sum(), axis=0)
    df_yearly_avg2.loc['Total'] = df_yearly_avg2.apply(lambda x: x.sum(), axis=0)

    df_yearly_avg1 = df_yearly_avg1.reindex([str(i) for i in sorted([int(i) for i in df_yearly_avg1.columns])], axis=1)
    df_yearly_avg2 = df_yearly_avg2.reindex([str(i) for i in sorted([int(i) for i in df_yearly_avg2.columns])], axis=1)

    df_yearly_avg1_list = df_yearly_avg1.loc['Average',:].tolist()
    df_yearly_avg2_list = df_yearly_avg2.loc['Average',:].tolist()
    df_yearly_tot1_list = df_yearly_avg1.loc['Total',:].tolist()
    df_yearly_tot2_list = df_yearly_avg2.loc['Total',:].tolist()
    df_yearly_col_list = df_yearly_avg1.columns.tolist()

    df_yearly_avg1_list = [int(i) for i in df_yearly_avg1_list]
    df_yearly_avg2_list = [int(i) for i in df_yearly_avg2_list]
    df_yearly_tot1_list = [int(i) for i in df_yearly_tot1_list]
    df_yearly_tot2_list = [int(i) for i in df_yearly_tot2_list]

    line_hourly6 =Line('Summary',background_color = 'white',title_text_size = 20)
    line_hourly6.add('Average',df_yearly_col_list,df_yearly_avg1_list,is_label_show = True,is_smooth=True,mark_line=['average'],is_fill = True,area_opacity=0.0001,legend_selectedmode='single',is_splitline_show = False)
    line_hourly6.add('Average',df_yearly_col_list,df_yearly_avg2_list,is_label_show = True,is_smooth=True,mark_line=['average'],is_fill = True,area_opacity=0.1,legend_selectedmode='single',is_splitline_show = False)
    line_hourly7 =Line('Summary',background_color = 'white',title_text_size = 20)
    line_hourly7.add('Total',df_yearly_col_list,df_yearly_tot1_list,is_label_show = True,is_smooth=True,mark_line=['average'],is_fill = True,area_opacity=0.0001,legend_selectedmode='single',is_splitline_show = False)
    line_hourly7.add('Total',df_yearly_col_list,df_yearly_tot2_list,is_label_show = True,is_smooth=True,mark_line=['average'],is_fill = True,area_opacity=0.1,legend_selectedmode='single',is_splitline_show = False)


    overlap = Overlap()
    overlap.add(line_hourly6)
    overlap.add(line_hourly7)
    graph_avg = overlap

    timeline_auto =  Timeline(timeline_bottom = 0,is_auto_play = False,timeline_play_interval = 2000,width = '100%',height = 500)


    for i in range(0,min(len(time_list1),12)):
        timeline_auto.add(globals()[graph_list[i]],str(date_name_list[i]))

    timeline_auto.add(graph_avg,'Summary')

    timeline_auto.render(path=r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\TNA\Failure_Daily.html')


    with tqdm_notebook(total=100) as pbar:
        pbar.update(80)
               


# In[ ]:


def andy_mo(df_merge):
    
    df = df_merge 


    df['FailureGeneratedTime']=pd.to_datetime(df['FailureGeneratedTime'])
    #df['week']=df['FailureGeneratedTime'].apply(lambda x: x.strftime("%Y-%m-%d"))
    df['Day']=df['FailureGeneratedTime'].apply(lambda x: x.strftime("%Y-%m-%d"))
    df['Hour']=df['FailureGeneratedTime'].apply(lambda x: x.strftime("%Y-%m-%d %H"))
    #df['Year']=df['FailureGeneratedTime'].apply(lambda x: x.strftime("%Y"))
    df['Month']=df['FailureGeneratedTime'].apply(lambda x: x.strftime("%Y-%m"))
    df['Day']=pd.to_datetime(df['Day'])
    df['Bizday']=df.groupby('Month')['Day'].rank("dense", ascending=True)
    df1 = df[df.FailureType.isin(['OngoingFailure'])] #ongoing failure
    df2 = df[df.FailureType.isin(['HistoricalFailure'])] #Historical failure

    #daily Total 包括history和ongoing
    df['ActionStatus_OneHour']=df['ActionStatus_OneHour'].astype(int)
    df['ActionStatus_24Hour']=df['ActionStatus_24Hour'].astype(int)
    df['Complete_OneHour']=df['Complete_OneHour'].astype(int)
    df['Complete_24Hour']=df['Complete_24Hour'].astype(int)



    df_Daily=pd.pivot_table(df,index=['Day'],
                    values=['ActionStatus_OneHour','ActionStatus_24Hour','Complete_OneHour','Complete_24Hour'],
                    aggfunc=np.sum)
    df_Daily=df_Daily.reset_index()

    df_TotalFailureNum=df.groupby('Day').agg({'InvestmentId': 'count'})
    df_TotalFailureNum=df_TotalFailureNum.reset_index()
    df_TotalFailureNum.rename(columns={ 'InvestmentId': 'Total_Failure_Num'}, inplace=True)

    df_DailyActionTotalNum = df[df.ActionType_Real.isin(['3','7','8'])]
    df_DailyActionTotalNum = df_DailyActionTotalNum.groupby('Day').agg({'InvestmentId': 'count'})
    df_DailyActionTotalNum = df_DailyActionTotalNum.reset_index()
    df_DailyActionTotalNum.rename(columns={ 'InvestmentId': 'DailyActionFailureNum'}, inplace=True)

    df_Daily=pd.merge(df_Daily,df_TotalFailureNum,on='Day')
    df_Daily=pd.merge(df_Daily,df_DailyActionTotalNum,on='Day')

    df_Daily.rename(columns={ 'ActionStatus_24Hour': 'Timeliness_24H_Num','ActionStatus_OneHour': 'Timeliness_1H_Num',
                    'Complete_24Hour': 'Completed_24H_Num','Complete_OneHour': 'Completed_1H_Num'}, inplace=True)

    df_Daily['Daily_Completeness']=df_Daily['Completed_24H_Num']/df_Daily['Total_Failure_Num']
    df_Daily['Daily_Completeness']=round(df_Daily['Daily_Completeness'].apply(lambda x: x*100),2)
    df_Daily['T+24_Timeliness']=df_Daily['Timeliness_24H_Num']/df_DailyActionTotalNum['DailyActionFailureNum']
    df_Daily['T+24_Timeliness']=round(df_Daily['T+24_Timeliness'].apply(lambda x: x*100),2)
    df_Daily['T+1_Timeliness']=df_Daily['Timeliness_1H_Num']/df_DailyActionTotalNum['DailyActionFailureNum']
    df_Daily['T+1_Timeliness']=round(df_Daily['T+1_Timeliness'].apply(lambda x: x*100),2)

    #daily Total ongoing
    df1['ActionStatus_OneHour']=df1['ActionStatus_OneHour'].astype(int)
    df1['ActionStatus_24Hour']=df1['ActionStatus_24Hour'].astype(int)
    df1['Complete_OneHour']=df1['Complete_OneHour'].astype(int)
    df1['Complete_24Hour']=df1['Complete_24Hour'].astype(int)


    df_Daily_ongoing=pd.pivot_table(df1,index=['Day'],
                    values=['ActionStatus_OneHour','ActionStatus_24Hour','Complete_OneHour','Complete_24Hour'],
                    aggfunc=np.sum)
    df_Daily_ongoing=df_Daily_ongoing.reset_index()

    df_TotalFailureNum_ongoing=df1.groupby('Day').agg({'InvestmentId': 'count'})
    df_TotalFailureNum_ongoing=df_TotalFailureNum_ongoing.reset_index()
    df_TotalFailureNum_ongoing.rename(columns={ 'InvestmentId': 'Ongoing_Failure_Num'}, inplace=True)

    df_DailyActionTotalNum_ongoing = df1[df1.ActionType_Real.isin(['3','7','8'])]
    df_DailyActionTotalNum_ongoing = df_DailyActionTotalNum_ongoing.groupby('Day').agg({'InvestmentId': 'count'})
    df_DailyActionTotalNum_ongoing = df_DailyActionTotalNum_ongoing.reset_index()
    df_DailyActionTotalNum_ongoing.rename(columns={ 'InvestmentId': 'OngoingDailyActionFailureNum'}, inplace=True)

    df_Daily_ongoing=pd.merge(df_Daily_ongoing,df_TotalFailureNum_ongoing,on='Day')
    df_Daily_ongoing=pd.merge(df_Daily_ongoing,df_DailyActionTotalNum_ongoing,on='Day')

    df_Daily_ongoing.rename(columns={ 'ActionStatus_24Hour': 'Timeliness_24H_Num_Ongoing',
                             'ActionStatus_OneHour': 'Timeliness_1H_Num_Ongoing',
                             'Complete_24Hour': 'Completed_24H_Num_Ongoing',
                             'Complete_OneHour': 'Completed_1H_Num_Ongoing'}, inplace=True)

    df_Daily_ongoing['Daily_Completeness_Ongoing']=df_Daily_ongoing['Completed_24H_Num_Ongoing']/df_Daily_ongoing['Ongoing_Failure_Num']
    df_Daily_ongoing['Daily_Completeness_Ongoing']=round(df_Daily_ongoing['Daily_Completeness_Ongoing'].apply(lambda x: x*100),2)
    df_Daily_ongoing['T+24_Timeliness_Ongoing']=df_Daily_ongoing['Timeliness_24H_Num_Ongoing']/df_DailyActionTotalNum_ongoing['OngoingDailyActionFailureNum']
    df_Daily_ongoing['T+24_Timeliness_Ongoing']=round(df_Daily_ongoing['T+24_Timeliness_Ongoing'].apply(lambda x:  x*100),2)
    df_Daily_ongoing['T+1_Timeliness_Ongoing']=df_Daily_ongoing['Timeliness_1H_Num_Ongoing']/df_DailyActionTotalNum_ongoing['OngoingDailyActionFailureNum']
    df_Daily_ongoing['T+1_Timeliness_Ongoing']=round(df_Daily_ongoing['T+1_Timeliness_Ongoing'].apply(lambda x: x*100),2)


    df_Daily=pd.merge(df_Daily,df_Daily_ongoing,on='Day')

    df_Daily['Day']=pd.to_datetime(df_Daily['Day'])
    df_Daily['Month']=df_Daily['Day'].apply(lambda x: x.strftime("%Y-%m"))
    df_Daily['Bizday']=df_Daily.groupby('Month')['Day'].rank("dense", ascending=True)

    #hourly Total 包括history和ongoing
    df_Hourly=pd.pivot_table(df,index=['Hour'],
                    values=['ActionStatus_OneHour','ActionStatus_24Hour','Complete_OneHour','Complete_24Hour'],
                    aggfunc=np.sum)
    df_Hourly=df_Hourly.reset_index()

    df_TotalFailureNum_hourly=df.groupby('Hour').agg({'InvestmentId': 'count'})
    df_TotalFailureNum_hourly=df_TotalFailureNum_hourly.reset_index()
    df_TotalFailureNum_hourly.rename(columns={ 'InvestmentId': 'Total_Failure_Num'}, inplace=True)

    df_HourlyActionTotalNum = df[df.ActionType_Real.isin(['3','7','8'])]
    df_HourlyActionTotalNum = df_HourlyActionTotalNum.groupby('Hour').agg({'InvestmentId': 'count'})
    df_HourlyActionTotalNum = df_HourlyActionTotalNum.reset_index()
    df_HourlyActionTotalNum.rename(columns={ 'InvestmentId': 'HourlyActionFailureNum'}, inplace=True)

    df_Hourly=pd.merge(df_Hourly,df_TotalFailureNum_hourly,on='Hour')
    df_Hourly=pd.merge(df_Hourly,df_HourlyActionTotalNum,on='Hour')

    df_Hourly.rename(columns={ 'ActionStatus_24Hour': 'Timeliness_24H_Num','ActionStatus_OneHour': 'Timeliness_1H_Num',
                    'Complete_24Hour': 'Completed_24H_Num','Complete_OneHour': 'Completed_1H_Num'}, inplace=True)

    df_Hourly['Hourly_Completeness']=df_Hourly['Completed_24H_Num']/df_Hourly['Total_Failure_Num']
    df_Hourly['Hourly_Completeness']=round(df_Hourly['Hourly_Completeness'].apply(lambda x: x*100),2)
    df_Hourly['T+24_Timeliness']=df_Hourly['Timeliness_24H_Num']/df_HourlyActionTotalNum['HourlyActionFailureNum']
    df_Hourly['T+24_Timeliness']=round(df_Hourly['T+24_Timeliness'].apply(lambda x: x*100),2)
    df_Hourly['T+1_Timeliness']=df_Hourly['Timeliness_1H_Num']/df_HourlyActionTotalNum['HourlyActionFailureNum']
    df_Hourly['T+1_Timeliness']=round(df_Hourly['T+1_Timeliness'].apply(lambda x: x*100),2)

    #Hourly Total ongoing
    df_Hourly_ongoing=pd.pivot_table(df1,index=['Hour'],
                    values=['ActionStatus_OneHour','ActionStatus_24Hour','Complete_OneHour','Complete_24Hour'],
                    aggfunc=np.sum)
    df_Hourly_ongoing=df_Hourly_ongoing.reset_index()

    df_TotalFailureNum_ongoing_hourly=df1.groupby('Hour').agg({'InvestmentId': 'count'})
    df_TotalFailureNum_ongoing_hourly=df_TotalFailureNum_ongoing_hourly.reset_index()
    df_TotalFailureNum_ongoing_hourly.rename(columns={ 'InvestmentId': 'Ongoing_Failure_Num'}, inplace=True)

    df_HourlyActionTotalNum_ongoing = df1[df1.ActionType_Real.isin(['3','7','8'])]
    df_HourlyActionTotalNum_ongoing = df_HourlyActionTotalNum_ongoing.groupby('Hour').agg({'InvestmentId': 'count'})
    df_HourlyActionTotalNum_ongoing = df_HourlyActionTotalNum_ongoing.reset_index()
    df_HourlyActionTotalNum_ongoing.rename(columns={ 'InvestmentId': 'OngoingHourlyActionFailureNum'}, inplace=True)

    df_Hourly_ongoing=pd.merge(df_Hourly_ongoing,df_TotalFailureNum_ongoing_hourly,on='Hour',how = 'left')
    df_Hourly_ongoing=pd.merge(df_Hourly_ongoing,df_HourlyActionTotalNum_ongoing,on='Hour',how = 'left')

    df_Hourly_ongoing.rename(columns={ 'ActionStatus_24Hour': 'Timeliness_24H_Num_Ongoing',
                             'ActionStatus_OneHour': 'Timeliness_1H_Num_Ongoing',
                             'Complete_24Hour': 'Completed_24H_Num_Ongoing',
                             'Complete_OneHour': 'Completed_1H_Num_Ongoing'}, inplace=True)

    df_Hourly_ongoing['Hourly_Completeness_Ongoing']=df_Hourly_ongoing['Completed_24H_Num_Ongoing']/df_Hourly_ongoing['Ongoing_Failure_Num']
    df_Hourly_ongoing['Hourly_Completeness_Ongoing']=round(df_Hourly_ongoing['Hourly_Completeness_Ongoing'].apply(lambda x: x*100),2)
    df_Hourly_ongoing['T+24_Timeliness_Ongoing']=df_Hourly_ongoing['Timeliness_24H_Num_Ongoing']/df_HourlyActionTotalNum_ongoing['OngoingHourlyActionFailureNum']
    df_Hourly_ongoing['T+24_Timeliness_Ongoing']=round(df_Hourly_ongoing['T+24_Timeliness_Ongoing'].apply(lambda x:  x*100),2)
    df_Hourly_ongoing['T+1_Timeliness_Ongoing']=df_Hourly_ongoing['Timeliness_1H_Num_Ongoing']/df_HourlyActionTotalNum_ongoing['OngoingHourlyActionFailureNum']
    df_Hourly_ongoing['T+1_Timeliness_Ongoing']=round(df_Hourly_ongoing['T+1_Timeliness_Ongoing'].apply(lambda x: x*100),2)


    df_Hourly=pd.merge(df_Hourly,df_Hourly_ongoing,on='Hour')

    df_Hourly['Hour']=pd.to_datetime(df_Hourly['Hour'])
    df_Hourly['Month']=df_Hourly['Hour'].apply(lambda x: x.strftime("%Y-%m"))
    df_Hourly['Day']=df_Hourly['Hour'].apply(lambda x: x.strftime("%Y-%m-%d"))
    df_Hourly['Day']=pd.to_datetime(df_Hourly['Day'])
    df_Hourly['Bizday']=df_Hourly.groupby('Month')['Day'].rank("dense", ascending=True)


    df_Hourly.to_csv(r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\TNA\Hourly.csv')


    df_Daily.to_csv(r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\TNA\Daily.csv')



    #prediction 部分
    Pre_Daily=pd.crosstab(df1.Bizday,df1['Month'])
    Pre_Daily1=Pre_Daily.values
    Pre_Daily1 = np.insert(Pre_Daily1, 0, values=0, axis=1)


    for i in range(Pre_Daily1.shape[0]):    #range(df1.shape[0]): #行
        aa=0
        Total=0
        for j in reversed(range(Pre_Daily1.shape[1])): #反向读列 最新的data在后面  
            if Pre_Daily1[i][j]>0:
                aa=aa+1
                Total=Total+Pre_Daily1[i][j]
                if 5<aa<7:
                    Pre_Daily1[i][0]=Total/6
                    Total=0
                    aa=0
                    break


    r_name=list(Pre_Daily._stat_axis)
    Pre_Daily_= DataFrame(Pre_Daily1,index=list(r_name))
    Pre_Daily_=Pre_Daily_.rename(columns={0:'Predict'})
    Pre_Daily_=Pre_Daily_.reset_index()
    Pre_Daily_=Pre_Daily_.rename(columns={'index':'Bizday'})


    df_prediction=pd.read_csv(r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\TNA\Prediction.csv')

    df_prediction['Day']=pd.to_datetime(df_prediction['Day'])
    df_prediction_=pd.merge(df_prediction,df_Daily,on='Day',how='left')
    df_prediction=df_prediction_.loc[:,['Day','Ongoing_Failure_Num_y', 'Month_x', 'Bizday_x','Predict']]

    df_prediction.rename(columns={ 'Ongoing_Failure_Num_y': 'Ongoing_Failure_Num','Month_x': 'Month', 
                                  'Bizday_x': 'Bizday'}, inplace=True)

    #生成未来1天的时间
    now_hour=datetime.now().strftime("%H")

    df_prediction['Day']=pd.to_datetime(df_prediction['Day'])
    end_date = (df_prediction['Day'].max() + dt.timedelta(days =2)).strftime("%Y-%m-%d")
    begin_date = (df_prediction['Day'].max() + dt.timedelta(days =1)).strftime("%Y-%m-%d")
    date_list = []
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    begin_date = datetime.strptime(begin_date, "%Y-%m-%d")
    #begin_date = datetime.datetime.strptime(time.strftime('%Y-%m-%d',time.localtime(time.time())), "%Y-%m-%d")
    if now_hour == '00':
        while begin_date <= end_date:
            date_str = begin_date.strftime("%Y-%m-%d")
            date_list.append(date_str)
            begin_date += dt.timedelta(days=1)

    date_list_=pd.DataFrame(date_list,columns=['Day'])
    df_prediction=pd.concat([df_prediction,date_list_],axis=0,sort=False)

    df_prediction['Day']=pd.to_datetime(df_prediction['Day'])
    df_prediction['Month']=df_prediction['Day'].apply(lambda x: x.strftime("%Y-%m"))
    df_prediction['Weekday']=df_prediction['Day'].apply(lambda x: x.strftime("%w"))
    df_prediction=df_prediction[df_prediction.Weekday.isin(['1','2','3','4','5'])]
    df_prediction['Bizday']=df_prediction.groupby('Month')['Day'].rank("dense", ascending=True)
    df_prediction['Month']=pd.to_datetime(df_prediction['Month'])

    df_prediction_nextmonth=df_prediction[df_prediction.Month.isin([df_prediction['Month'].max()])]
    df_prediction1=df_prediction[~df_prediction.Month.isin([df_prediction['Month'].max()])]
    df_prediction2=pd.merge(df_prediction_nextmonth,Pre_Daily_,on='Bizday')
    df_prediction2=df_prediction2.loc[:,['Day','Ongoing_Failure_Num','Month','Bizday','Predict_y']]
    df_prediction2.rename(columns={ 'Predict_y': 'Predict'}, inplace=True)
    df_prediction=pd.concat([df_prediction1,df_prediction2],axis=0,sort=False).fillna(0)
    df_prediction=df_prediction.loc[:,['Day','Ongoing_Failure_Num','Month','Bizday','Predict']]


    df_prediction.to_csv(r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\TNA\Prediction.csv')


    #画图部分 daily
    df_Daily['Un_Completed_24H_Num']=df_Daily['Total_Failure_Num']-df_Daily['Completed_24H_Num']
    df_Daily.sort_values(by='Day')
    df_Daily1=df_Daily.iloc[-23:,:]
    df_Daily1['Day']=pd.to_datetime(df_Daily1['Day'])
    df_Daily1['Day1']=df_Daily1['Day'].apply(lambda x: x.strftime("%Y-%m-%d"))


    page = Page()

    x = df_Daily1.Day1.to_list()
    Un_Completed=df_Daily1.Un_Completed_24H_Num.to_list()
    Completed=df_Daily1.Completed_24H_Num.to_list()
    T1_Timeliness=df_Daily1['T+1_Timeliness'].to_list()
    T24_Timeliness=df_Daily1['T+24_Timeliness'].to_list()

    #折线图
    line =Line('Daily',background_color = 'white',title_text_size = 20,width = 550)
    line.add("T1_Timeliness",x,T1_Timeliness,is_smooth=False,is_fill = False,area_opacity=0.001,is_symbol_show=False)
    line.add("T24_Timeliness",x,T24_Timeliness,is_smooth=False,is_fill = False,area_opacity=0.001,is_symbol_show=False)
    #line

    #柱状图
    bar = Bar('Daily',background_color = 'white',title_text_size = 25,width = 550)
    bar.add("Completed",x,Completed,is_stack=True)
    bar.add("Un_Completed",x,Un_Completed,is_stack=True)
    #bar

    overlap = Overlap(width = 550)
    #overlap.add(line,is_add_yaxis=True)
    overlap.add(bar)
    overlap.add(line,yaxis_index=1,is_add_yaxis=True)
    overlap


    overlap.render(r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\TNA\TNA_Daily.html')

    # Today=dt.datetime.now()#.strftime("%Y-%m-%d") #本机时间
    Today=dt.datetime.now()-dt.timedelta(hours=14)

    Today_wd=dt.datetime.now().strftime("%w")
    if Today_wd == '1':
        yesterday=Today-dt.timedelta(days=3)

    elif Today_wd == '6':
        Today=Today-dt.timedelta(days=1)
        yesterday=Today-dt.timedelta(days=2)
    elif Today_wd == '0':  #星期天
        Today=Today-dt.timedelta(days=2)
        yesterday=Today-dt.timedelta(days=3)   
    else:
        yesterday=Today-dt.timedelta(days=1)


    zeroToday = Today - dt.timedelta(hours=Today.hour, minutes=Today.minute, seconds=Today.second, microseconds=Today.microsecond)
    zeroyesterday = yesterday - dt.timedelta(hours=yesterday.hour, minutes=yesterday.minute, seconds=yesterday.second, microseconds=yesterday.microsecond)


    end_date_hour1 = zeroToday + dt.timedelta(hours =23)
    begin_date_hour1 = zeroToday + dt.timedelta(hours =1)
    date_list_hour1 = []
    while begin_date_hour1 <= end_date_hour1:
        date_str_hour1 = begin_date_hour1.strftime("%Y-%m-%d %H")
        date_list_hour1.append(date_str_hour1)
        begin_date_hour1 += dt.timedelta(hours=1)

    df_Hourly1=pd.DataFrame(date_list_hour1,columns=['Hour']) #今天的
    df_Hourly1['Hour']=pd.to_datetime(df_Hourly1['Hour'])
    df_Hourly1 = pd.merge(df_Hourly1,df_Hourly,on='Hour',how='left').fillna(0)


    end_date_hour2 = zeroyesterday + dt.timedelta(hours =23)
    begin_date_hour2 = zeroyesterday + dt.timedelta(hours =1)
    date_list_hour2 = []
    while begin_date_hour2 <= end_date_hour2:
        date_str_hour2 = begin_date_hour2.strftime("%Y-%m-%d %H")
        date_list_hour2.append(date_str_hour2)
        begin_date_hour2 += dt.timedelta(hours=1)

    df_Hourly2=pd.DataFrame(date_list_hour2,columns=['Hour']) #昨天的
    df_Hourly2['Hour']=pd.to_datetime(df_Hourly2['Hour'])
    df_Hourly2 = pd.merge(df_Hourly2,df_Hourly,on='Hour',how='left').fillna(0)
    # Today_wd=dt.datetime.now().strftime("%w")
    # if Today_wd == '1':
    #     yesterday=dt.datetime.now()-dt.timedelta(days=3)

    # elif Today_wd == '6':
    #     Today=dt.datetime.now()-dt.timedelta(days=1)
    #     yesterday=dt.datetime.now()-dt.timedelta(days=2)
    # elif Today_wd == '0':  #星期天
    #     Today=dt.datetime.now()-dt.timedelta(days=2)
    #     yesterday=dt.datetime.now()-dt.timedelta(days=3)   
    # else:
    #     yesterday=dt.datetime.now()-dt.timedelta(days=1)


    # zeroToday = Today - dt.timedelta(hours=Today.hour, minutes=Today.minute, seconds=Today.second, microseconds=Today.microsecond)
    # zeroyesterday = yesterday - dt.timedelta(hours=yesterday.hour, minutes=yesterday.minute, seconds=yesterday.second, microseconds=yesterday.microsecond)


    # end_date_hour1 = zeroToday + dt.timedelta(hours =23)
    # begin_date_hour1 = zeroToday + dt.timedelta(hours =1)
    # date_list_hour1 = []
    # while begin_date_hour1 <= end_date_hour1:
    #     date_str_hour1 = begin_date_hour1.strftime("%Y-%m-%d %H")
    #     date_list_hour1.append(date_str_hour1)
    #     begin_date_hour1 += dt.timedelta(hours=1)

    # df_Hourly1=pd.DataFrame(date_list_hour1,columns=['Hour']) #今天的
    # df_Hourly1['Hour']=pd.to_datetime(df_Hourly1['Hour'])
    # df_Hourly1 = pd.merge(df_Hourly1,df_Hourly,on='Hour',how='left').fillna(0)


    # end_date_hour2 = zeroyesterday + dt.timedelta(hours =23)
    # begin_date_hour2 = zeroyesterday + dt.timedelta(hours =1)
    # date_list_hour2 = []
    # while begin_date_hour2 <= end_date_hour2:
    #     date_str_hour2 = begin_date_hour2.strftime("%Y-%m-%d %H")
    #     date_list_hour2.append(date_str_hour2)
    #     begin_date_hour2 += dt.timedelta(hours=1)

    # df_Hourly2=pd.DataFrame(date_list_hour2,columns=['Hour']) #昨天的
    # df_Hourly2['Hour']=pd.to_datetime(df_Hourly2['Hour'])
    # df_Hourly2 = pd.merge(df_Hourly2,df_Hourly,on='Hour',how='left').fillna(0)


    #今天的hourly

    df_Hourly1['Un_Completed_24H_Num']=df_Hourly1['Total_Failure_Num']-df_Hourly1['Completed_24H_Num']
    #df_Hourly1=df_Hourly.iloc[-23:,:]
    df_Hourly1['Hour']=pd.to_datetime(df_Hourly1['Hour'])
    df_Hourly1['Hour1']=df_Hourly1['Hour'].apply(lambda x: x.strftime("%H"))

    page = Page()

    x_hourly = df_Hourly1.Hour1.to_list()
    #x_hourly=list(range(24))
    Un_Completed_hourly=df_Hourly1.Un_Completed_24H_Num.to_list()
    Completed_hourly=df_Hourly1.Completed_24H_Num.to_list()
    T1_Timeliness_hourly=df_Hourly1['T+1_Timeliness'].to_list()
    T24_Timeliness_hourly=df_Hourly1['T+24_Timeliness'].to_list()


    #柱状图
    bar_hourly = Bar('Hourly',background_color = 'white',title_text_size = 20,width = 550)
    bar_hourly.add("Completed",x_hourly,Completed_hourly,is_stack=True)
    bar_hourly.add("Un_Completed",x_hourly,Un_Completed_hourly,is_stack=True)
    #bar


    #折线图
    line_hourly =Line('Hourly',background_color = 'white',title_text_size = 20,width = 550)
    line_hourly.add("T1_Timeliness",x_hourly,T1_Timeliness_hourly,is_smooth=False,is_fill = False,area_opacity=0.001)
    line_hourly.add("T24_Timeliness",x_hourly,T24_Timeliness_hourly,is_smooth=False,is_fill = True,area_opacity=0.001)
    #line


    overlap_hourly = Overlap()
    #overlap.add(line,is_add_yaxis=True)
    overlap_hourly.add(bar_hourly)
    overlap_hourly.add(line_hourly,yaxis_index=1,is_add_yaxis=True)
    overlap_hourly

    ##############昨天的hourly

    df_Hourly2['Un_Completed_24H_Num']=df_Hourly2['Total_Failure_Num']-df_Hourly2['Completed_24H_Num']
    #df_Hourly1=df_Hourly.iloc[-23:,:]
    df_Hourly2['Hour']=pd.to_datetime(df_Hourly2['Hour'])
    df_Hourly2['Hour1']=df_Hourly2['Hour'].apply(lambda x: x.strftime("%H"))

    page = Page()

    x_hourly1 = df_Hourly2.Hour1.to_list()
    Un_Completed_hourly1=df_Hourly2.Un_Completed_24H_Num.to_list()
    Completed_hourly1=df_Hourly2.Completed_24H_Num.to_list()
    T1_Timeliness_hourly1=df_Hourly2['T+1_Timeliness'].to_list()
    T24_Timeliness_hourly1=df_Hourly2['T+24_Timeliness'].to_list()


    #柱状图
    bar_hourly1 = Bar('Hourly',background_color = 'white',title_text_size = 20,width = 550)
    bar_hourly1.add("Completed",x_hourly1,Completed_hourly1,is_stack=True)
    bar_hourly1.add("Un_Completed",x_hourly1,Un_Completed_hourly1,is_stack=True)
    #bar

    #折线图
    line_hourly1 =Line('Hourly',background_color = 'white',title_text_size = 20,width = 550)
    line_hourly1.add("T1_Timeliness",x_hourly1,T1_Timeliness_hourly1,is_smooth=False,is_fill = False,area_opacity=0.001)
    line_hourly1.add("T24_Timeliness",x_hourly1,T24_Timeliness_hourly1,is_smooth=False,is_fill = True,area_opacity=0.001)
    #line

    overlap_hourly1 = Overlap()
    #overlap.add(line,is_add_yaxis=True)
    overlap_hourly1.add(bar_hourly1)
    overlap_hourly1.add(line_hourly1,yaxis_index=1,is_add_yaxis=True)
    #overlap_hourly1

    ####### 昨天和今天的合在一起
    timeline_line = Timeline(is_auto_play=False, timeline_bottom=0,width = 550)

    Linelist_name=['%s'%(Today.strftime("%m-%d")),
                   '%s'%(yesterday.strftime("%m-%d"))]


    timeline_line.add(overlap_hourly, Linelist_name[0])
    timeline_line.add(overlap_hourly1, Linelist_name[1])



    timeline_line.render(r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\TNA\TNA_Hourly.html')

    #预测的图
    df_prediction1=df_prediction.iloc[-60:,:]
    df_prediction1['Day']=pd.to_datetime(df_prediction1['Day'])
    df_prediction1['Day1']=df_prediction1['Day'].apply(lambda x: x.strftime("%Y-%m-%d"))

    page = Page()

    x_Prediction = df_prediction1.Day1.to_list()
    Prediction=df_prediction1.Predict.to_list()
    Actual=df_prediction1.Ongoing_Failure_Num.to_list()

    line_Prediction =Line('Prediction',background_color = 'white',title_text_size = 20,width = 500)
    line_Prediction.add("Prediction",x_Prediction,Prediction,is_smooth=True,is_fill = True,area_opacity=0.001)
    line_Prediction.add("Actual",x_Prediction,Actual,is_smooth=True,is_fill = True,area_opacity=0.1)



    line_Prediction.render(r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\TNA\Prediction.html')

    with tqdm_notebook(total=100) as pbar:
        pbar.update(90)


               
    
               
    #-------------------------------------------------------分割线--------------------------------------------------------------           

#     send_mail(t)
               
    print('运行完成')

    with tqdm_notebook(total=100) as pbar:

        pbar.update(100) 


# In[ ]:


set_runtime = '20'

def auto_run():
    print('开启auto_run')
    recorder = 0
    t = 1
    
    
    global connection
    
    while True:
        time_now = datetime.now()
        running = False
        if recorder > 3:
            recorder = 0
        
        
        if time_now.strftime('%M') == set_runtime or 0<recorder<=3:
            print('准备开启running')
            
            connection = login_sql()
            
            running = True
            
            print('Start running at %s'%time_now)
            
        if running is True:
            try:
                print("启动进程")
                
                df_merge = run_python()
                mason_cats(df_merge)
                attr_pie = nick_false_alarm(df_merge)
                mason_failure(df_merge,attr_pie)
                andy_mo(df_merge)
                
                recorder = 0
                t += 1
                timeinterval = time_interval()
                if int(time_now.strftime('%M')) >= 20:
                    for x in tqdm_notebook(range(timeinterval),desc='跑成功:重启中'):
                        sleep(1)
                
            except Exception as e:
                print('报错啦:%s'%e)
                recorder += 1
                
                if recorder == 1:
                    send_mail_failure(e)
                    
                for x in tqdm_notebook(range(300),desc='报错啦:5分钟后重跑'):
                    sleep(1)
            
        
if __name__ == '__main__':
    auto_run()
            


# In[ ]:




