#!/usr/bin/env python
# coding: utf-8

# In[1]:


from __future__ import unicode_literals
from pyecharts import Line, Pie, Kline, Radar, Bar, Overlap
from pyecharts import Page
import pandas as pd

import numpy as np
import matplotlib
import pandas as pd
import time as tm
import calendar
import datetime as dt
import pyecharts
from datetime import datetime,timedelta,date
from dateutil.relativedelta import relativedelta
from datetime import date
from time import sleep
import win32com.client as win32
import pyodbc

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
    
    suject = "(missing)成功啦,第%s次,时间%s" % (t,datetime.now())

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

    mail_item.HTMLBody = html2
    
    mail_item.Attachments.Add(r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\TNA_missing\TNA_Report.html')

    mail_item.Send()
    
    print('成功email发送成功')
    
    with tqdm_notebook(total=100) as pbar:
        pbar.update(100)


# In[4]:


def send_mail_failure(e):
    suject = "(missing)报错啦,原因:%s,时间%s" % (e,datetime.now())

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
    
    print('报错email发送成功')


# In[5]:


def sql_reader():
    sql11 = '''
    select K.InvestmentId,K.InvestmentStatus,K.DataReadiness,K.Universe,K.CountryId,
    K.FrequencyPattern,K.Frequency,K.DelayInDays,K.EffectiveDate,K.ExpectedUpdateDate,H.EffectiveDateMaster,
    case when datediff(day, H.EffectiveDateMaster, GETDATE()) > 180 then 'TNA is not available within 6 month'
    when (datediff(day, H.EffectiveDateMaster, GETDATE()) <= 180 and datediff(day, H.EffectiveDateMaster, GETDATE()) > 90)
    then 'TNA is not available within 3 month'
    else 'Ongoing missing'end as TNADefectType
    from (
    select A.InvestmentId,A.InvestmentStatus,A.DataReadiness,A.Universe,A.CountryId,
    c.FrequencyPattern,c.Frequency,c.DelayInDays,d.ExpectedTime as EffectiveDate,
    case when datename(dw,DATEADD(day,(c.DelayInDays/5)*2+c.DelayInDays,d.ExpectedTime))='Saturday' 
    then DATEADD(day,(c.DelayInDays/5)*2+c.DelayInDays+2,d.ExpectedTime)
    when datename(dw,DATEADD(day,(c.DelayInDays/5)*2+DelayInDays,d.ExpectedTime))='Sunday' 
    then DATEADD(day,(c.DelayInDays/5)*2+c.DelayInDays+1,d.ExpectedTime)
    else DATEADD(day,(c.DelayInDays/5)*2+c.DelayInDays,d.ExpectedTime)
    end as ExpectedUpdateDate
    from 
    (select a.InvestmentId,a.InvestmentStatus,a.DataReadiness,a.Universe,a.CountryId,max(b.StartDate) as StartDate
    from StatusData_DMPERFORMDB.dbo.DataMissingInvestmentBasicInfo a 
    left join SupportData_DMWkspaceDB.dbo.PerformanceFeedInfoHistory b on a.InvestmentId=b.InvestmentId
    where a.InvestmentStatus='1'
    --and a.InvestmentId='0P000180A7'
    --and a.CountryId = 'ITA'
    and a.DataReadiness='9'
    and b.DataPointType='8'
    group by a.InvestmentId,a.InvestmentStatus,a.DataReadiness,a.Universe,a.CountryId) A
    left join SupportData_DMWkspaceDB.dbo.PerformanceFeedInfoHistory c on A.InvestmentId=c.InvestmentId and A.StartDate=c.StartDate
    left join [StatusData_DMPERFORMDB].[dbo].[DataMissingReport] d on A.InvestmentId=d.InvestmentId
    where c.DataPointType='8'
    and ReportTypeId='91'
    ) K
    left join 
    (select   a.InvestmentId, max(EndDate) as EffectiveDateMaster  from  MasterData_DMPerformDB.dbo.InvestmentTNA as a with (nolock)
    where a.InvestmentType = 130
    group by a.InvestmentId)H   on K.InvestmentId = H.InvestmentId
    where datepart(year,K.ExpectedUpdateDate)=datepart(year,getdate())
    and datepart(month,K.ExpectedUpdateDate)=datepart(month,getdate())
    '''
    new = pd.read_sql(sql11,connection)
    
    if datetime.strftime(datetime.now(),'%d') == 1:  
        new_initial = new
        old_initial= pd.read_excel(r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\TNA_missing\initial_data_tnamissing.xlsx')
        initial_data = pd.concat([old_initial,new_initial],axis=0,sort=False).drop_duplicates()
        initial_data.dropna(inplace = True)
        initial_data.to_excel(r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\TNA_missing\initial_data_tnamissing.xlsx')
    else:
        new_ongoing = new
        old_ongoing = pd.read_excel(r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\TNA_missing\ongoing_data_tnamissing.xlsx')
        ongoing_data = pd.concat([old_ongoing,new_ongoing],axis=0,sort=False).drop_duplicates()
        ongoing_data.dropna(inplace = True)
        ongoing_data.to_excel(r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\TNA_missing\ongoing_data_tnamissing.xlsx')
        
    df_key_initial = pd.read_excel(r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\TNA_missing\initial_data_tnamissing.xlsx')  
    # 每个月第一天的excel 路径
    df_key_ongoing = pd.read_excel(r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\TNA_missing\ongoing_data_tnamissing.xlsx') 
    # 每个月ongoing的excel 路径

    with tqdm_notebook(total=100) as pbar:
        pbar.update(50)
        
    return df_key_initial,df_key_ongoing


# In[6]:


def tna_missing_line(df_key_initial,df_key_ongoing):
    
    df_key_initial.ExpectedUpdateDate = pd.to_datetime(df_key_initial.ExpectedUpdateDate)
    df_key_initial_count = df_key_initial.groupby('ExpectedUpdateDate').InvestmentId.count()

    grouper_key = df_key_ongoing.groupby([pd.Grouper('ExpectedUpdateDate'), pd.Grouper('TNADefectType')])
    df_key_ongoing_count = grouper_key['ExpectedUpdateDate'].count().unstack('TNADefectType').fillna(0)

    df_key_ongoing_count['Total'] = df_key_ongoing_count.apply(lambda x: x.sum(), axis=1)

    df_key_result = pd.merge(df_key_initial_count, df_key_ongoing_count, on=['ExpectedUpdateDate'],
                             how='outer',).fillna(0)   # Merge 一起，默认用 第一天的excel的index作为merge之后的index
    df_key_result.rename(columns={"InvestmentId": "All_missing", "Total": "Ongoing_Total"},inplace= True)

    Time_x = []
    for x_time in df_key_result.index:  # 取出x轴 
        x_time = x_time.strftime("%m-%d")
        Time_x.append(x_time)

    Total_key = df_key_result.All_missing.to_list()
    Ongoing_key = df_key_result.Ongoing_Total.to_list()

    line =Line('Missing',background_color = 'white',title_text_size = 15,width = '100%')
    line.add("Benchmark",Time_x,Total_key,is_smooth=True,is_fill = False,area_opacity=0.001,is_more_utils = True)
    line.add("Actual",Time_x,Ongoing_key,is_smooth=True,is_fill = True,area_opacity=0.1,is_more_utils = True)
    
    with tqdm_notebook(total=100) as pbar:
        pbar.update(70)
    
    return line


# In[7]:


def tna_missing_bar_excel(df_key_initial,df_key_ongoing):
    
    today = datetime.today()

    i = 31  #  这里就是手造一下日期index
    try:
        try:
            end = datetime(today.year, today.month, i)
            star = datetime(today.year, today.month, 1)
            now = datetime(today.year, today.month, today.day)
        except:
            end = datetime(today.year, today.month, i-1)
            star = datetime(today.year, today.month, 1)
            now = datetime(today.year, today.month, today.day)

    except:
        end = datetime(today.year, today.month, i-3)
        star = datetime(today.year, today.month, 1)
        now = datetime(today.year, today.month, today.day)

    df_key_TNADefectType = df_key_ongoing.groupby('TNADefectType').InvestmentId.count()


    date_index = pd.date_range(start= star, end=end)

    df_key_bar_index = pd.DataFrame(date_index[date_index.weekday < 5],
                              columns=['ExpectedUpdateDate']) 

    df_key_bar_old = pd.read_excel(r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\TNA_missing\TNA_Missing_daily.xlsx')

    try:
        df_key_bar_old = df_key_bar_old.drop(['Unnamed: 0'], axis=1)
        df_key_bar_old = df_key_bar_old.drop(['Unnamed: 1'], axis=1)
        df_key_bar_old =df_key_bar_old
    except: 
        df_key_bar_old =df_key_bar_old

    value = [df_key_TNADefectType['Ongoing missing'],df_key_TNADefectType['TNA is not available within 3 month'],df_key_TNADefectType['TNA is not available within 6 month']]
    now_str = now.strftime("%Y-%m-%d")

    df_key_bar_value = pd.DataFrame(index = {today.day},data = {'Ongoing missing':value[0],'TNA is not available within 3 month':value[1],'TNA is not available within 6 month':value[2],'ExpectedUpdateDate':now_str })
    df_key_bar_value.ExpectedUpdateDate = pd.to_datetime(df_key_bar_value.ExpectedUpdateDate)


    df_key_bar_result = pd.concat([df_key_bar_old,df_key_bar_value])

    # concat 一起，默认用 第一天的excel的index作为merge之后的index
    
    df_key_bar_result.to_excel(r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\TNA_missing\TNA_Missing_daily.xlsx')
    
    with tqdm_notebook(total=100) as pbar:
        pbar.update(80)
        
    return df_key_bar_result,df_key_bar_index


# In[8]:


def tna_missing_allgraph(df_key_initial,df_key_ongoing,df_key_bar_result,df_key_bar_index,line):
    
    df_key_bar_result_charts = df_key_bar_result.set_index('ExpectedUpdateDate')
    df_key_bar_result_charts['Total'] = df_key_bar_result_charts.apply(lambda x: x.sum(), axis=1)


    df_key_bar_result_charts_final = pd.merge(df_key_bar_index, df_key_bar_result_charts, on=['ExpectedUpdateDate'],
                             how='outer',).fillna(0)   # Merge 一起，用非周末的月份

    Time_bar_x = []
    for x_bar_time in df_key_bar_result_charts_final.ExpectedUpdateDate:  # 取出x轴 
        x_bar_time = x_bar_time.strftime("%m-%d")
        Time_bar_x.append(x_bar_time)


    Ongoing_missing = df_key_bar_result_charts_final['Ongoing missing'].to_list()  # 转换 df 元素到list 
    Three_month_Missing = df_key_bar_result_charts_final['TNA is not available within 3 month'].to_list() # 转换 df 元素到list 
    Six_month_Missing = df_key_bar_result_charts_final['TNA is not available within 6 month'].to_list() # 转换 df 元素到list 
    Total_line = df_key_bar_result_charts_final.Total.to_list() # 转换 df 元素到list 
    
    page = Page()

    #---开始画Bar---

    bar =Bar('Missing',background_color = 'white',title_text_size = 15,width = '100%')
    bar.add("Ongoing",Time_bar_x,Ongoing_missing,is_stack=True,is_more_utils = True) # is_more_utils = True 这个是开启多个小工具
    bar.add("3 M",Time_bar_x,Three_month_Missing,is_stack=True,is_more_utils = True)
    bar.add("6 M",Time_bar_x,Six_month_Missing,is_stack=True,is_more_utils = True)

    line_bar =Line('Total',background_color = 'white',title_text_size = 15,width = '100%')
    line_bar.add("Total",Time_bar_x,Total_line,is_fill = False,area_opacity=0.001,is_more_utils = True)

    overlap = Overlap(width= '100%')  # 把 line 和bar overlap一起
    overlap.add(bar)
    overlap.add(line_bar)
    #overlap.render()
    page.add_chart(overlap)  # 把 所有page 一起
    page.add_chart(line)
    page.render(r'\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Python Code\PublicData_project1\TNA_missing\TNA_Report.html')
    
    with tqdm_notebook(total=100) as pbar:
        pbar.update(90)
        


# In[ ]:


def time_interval():
    timenow = datetime.now()
    time_nextday = timenow + relativedelta(days = 1)
    time_20 = time_nextday.strftime("%Y/%m/%d 00/20/%S")
    time_20 = datetime.strptime(time_20, "%Y/%m/%d %H/%M/%S")
    time_interval = time_20 - timenow
    return time_interval.seconds - 300


# In[ ]:


set_runtime = '00:20'

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
        
        
        if time_now.strftime('%H:%M') == set_runtime or 0<recorder<=3:
            print('准备开启running')
            connection = login_sql()
            running = True
            print('Start running at %s'%time_now)
            
        if running is True:
            try:
                print("启动进程")
                
                df_key_initial,df_key_ongoing = sql_reader()                
                print("sql_reader 运行成功")
                
                line = tna_missing_line(df_key_initial,df_key_ongoing)
                print("tna_missing_line 运行成功")
                
                df_key_bar_result,df_key_bar_index = tna_missing_bar_excel(df_key_initial,df_key_ongoing)
                print("tna_missing_bar_excel 运行成功")
                
                tna_missing_allgraph(df_key_initial,df_key_ongoing,df_key_bar_result,df_key_bar_index,line)
                print("tna_missing_allgraph 运行成功")
                
                send_mail(t)
                print("All 运行完成")
                
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
            

