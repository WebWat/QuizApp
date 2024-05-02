# Generated by Django 5.0.2 on 2024-05-01 10:32

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Web', '0015_alter_singlechoiceresult_chose_alter_test_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='singlechoice',
            name='correct_answer',
            field=models.IntegerField(default=-1),
        ),
        migrations.AlterField(
            model_name='test',
            name='created_at',
            field=models.DateField(default=datetime.date(2024, 5, 1)),
        ),
        migrations.AlterField(
            model_name='test',
            name='description',
            field=models.CharField(default='', max_length=2000),
        ),
        migrations.AlterField(
            model_name='test',
            name='published_at',
            field=models.DateField(default=datetime.date(2024, 5, 1)),
        ),
        migrations.AlterField(
            model_name='test',
            name='title',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AlterField(
            model_name='useranswers',
            name='finished_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 1, 13, 32, 53, 100359)),
        ),
    ]