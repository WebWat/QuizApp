# Generated by Django 5.0.2 on 2024-03-09 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Web', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='multiplechoiceanswers',
            name='is_correct',
            field=models.BooleanField(default=False),
        ),
    ]