# Generated by Django 4.1 on 2023-12-12 16:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('voting', '0006_remove_questionoption_question_type_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Opinion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('voting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='opinions', to='voting.voting')),
            ],
        ),
    ]
