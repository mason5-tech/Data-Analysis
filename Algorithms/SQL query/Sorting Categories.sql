/*
Scores:
+-------------+--------+------------+--------------+
| player_name | gender | day        | score_points |
+-------------+--------+------------+--------------+
| Aron        | F      | 2020-01-01 | 17           |
| Alice       | F      | 2020-01-07 | 23           |
| Bajrang     | M      | 2020-01-07 | 7            |
| Khali       | M      | 2019-12-25 | 11           |
| Slaman      | M      | 2019-12-30 | 13           |
| Joe         | M      | 2019-12-31 | 3            |
| Jose        | M      | 2019-12-18 | 2            |
| Priya       | F      | 2019-12-31 | 23           |
| Priyanka    | F      | 2019-12-30 | 17           |
+-------------+--------+------------+--------------+
Result:
+--------+------------+-------+
| gender | day        | total |
+--------+------------+-------+
| F      | 2019-12-30 | 17    |
| F      | 2019-12-31 | 40    |
| F      | 2020-01-01 | 57    |
| F      | 2020-01-07 | 80    |
| M      | 2019-12-18 | 2     |
| M      | 2019-12-25 | 13    |
| M      | 2019-12-30 | 26    |
| M      | 2019-12-31 | 29    |
| M      | 2020-01-07 | 36    |
+--------+------------+-------+

*/

Create table If Not Exists Scores (player_name varchar(20), gender varchar(1), day date, score_points int)
Truncate table Scores
insert into Scores (player_name, gender, day, score_points) values ('Aron', 'F', '2020-01-01', '17')
insert into Scores (player_name, gender, day, score_points) values ('Alice', 'F', '2020-01-07', '23')
insert into Scores (player_name, gender, day, score_points) values ('Bajrang', 'M', '2020-01-07', '7')
insert into Scores (player_name, gender, day, score_points) values ('Khali', 'M', '2019-12-25', '11')
insert into Scores (player_name, gender, day, score_points) values ('Slaman', 'M', '2019-12-30', '13')
insert into Scores (player_name, gender, day, score_points) values ('Joe', 'M', '2019-12-31', '3')
insert into Scores (player_name, gender, day, score_points) values ('Jose', 'M', '2019-12-18', '2')
insert into Scores (player_name, gender, day, score_points) values ('Priya', 'F', '2019-12-31', '23')
insert into Scores (player_name, gender, day, score_points) values ('Priyanka', 'F', '2019-12-30', '17')

#solution


select s.gender,s.day,sum(s1.score_points) total
from Scores s
left join scores s1
on s.day>=s1.day and s.gender=s1.gender
group by s.gender,s.day
order by s.gender asc,s.day asc
