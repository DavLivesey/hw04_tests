# Generated by Django 2.2.9 on 2020-08-03 10:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_auto_20200721_1707'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(
                blank=True, help_text='Можете не выбирать',
                null=True, on_delete=django.db.models.deletion.SET_NULL,
                related_name='posts',
                to='posts.Group',
                verbose_name='Выберите тему'
                ),
        ),
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(
                help_text='Чем хотите поделиться?',
                verbose_name='Введите текст'
                ),
        ),
    ]