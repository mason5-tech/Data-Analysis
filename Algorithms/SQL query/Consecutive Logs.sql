/*

Logs Table:

+----+-----+
| Id | Num |
+----+-----+
| 1  |  1  |
| 2  |  1  |
| 3  |  1  |
| 4  |  2  |
| 5  |  1  |
| 6  |  2  |
| 7  |  2  |
+----+-----+

Result:

+-----------------+
| ConsecutiveNums |
+-----------------+
| 1               |
+-----------------+

*/

Create table If Not Exists Logs (Id int, Num int)
Truncate table Logs
insert into Logs (Id, Num) values ('1', '1')
insert into Logs (Id, Num) values ('2', '1')
insert into Logs (Id, Num) values ('3', '1')
insert into Logs (Id, Num) values ('4', '2')
insert into Logs (Id, Num) values ('5', '1')
insert into Logs (Id, Num) values ('6', '2')
insert into Logs (Id, Num) values ('7', '2')

select
    distinct l1.Num as ConsecutiveNums

from 
    Logs l1,
    Logs l2,
    Logs l3

where
    l1.id = l2.id - 1
    AND l2.id = l3.id - 1
    AND l1.Num = l2.Num
    AND l2.Num = l3.Num