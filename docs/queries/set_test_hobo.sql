-- SQLite
update customers as c
set hobo = 1, hobo_at = datetime('now', '-8 days')
where c.id = 2;

update customers as c
set hobo = 1, hobo_at = datetime('now', '-5 days')
where c.id = 3;

select * from customers c
where c.hobo = 1
    and c.hobo_at < datetime('now', '-7 days');

select * from customers c
    join cities ct on c.city_id = ct.id
    left join subscriptions s on s.cust_id = c.id
;
