from django.db import migrations, models


def delete_users_without_phone(apps, schema_editor):
    """Delete users with blank or null phone — ORM handles FK cascades."""
    User = apps.get_model('accounts', 'User')
    User.objects.filter(phone__isnull=True).delete()
    User.objects.filter(phone='').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_pin_hash'),
    ]

    operations = [
        # Step 1: delete users with no phone via ORM (respects CASCADE/SET_NULL)
        migrations.RunPython(delete_users_without_phone, migrations.RunPython.noop),
        # Step 2: now safe to add unique constraint — no duplicates remain
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(max_length=20, unique=True, blank=True, null=True, default=None),
        ),
    ]
