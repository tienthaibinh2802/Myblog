This project is a basic blog built with Django and Tailwind CSS.

## Production database

To avoid losing data after deploy, use PostgreSQL in production instead of `sqlite3`.

1. Create a PostgreSQL database on your hosting provider.
2. Set the `DATABASE_URL` environment variable.
3. Deploy the app.
4. Run migrations.

Example `DATABASE_URL`:

```env
DATABASE_URL=postgres://USER:PASSWORD@HOST:5432/DBNAME
```

Local development still falls back to `db.sqlite3` if `DATABASE_URL` is not set.
