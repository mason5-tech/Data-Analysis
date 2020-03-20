#!/usr/bin/env python
# coding: utf-8

# In[6]:


import pyodbc
import pandas as pd
import numpy as np
import sys
from datetime import datetime,date, timedelta
import time
import matplotlib
import copy
from time import sleep
from tqdm import tqdm_notebook
from tqdm import tqdm
from pandas import DataFrame
import traceback

got_err = False

today = []
today = datetime.now()



#while True:
#
connecting_string = '''
Driver={SQL Server Native Client 11.0};
Server=xxxxx\xxxxx;
Database=;
Uid=xxxxx\xxxxx;
Pwd=;
Trusted_Domain=;
Trusted_Connection=yes;
MARS_Connection=yes'''
connection = pyodbc.connect(connecting_string)

with tqdm_notebook(total=100) as pbar:
    pbar.update(10) 

start = time.time()

cursor = connection.cursor()


# In[7]:


sql_code = ''';with GenerateList as (
select distinct 
B.DeliveryId,B.FileId,B.GeneratedTime as TaskGeneratedTime,B.OwnerId,B.ZoneId,B.Status,B.LastUpdate,B.EndDate as TaskDoneDate,
a.InvestmentId,a.DataUnit,a.ValidationCodeId,a.EffectiveDate,a.ActionTime as FailureGenerateTime,a.UserId as FailureGenerateUser,
DATEDIFF(HOUR,B.GeneratedTime,(case when B.Status=0 then B.EndDate else B.LastUpdate end )) as TimeGap
from LogData_GPMainDB.dbo.PerformanceFailureDataSourceTracking a with(nolock)
right join 
(select b.DeliveryId,b.FileId,b.GeneratedTime,b.OwnerId,b.ZoneId,b.Status,b.LastUpdate,b.EndDate
from StatusData_DMPERFORMDB.dbo.DashBoardTask b with(nolock)
where ReportType=1 
and b.GeneratedTime<getdate()
and b.GeneratedTime>dateadd(DD,-1,getdate())
) B
on a.FileId=B.FileId
where a.ActionType=1 
and datediff(n,a.ActionTime,B.GeneratedTime)<10
and a.DataUnit in ('101','105','108') 
and a.ActionTime<getdate()
and a.ActionTime>dateadd(DD,-1,getdate())
)

,ActionList as (
select K.DeliveryId,K.FileId,K.TaskGeneratedTime,K.OwnerId,K.ZoneId,K.Status,K.LastUpdate,K.TaskDoneDate,
K.InvestmentId,K.DataUnit,K.ValidationCodeId,K.EffectiveDate,K.FailureGenerateTime,K.FailureGenerateUser,
C.ActionType,C.ActionTime,C.UserId as FailureActionUser
from GenerateList K
left join 
(select c.FileId,c.InvestmentId,c.EffectiveDate,c.ActionType,c.ActionTime,c.UserId,c.ValidationCodeId
from LogData_GPMainDB.dbo.PerformanceFailureDataSourceTracking c with(nolock) 
where 
c.ActionType between 7 and 8 and c.DataUnit in ('101','105','108')
and c.ActionTime<getdate()
and c.ActionTime>dateadd(DD,-1,getdate())
) C 
on (C.InvestmentId=K.InvestmentId and C.EffectiveDate=K.EffectiveDate and C.ValidationCodeId=K.ValidationCodeId)
where C.ActionTime>=K.TaskGeneratedTime 


union 

select K.DeliveryId,K.FileId,K.TaskGeneratedTime,K.OwnerId,K.ZoneId,K.Status,K.LastUpdate,K.TaskDoneDate,
K.InvestmentId,K.DataUnit,K.ValidationCodeId,K.EffectiveDate,K.FailureGenerateTime,K.FailureGenerateUser,
C.ActionType,C.ActionTime,C.UserId as FailureActionUser
from GenerateList K
left join 
(select c.FileId,c.InvestmentId,c.EffectiveDate,c.ValidationCodeId,c.ActionType,c.ActionTime,c.UserId
from LogData_GPMainDB.dbo.PerformanceFailureDataSourceTracking c with(nolock) 
where c.ActionType=3 and c.DataUnit in ('101','105','108')
and c.ActionTime<getdate()
and c.ActionTime>dateadd(DD,-1,getdate())
)C 
on (C.InvestmentId=K.InvestmentId and C.EffectiveDate=K.EffectiveDate and C.ValidationCodeId=K.ValidationCodeId and C.UserId=K.OwnerId)
where (C.ActionTime>=K.TaskGeneratedTime or C.ActionTime is null)
and (C.ActionTime<=(case when K.Status=0 then K.TaskDoneDate else K.LastUpdate end) or C.ActionTime is null)
)


select distinct 
H.DeliveryId,H.FileId,H.TaskGeneratedTime,H.OwnerId,y.Email as TaskownerUserName,H.ZoneId,H.Status,H.LastUpdate,H.TaskDoneDate,
H.InvestmentId,H.DataUnit,H.ValidationCodeId,H.EffectiveDate,H.FailureGenerateTime as FailureGenerateTime1,

case 
when (DATEPART(WEEKDAY,H.FailureGenerateTime) = '6' and CONVERT(varchar,H.FailureGenerateTime, 24) >= '18:30:00') 
then dateadd(day,2,CONVERT(varchar(100),CONVERT(varchar(10),H.FailureGenerateTime, 120)+' 18:30:00',120))
when (DATEPART(WEEKDAY,H.FailureGenerateTime) = '7') 
then dateadd(day,1,CONVERT(varchar(100),CONVERT(varchar(10),H.FailureGenerateTime, 120)+' 18:30:00',120))
when ((DATEPART(WEEKDAY,H.FailureGenerateTime)) = '1' and CONVERT(varchar,H.FailureGenerateTime, 24) < '18:30:00')
then CONVERT(varchar(100),CONVERT(varchar(10),H.FailureGenerateTime, 120)+' 18:30:00',120)
else H.FailureGenerateTime end  as FailureGenerateTime2,

H.FailureGenerateUser,
Q.ActionType,Q.ActionTime,Q.FailureActionUser,
d.UserId as FileUploadUser,
E.UserId as ReprocessUser,
F.UserId as MasterSourceUserId,

case when (H.TimeGap<=24 and E.UserId=H.OwnerId and d.UserId is null)
then 'OngoingFailure'
when (H.TimeGap<=24 and d.UserId is null and E.UserId is null)
then 'OngoingFailure'
when (H.TimeGap>24 and E.UserId=H.OwnerId and d.UserId is null )
then 'HistoricalFailure'
when (H.TimeGap>24 and d.UserId is null and E.UserId is null)
then 'HistoricalFailure'
when E.UserId!=H.OwnerId
then 'OutofFTSscope'
when d.UserId is not null
then 'OutofFTSscope'
else null 
end as FailureType,
case 
when (H.TimeGap<=24 and E.UserId=H.OwnerId and d.UserId is null) 
then 'OngoingFailure_System'
when (H.TimeGap<=24 and d.UserId is null and E.UserId is null)
then 'OngoingFailure_System'
when (H.TimeGap<=24 and E.UserId!=H.OwnerId)
then 'OngoingFailure_OutofFTSscope'
when (H.TimeGap<=24 and d.UserId is not null)
then 'OngoingFailure_OutofFTSscope'
when (H.TimeGap>24 and E.UserId=H.OwnerId and d.UserId is null) 
then 'HistoricalFailure_System'
when (H.TimeGap>24 and d.UserId is null and E.UserId is null)
then 'HistoricalFailure_System'
when (H.TimeGap>24 and E.UserId!=H.OwnerId)
then 'HistoricalFailure_OutofFTSscope'
when (H.TimeGap>24 and d.UserId is not null)
then 'HistoricalFailure_OutofFTSscope'
else null end as DoneType,
case when (Q.ActionType=3 and H.OwnerId!=0)
then 1
when (Q.ActionType in ('7','8') and H.OwnerId=F.UserId )
then 1
else 0 end as DoneFailureByTaskOwner,
case when Q.ActionType=3 
then Q.FailureActionUser
when Q.ActionType in ('7','8') 
then F.UserId
else 0 end as DoneFailureUser,
case when Q.ActionType=3 
then y.Email
when Q.ActionType in ('7','8') 
then yy.Email
else null end as DoneFailureUserName

from GenerateList H
left join 
(select G.DeliveryId,G.FileId,G.InvestmentId,G.EffectiveDate,G.ValidationCodeId,G.ActionType,G.ActionTime,G.FailureActionUser
from ActionList G where G.ActionType is not null) Q
on (Q.DeliveryId=H.DeliveryId and Q.FileId=H.FileId and Q.InvestmentId=H.InvestmentId 
and Q.EffectiveDate=H.EffectiveDate and Q.ValidationCodeId=H.ValidationCodeId)
left join 
(select FileId,UserId from [LogData_GPMainDB].[dbo].[FileSourceTracking] e with(nolock) 
where e.ActionType=5
and e.UserId!=10739
and e.ActionTime<getdate()
and e.ActionTime>dateadd(DD,-1,getdate())) E 
on E.FileId=H.FileId
left join 
(select InvestmentId,EffectiveDate,UserId,ActionTime from LogData_GPMainDB.dbo.PerformanceTimeSeriesDataSourceTracking f with(nolock) 
where f.DataUnit in ('101','105','108')
and f.UserId!=10739
and f.ActionType between 7 and 8 
and f.ActionTime<getdate()
and f.ActionTime>dateadd(DD,-1,getdate())) F
on (F.InvestmentId=H.InvestmentId and F.EffectiveDate=H.EffectiveDate)
left join 
(select FileId,UserId from [LogData_GPMainDB].[dbo].[FileSourceTracking] D with(nolock)
where D.ActionType=3
and D.UserId!=10739
and D.ActionTime<getdate()
and D.ActionTime>dateadd(DD,-1,getdate())) d
on d.FileId=H.FileId
left join SupportData_DMWkspaceDB.dbo.UserSearch y on y.UserId=H.OwnerId
left join SupportData_DMWkspaceDB.dbo.UserSearch yy on yy.UserId=F.UserId
'''


