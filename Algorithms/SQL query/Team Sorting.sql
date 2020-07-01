/*
Teams table:
+-----------+--------------+
| team_id   | team_name    |
+-----------+--------------+
| 10        | Leetcode FC  |
| 20        | NewYork FC   |
| 30        | Atlanta FC   |
| 40        | Chicago FC   |
| 50        | Toronto FC   |
+-----------+--------------+

Matches table:
+------------+--------------+---------------+-------------+--------------+
| match_id   | host_team    | guest_team    | host_goals  | guest_goals  |
+------------+--------------+---------------+-------------+--------------+
| 1          | 10           | 20            | 3           | 0            |
| 2          | 30           | 10            | 2           | 2            |
| 3          | 10           | 50            | 5           | 1            |
| 4          | 20           | 30            | 1           | 0            |
| 5          | 50           | 30            | 1           | 0            |
+------------+--------------+---------------+-------------+--------------+

Result table:
+------------+--------------+---------------+
| team_id    | team_name    | num_points    |
+------------+--------------+---------------+
| 10         | Leetcode FC  | 7             |
| 20         | NewYork FC   | 3             |
| 50         | Toronto FC   | 3             |
| 30         | Atlanta FC   | 1             |
| 40         | Chicago FC   | 0             |
+------------+--------------+---------------+

*/

Create table If Not Exists Teams (team_id int, team_name varchar(30))
Create table If Not Exists Matches (match_id int, host_team int, guest_team int, host_goals int, guest_goals int)
Truncate table Teams
insert into Teams (team_id, team_name) values ('10', 'Leetcode FC')
insert into Teams (team_id, team_name) values ('20', 'NewYork FC')
insert into Teams (team_id, team_name) values ('30', 'Atlanta FC')
insert into Teams (team_id, team_name) values ('40', 'Chicago FC')
insert into Teams (team_id, team_name) values ('50', 'Toronto FC')
Truncate table Matches
insert into Matches (match_id, host_team, guest_team, host_goals, guest_goals) values ('1', '10', '20', '30', '0')
insert into Matches (match_id, host_team, guest_team, host_goals, guest_goals) values ('2', '30', '10', '2', '2')
insert into Matches (match_id, host_team, guest_team, host_goals, guest_goals) values ('3', '10', '50', '5', '1')
insert into Matches (match_id, host_team, guest_team, host_goals, guest_goals) values ('4', '20', '30', '1', '0')
insert into Matches (match_id, host_team, guest_team, host_goals, guest_goals) values ('5', '50', '30', '1', '0')

#solution

select 
t.team_id,
t.team_name,
sum(case when t.team_id = m1.host_team and m1.host_goals > m1.guest_goals then 3 
        when m1.host_goals = m1.guest_goals then 1 
        when  t.team_id = m1.guest_team and m1.guest_goals>m1.host_goals THEN 3 ELSE 0 END) 
        `num_points` 
        
from Teams t 
left join Matches m1 on t.team_id = m1.host_team or t.team_id = m1.guest_team 
group by t.team_id order by num_points desc,team_id asc