from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0003_phone_required_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='SsoPin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sub', models.CharField(max_length=255, unique=True)),
            ],
            options={'db_table': 'accounts_sso_pin'},
        ),
    ]
