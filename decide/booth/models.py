from django.db import models

from voting.models import Voting


class Opinion(models.Model):
    voting = models.ForeignKey(
        Voting, related_name="opinions", on_delete=models.CASCADE
    )
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
