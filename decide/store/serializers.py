from rest_framework import serializers

from .models import Vote, VoteOption


class VoteOptionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = VoteOption
        fields = ("a", "b")


class VoteSerializer(serializers.HyperlinkedModelSerializer):
    options = VoteOptionSerializer(many=True)

    class Meta:
        model = Vote
        fields = ("voting_id", "voter_id", "options")
