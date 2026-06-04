from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_pin_hash'),
    ]

    operations = [
        # Step 1: allow null so existing rows with blank phones don't conflict
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(max_length=20, unique=True, blank=True, null=True, default=None),
        ),
        # Step 2: delete users with no phone (can't send/receive money anyway)
        migrations.RunSQL(
            "DELETE FROM accounts_user WHERE phone IS NULL OR phone = '';",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
