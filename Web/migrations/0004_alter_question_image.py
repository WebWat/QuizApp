# Generated by Django 5.0.2 on 2024-04-14 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Web', '0003_question_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='image',
            field=models.ImageField(blank=True, upload_to=''),
        ),
    ]
