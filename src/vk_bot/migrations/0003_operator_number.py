# Generated by Django 4.0.5 on 2022-07-09 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vk_bot', '0002_operator'),
    ]

    operations = [
        migrations.AddField(
            model_name='operator',
            name='number',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
    ]
