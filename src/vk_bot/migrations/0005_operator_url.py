# Generated by Django 4.0.5 on 2022-07-09 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vk_bot', '0004_alter_operator_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='operator',
            name='url',
            field=models.TextField(blank=True),
        ),
    ]