# In[8]:


connection.autocommit = True


result1 = cursor.execute(sql_code).fetchall()
pdresult1 = pd.read_sql(sql_code,connection)



with tqdm_notebook(total=100) as pbar:
    pbar.update(30) 



end = time.time()
n = end - start
n = int(n)
try:
    if n < 60: 
        print("SQl 一共需要跑 %s 秒 " % (n))

    else: 
        print("SQl 一共需要跑 %s 分钟 " % (n/60))
except:

    print("SQl 一共需要跑 %s  " % (n))


#-------------------------------------------------------------------------------------
with tqdm_notebook(total=100) as pbar:
    pbar.update(50) 

time.sleep(3)

df = DataFrame(pdresult1)


# In[39]:


def get_updated_raw_data():
    history = pd.read_csv(r"\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Price failure\price failure 3M.csv")
    print("History Data loading done")
    updated = pd.concat([df,history],axis = 0)
    print("Total have %d records" % (updated.shape[0]))
    updated = updated.drop_duplicates(keep='first', inplace=False)
    print("Drop Duplicate Done, Now have %d records and try to Save updated file"% (updated.shape[0]))
    
    return updated.to_csv(r"\\szmsfs03\Shared\Global Fund\Public folder\Performance & VA & ETF sharing\Performance AI Study Group\Price failure\price failure 3M with ongoing.csv",index = False)


