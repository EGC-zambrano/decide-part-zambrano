# Generated by Django 4.1 on 2023-11-20 18:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("voting", "0009_remove_voting_blank_vote"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="voteBlank",
            field=models.BooleanField(default=False),
        ),
    ]