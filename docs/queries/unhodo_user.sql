-- SQLite
update customers as c
set hobo = 0, updated_at = datetime('now')
where c.id = 1;

select * from customers c
where c.id = 1;
