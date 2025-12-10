# Database Migration Scripts

## Adding New User Fields

This migration adds the following columns to the `users` table:
- `first_name` VARCHAR(255)
- `last_name` VARCHAR(255)
- `dob` DATE
- `mobile` VARCHAR(20)
- Updates `profile_image` from VARCHAR(225) to VARCHAR(500)

✅ **Code Updated**: All code has been updated to use `mobile` as the column name.

## How to Run

### Option 1: Using MySQL Command Line
```bash
mysql -u root -p test < migrations/add_user_fields.sql
```

### Option 2: Using MySQL Client
1. Connect to your MySQL database:
   ```bash
   mysql -u root -p
   ```
2. Select the database:
   ```sql
   USE test;
   ```
3. Run the migration:
   ```sql
   SOURCE backend/migrations/add_user_fields.sql;
   ```

### Option 3: Using phpMyAdmin or MySQL Workbench
1. Open phpMyAdmin or MySQL Workbench
2. Select the `test` database
3. Go to SQL tab
4. Copy and paste the contents of `add_user_fields.sql`
5. Execute the script

### Option 4: Manual Migration (if IF NOT EXISTS doesn't work)
If your MySQL version doesn't support `IF NOT EXISTS` in `ALTER TABLE`, use:
```bash
mysql -u root -p test < migrations/add_user_fields_manual.sql
```

## Important Notes

✅ **Code Updated**: All code has been updated to use `mobile` as specified. Use `add_user_fields_mobile.sql` for the migration.

The following files have been updated to use `mobile`:
- `backend/models/user.py`
- `backend/schemas/user.py`
- `backend/routes/user.py`
- `ui/src/app/pages/profile/profile.html`
- `ui/src/app/pages/update/update.ts`
- `admin-ui/src/app/pages/admin-dashboard/admin-dashboard.ts`
- `admin-ui/src/app/pages/admin-dashboard/admin-dashboard.html`

## Verification

After running the migration, verify the columns were added:
```sql
DESCRIBE users;
```

You should see the new columns:
- first_name
- last_name
- dob
- mobile
- profile_image (with size 500)

