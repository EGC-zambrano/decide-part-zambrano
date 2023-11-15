from base.models import BigBigField
from django.db import models


class Vote(models.Model):
    voting_id = models.PositiveIntegerField()
    voter_id = models.PositiveIntegerField()

    voted = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}: {}".format(self.voting_id, self.voter_id)


class VoteOption(models.Model):
    vote = models.ForeignKey(Vote, related_name="options", on_delete=models.CASCADE)
    a = BigBigField()
    b = BigBigField()
