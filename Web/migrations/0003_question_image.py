# Generated by Django 5.0.2 on 2024-04-14 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Web', '0002_useranswers_correct_answer_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='image',
            field=models.ImageField(blank=True, upload_to='images'),
        ),
    ]
