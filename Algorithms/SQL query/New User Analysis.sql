/*
Traffic Table：
+---------+----------+---------------+
| user_id | activity | activity_date |
+---------+----------+---------------+
| 1       | login    | 2019-05-01    |
| 1       | homepage | 2019-05-01    |
| 1       | logout   | 2019-05-01    |
| 2       | login    | 2019-06-21    |
| 2       | logout   | 2019-06-21    |
| 3       | login    | 2019-01-01    |
| 3       | jobs     | 2019-01-01    |
| 3       | logout   | 2019-01-01    |
| 4       | login    | 2019-06-21    |
| 4       | groups   | 2019-06-21    |
| 4       | logout   | 2019-06-21    |
| 5       | login    | 2019-03-01    |
| 5       | logout   | 2019-03-01    |
| 5       | login    | 2019-06-21    |
| 5       | logout   | 2019-06-21    |
+---------+----------+---------------+

Result Table：
+------------+-------------+
| login_date | user_count  |
+------------+-------------+
| 2019-05-01 | 1           |
| 2019-06-21 | 2           |
+------------+-------------+

*/

Create table If Not Exists Traffic (user_id int, activity ENUM('login', 'logout', 'jobs', 'groups', 'homepage'), activity_date date)
Truncate table Traffic
insert into Traffic (user_id, activity, activity_date) values ('1', 'login', '2019-05-01')
insert into Traffic (user_id, activity, activity_date) values ('1', 'homepage', '2019-05-01')
insert into Traffic (user_id, activity, activity_date) values ('1', 'logout', '2019-05-01')
insert into Traffic (user_id, activity, activity_date) values ('2', 'login', '2019-06-21')
insert into Traffic (user_id, activity, activity_date) values ('2', 'logout', '2019-06-21')
insert into Traffic (user_id, activity, activity_date) values ('3', 'login', '2019-01-01')
insert into Traffic (user_id, activity, activity_date) values ('3', 'jobs', '2019-01-01')
insert into Traffic (user_id, activity, activity_date) values ('3', 'logout', '2019-01-01')
insert into Traffic (user_id, activity, activity_date) values ('4', 'login', '2019-06-21')
insert into Traffic (user_id, activity, activity_date) values ('4', 'groups', '2019-06-21')
insert into Traffic (user_id, activity, activity_date) values ('4', 'logout', '2019-06-21')
insert into Traffic (user_id, activity, activity_date) values ('5', 'login', '2019-03-01')
insert into Traffic (user_id, activity, activity_date) values ('5', 'logout', '2019-03-01')
insert into Traffic (user_id, activity, activity_date) values ('5', 'login', '2019-06-21')
insert into Traffic (user_id, activity, activity_date) values ('5', 'logout', '2019-06-21')

#solution

select login_date, count(user_id) as user_count

from
(
select min(activity_date) as login_date, user_id

from Traffic

WHERE activity = 'login'

group by user_id
) t

where datediff('2019-06-30',login_date) <= 90

GROUP BY login_date