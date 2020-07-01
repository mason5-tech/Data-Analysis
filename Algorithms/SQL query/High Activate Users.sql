\*
Accounts Table:
+----+----------+
| id | name     |
+----+----------+
| 1  | Winston  |
| 7  | Jonathan |
+----+----------+

Logins Table:
+----+------------+
| id | login_date |
+----+------------+
| 7  | 2020-05-30 |
| 1  | 2020-05-30 |
| 7  | 2020-05-31 |
| 7  | 2020-06-01 |
| 7  | 2020-06-02 |
| 7  | 2020-06-02 |
| 7  | 2020-06-03 |
| 1  | 2020-06-07 |
| 7  | 2020-06-10 |
+----+------------+

Result Table:
+----+----------+
| id | name     |
+----+----------+
| 7  | Jonathan |
+----+----------+

*/

Create table If Not Exists Accounts (id int, name varchar(10))
Create table If Not Exists Logins (id int, login_date date)
Truncate table Accounts
insert into Accounts (id, name) values ('1', 'Winston')
insert into Accounts (id, name) values ('7', 'Jonathan')
Truncate table Logins
insert into Logins (id, login_date) values ('7', '2020-05-30')
insert into Logins (id, login_date) values ('1', '2020-05-30')
insert into Logins (id, login_date) values ('7', '2020-05-31')
insert into Logins (id, login_date) values ('7', '2020-06-01')
insert into Logins (id, login_date) values ('7', '2020-06-02')
insert into Logins (id, login_date) values ('7', '2020-06-02')
insert into Logins (id, login_date) values ('7', '2020-06-03')
insert into Logins (id, login_date) values ('1', '2020-06-07')
insert into Logins (id, login_date) values ('7', '2020-06-10')

#solution

select 
        id,
        Case
            When @id = id AND @pre=subdate(login_date,interval 1 day) AND (@pre := login_date) then @ak := @ak + 1
            When @id = id AND @pre=subdate(login_date,interval 0 day) then @ak := @ak
            WHEN (@id := id)IS NOT NULL AND (@pre := login_date) IS NOT NULL THEN @ak:=1
            end as ak

    from
    (select * from logins order by id, login_date) c,
    (select @pre:= Null, @ID:=Null,@ak:=1) t