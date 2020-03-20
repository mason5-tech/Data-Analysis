select distinct a.FileId,b.DeliveryId,a.InvestmentId,a.DataUnit,b.ZoneId,a.ValidationCodeId,a.ActionType,a.UserId as ActionUserID,b.DeliveryId,b.GeneratedTime as FailureTaskGeneratedTime,b.EndDate as TaskDoneTime,b.OwnerId as Taskowner ,c.Email as TaskownerUserName,e.UserId as FileUserID,case when e.ActionType = 3 or e.ActionType =5
then 'outofscope' end as FailureGenerationType,
case
when ((DATEPART(WEEKDAY,b.GeneratedTime)-1) = '5' and CONVERT(varchar,b.GeneratedTime, 24) >= '18:30:00') then 'weekend'
when ((DATEPART(WEEKDAY,b.GeneratedTime)-1) = '6') then 'weekend'
when ((DATEPART(WEEKDAY,b.GeneratedTime)-1) = '0' and CONVERT(varchar,b.GeneratedTime, 24) < '18:30:00') then 'weekend'
else 'weekday' end  as workday
from [LogData_GPMainDB].[dbo].[PerformanceFailureDataSourceTracking] a with (NOLOCK)
join [StatusData_DMPERFORMDB].[dbo].[DashBoardTask] b on a.FileId=b.FileId
left join SupportData_DMWkspaceDB.dbo.UserSearch c on c.UserId=b.OwnerId
left join StatusData_DMWkspaceDB.dbo.PerformanceFileStatus d on a.FileId=d.FileId
left join LogData_GPMainDB.dbo.FileSourceTracking e on a.FileId=e.FileId
where
a.DataUnit in ('101','105','108')
and b.GeneratedTime>='2019-01-01'
and b.GeneratedTime<'2020-01-03'
and a.ActionType = 1
and ReportType = 1
and e.UserId != 10739
and (e.ActionType = 3 or e.ActionType =5)
and e.UserId != b.OwnerId
order by b.GeneratedTime