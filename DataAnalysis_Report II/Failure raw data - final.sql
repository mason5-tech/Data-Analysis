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