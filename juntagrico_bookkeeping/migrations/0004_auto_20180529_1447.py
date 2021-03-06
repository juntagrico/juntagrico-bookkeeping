# Generated by Django 2.0.2 on 2018-05-29 12:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('juntagrico_bookkeeping', '0003_settings'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExtraSubscriptionCategoryAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.CharField(max_length=100, verbose_name='Konto')),
                ('extrasubcategory', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='extrasub_account', to='juntagrico.ExtraSubscriptionCategory')),
            ],
        ),
        migrations.AlterModelOptions(
            name='settings',
            options={'verbose_name_plural': 'Settings'},
        ),
    ]
