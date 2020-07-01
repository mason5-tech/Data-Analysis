/*
Transactions Table：
+------+---------+----------+--------+------------+
| id   | country | state    | amount | trans_date |
+------+---------+----------+--------+------------+
| 101  | US      | approved | 1000   | 2019-05-18 |
| 102  | US      | declined | 2000   | 2019-05-19 |
| 103  | US      | approved | 3000   | 2019-06-10 |
| 104  | US      | declined | 4000   | 2019-06-13 |
| 105  | US      | approved | 5000   | 2019-06-15 |
+------+---------+----------+--------+------------+

Chargebacks Table：
+------------+------------+
| trans_id   | trans_date |
+------------+------------+
| 102        | 2019-05-29 |
| 101        | 2019-06-30 |
| 105        | 2019-09-18 |
+------------+------------+

Result Table：
+----------+---------+----------------+-----------------+-------------------+--------------------+
| month    | country | approved_count | approved_amount | chargeback_count  | chargeback_amount  |
+----------+---------+----------------+-----------------+-------------------+--------------------+
| 2019-05  | US      | 1              | 1000            | 1                 | 2000               |
| 2019-06  | US      | 2              | 8000            | 1                 | 1000               |
| 2019-09  | US      | 0              | 0               | 1                 | 5000               |
+----------+---------+----------------+-----------------+-------------------+--------------------+

*/

create table if not exists Transactions (id int, country varchar(4), state enum('approved', 'declined'), amount int, trans_date date)
create table if not exists Chargebacks (trans_id int, trans_date date)
Truncate table Transactions
insert into Transactions (id, country, state, amount, trans_date) values ('101', 'US', 'approved', '1000', '2019-05-18')
insert into Transactions (id, country, state, amount, trans_date) values ('102', 'US', 'declined', '2000', '2019-05-19')
insert into Transactions (id, country, state, amount, trans_date) values ('103', 'US', 'approved', '3000', '2019-06-10')
insert into Transactions (id, country, state, amount, trans_date) values ('104', 'US', 'declined', '4000', '2019-06-13')
insert into Transactions (id, country, state, amount, trans_date) values ('105', 'US', 'approved', '5000', '2019-06-15')
Truncate table Chargebacks
insert into Chargebacks (trans_id, trans_date) values ('102', '2019-05-29')
insert into Chargebacks (trans_id, trans_date) values ('101', '2019-06-30')
insert into Chargebacks (trans_id, trans_date) values ('105', '2019-09-18')

#solution

select Date_Format(trans_date, '%Y-%m') 'month', country, 
Count(case `state` when 'approved' then 1 else Null end) approved_count, 
Sum(if(state='approved',amount,0)) approved_amount,
Count(if(state='chargeback',1,Null)) chargeback_count,
Sum(if(state='chargeback',amount,0)) chargeback_amount
from (
select id, country,state,amount,trans_date from Transactions
union
select t.id, t.country,'chargeback' state,t.amount,c.trans_date from Transactions t
right join Chargebacks c on t.id = c.trans_id
) t
group by 1,2

having chargeback_count + approved_count >= 1

