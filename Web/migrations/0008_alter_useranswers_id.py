# Generated by Django 5.0.2 on 2024-03-23 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Web', '0007_questionresult_question_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useranswers',
            name='id',
            field=models.CharField(max_length=32, primary_key=True, serialize=False),
        ),
    ]
