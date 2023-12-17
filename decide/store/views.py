import django_filters.rest_framework
from base import mods
from base.perms import UserIsStaff
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import generics, status
from rest_framework.response import Response

from .models import Vote, VoteOption
from .serializers import VoteSerializer


class StoreView(generics.ListAPIView):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_fields = ("voting_id", "voter_id")

    def get(self, request):
        self.permission_classes = (UserIsStaff,)
        self.check_permissions(request)
        return super().get(request)

    def post(self, request):
        """
        * voting: id
        * voter: id
        * vote: { "a": int, "b": int } or [ { "a": int, "b": int }, ...}]
        """

        vid = request.data.get("voting")
        voting = mods.get("voting", params={"id": vid})
        if not voting or not isinstance(voting, list):
            # print("por aqui 35")
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)
        start_date = voting[0].get("start_date", None)
        # print ("Start date: "+  start_date)
        end_date = voting[0].get("end_date", None)
        # print ("End date: ", end_date)
        not_started = not start_date or timezone.now() < parse_datetime(start_date)
        # print (not_started)
        is_closed = end_date and parse_datetime(end_date) < timezone.now()
        if not_started or is_closed:
            # print("por aqui 42")
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)

        uid = request.data.get("voter")
        vote = request.data.get("vote")

        if (
            voting[0]["question"]["question_type"] == "M"
            or voting[0]["question"]["question_type"] == "P"
        ) and not isinstance(vote, list):
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        if not vid or not uid or not vote:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        # validating voter
        if request.auth:
            token = request.auth.key
        else:
            token = "NO-AUTH-VOTE"
        voter = mods.post(
            "authentication", entry_point="/getuser/", json={"token": token}
        )
        voter_id = voter.get("id", None)
        if not voter_id or voter_id != uid:
            # print("por aqui 59")
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)

        # the user is in the census
        perms = mods.get(
            "census/{}".format(vid), params={"voter_id": uid}, response=True
        )
        if perms.status_code == 401:
            # print("por aqui 65")
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)

        with transaction.atomic():
            if voting[0]["question"]["question_type"] == "S":
                v, _ = Vote.objects.get_or_create(voting_id=vid, voter_id=uid)
                # Delete previous options
                VoteOption.objects.filter(vote=v).delete()

                a = vote.get("a")
                b = vote.get("b")

                vote_option = VoteOption(vote=v)
                vote_option.a = a
                vote_option.b = b

                vote_option.save()
                v.save()

            elif voting[0]["question"]["question_type"] == "M":
                v, _ = Vote.objects.get_or_create(voting_id=vid, voter_id=uid)
                # Delete previous options
                VoteOption.objects.filter(vote=v).delete()
                for option in vote:
                    a = option.get("a")
                    b = option.get("b")

                    vote_option = VoteOption(vote=v)
                    vote_option.a = a
                    vote_option.b = b

                    vote_option.save()
                v.save()
            elif voting[0]["question"]["question_type"] == "P":
                v, _ = Vote.objects.get_or_create(voting_id=vid, voter_id=uid)
                # Delete previous options
                VoteOption.objects.filter(vote=v).delete()
                for option in vote:
                    a = option.get("a")
                    b = option.get("b")
                    p = option.get("p")

                    vote_option = VoteOption(vote=v)
                    vote_option.a = a
                    vote_option.b = b
                    vote_option.p = p

                    vote_option.save()
                v.save()

        return Response({})
