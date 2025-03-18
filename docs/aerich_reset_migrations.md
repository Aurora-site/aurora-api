# How to reset migrations

```bash
rm -rf migrations/models
```

run sql

```sql
drop table aerich;
```

run only from wsl / linux

```bash
aerich init-db
aerich migrate
```
