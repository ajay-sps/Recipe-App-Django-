# Generated by Django 4.2.2 on 2023-08-14 05:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_roles_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roles',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
