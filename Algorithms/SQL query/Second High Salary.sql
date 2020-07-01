/*
Employee Table:

+----+--------+
| Id | Salary |
+----+--------+
| 1  | 100    |
| 2  | 200    |
| 3  | 300    |
+----+--------+

Result Table:

+---------------------+
| SecondHighestSalary |
+---------------------+
| 200                 |
+---------------------+

*/

Create table If Not Exists Employee (Id int, Salary int)
Truncate table Employee
insert into Employee (Id, Salary) values ('1', '100')
insert into Employee (Id, Salary) values ('2', '200')
insert into Employee (Id, Salary) values ('3', '300')

#solution

select 
(select distinct Salary
from Employee
order by Salary DESC
limit 1 offset 1) as SecondHighestSalary