# Generated by Django 2.2.6 on 2019-11-07 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0003_auto_20191107_1859'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacancy',
            name='company',
            field=models.CharField(blank=True, default='Company', max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='vacancy',
            name='name',
            field=models.CharField(blank=True, default='Worker', max_length=128, null=True),
        ),
    ]