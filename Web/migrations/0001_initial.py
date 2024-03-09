# Generated by Django 5.0.2 on 2024-03-09 09:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issue', models.CharField(max_length=1000)),
                ('choice_type', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='MultipleChoice',
            fields=[
                ('question', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='Web.question')),
            ],
        ),
        migrations.CreateModel(
            name='SingleChoice',
            fields=[
                ('question', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='Web.question')),
                ('correct_answer', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=2000)),
                ('is_published', models.BooleanField(default=False)),
                ('created_at', models.DateField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='question',
            name='test',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Web.test'),
        ),
        migrations.CreateModel(
            name='MultipleChoiceAnswers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=100)),
                ('is_correct', models.BooleanField()),
                ('multiple_choice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Web.multiplechoice')),
            ],
        ),
        migrations.CreateModel(
            name='SingleChoiceAnswers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=100)),
                ('single_choice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Web.singlechoice')),
            ],
        ),
    ]
