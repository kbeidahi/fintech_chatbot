from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Make phone unique and nullable.
    All SQL is idempotent — safe to run multiple times even if partially applied.
    SeparateDatabaseAndState is used so Django's ORM state is updated without
    re-running DDL that may already exist in the database.
    """
    atomic = False

    dependencies = [
        ('accounts', '0002_user_pin_hash'),
    ]

    operations = [
        # 1. Delete users with no phone (idempotent)
        migrations.RunSQL(
            "DELETE FROM accounts_user WHERE phone IS NULL OR phone = '';",
            reverse_sql=migrations.RunSQL.noop,
        ),
        # 2. Allow NULL on phone column (idempotent — no error if already nullable)
        migrations.RunSQL(
            "ALTER TABLE accounts_user ALTER COLUMN phone DROP NOT NULL;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        # 3. Drop old unique constraint if it exists
        migrations.RunSQL(
            "ALTER TABLE accounts_user DROP CONSTRAINT IF EXISTS accounts_user_phone_key;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        # 4. Create partial unique index (IF NOT EXISTS = idempotent)
        migrations.RunSQL(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS accounts_user_phone_uniq
            ON accounts_user (phone)
            WHERE phone IS NOT NULL;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # 5. Update Django ORM state only — no DB changes (DDL already done above)
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name='user',
                    name='phone',
                    field=models.CharField(max_length=20, unique=True, blank=True, null=True, default=None),
                ),
            ],
        ),
    ]
