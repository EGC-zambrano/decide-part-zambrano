import datetime
import random

from base import mods
from base.models import Auth
from base.tests import BaseTestCase
from census.models import Census
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from mixnet.models import Key
from rest_framework.test import APIClient, APITestCase
from voting.models import Question, Voting

from .models import Vote
from .serializers import VoteSerializer


class StoreTextCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.question = Question(desc="qwerty")
        self.question.save()
        self.voting = Voting(
            pk=5001,
            name="voting example",
            question=self.question,
            start_date=timezone.now(),
        )
        self.voting.save()

    def tearDown(self):
        super().tearDown()

    def gen_voting_single(self, pk):
        voting = Voting(
            pk=pk,
            name="v1",
            question=self.question,
            start_date=timezone.now(),
            end_date=timezone.now() + datetime.timedelta(days=1),
        )
        voting.save()

    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = "user{}".format(pk)
        user.set_password("qwerty")
        user.save()
        return user

    def gen_votes_single(self):
        votings = [random.randint(1, 5000) for i in range(10)]
        users = [random.randint(3, 5002) for i in range(50)]
        for v in votings:
            a = random.randint(2, 500)
            b = random.randint(2, 500)
            self.gen_voting_single(v)
            random_user = random.choice(users)
            user = self.get_or_create_user(random_user)
            self.login(user=user.username)
            census = Census(voting_id=v, voter_id=random_user)
            census.save()
            data = {"voting": v, "voter": random_user, "vote": {"a": a, "b": b}}
            response = self.client.post("/store/", data, format="json")
            self.assertEqual(response.status_code, 200)

        self.logout()
        return votings, users

    def gen_voting_multiple_options(self, pk):
        question = Question(desc="multiple_options_question", question_type="M")
        question.save()
        voting = Voting(
            pk=pk,
            name="voting_multiple_options",
            question=question,
            start_date=timezone.now(),
            end_date=timezone.now() + datetime.timedelta(days=1),
        )
        voting.save()

    def test_gen_vote_invalid_single(self):
        data = {"voting": 1, "voter": 1, "vote": {"a": 1, "b": 1}}
        response = self.client.post("/store/", data, format="json")
        self.assertEqual(response.status_code, 401)

    def test_store_vote_single(self):
        VOTING_PK = 345
        CTE_A = 96
        CTE_B = 184
        census = Census(voting_id=VOTING_PK, voter_id=1)
        census.save()
        self.gen_voting_single(VOTING_PK)
        data = {"voting": VOTING_PK, "voter": 1, "vote": {"a": CTE_A, "b": CTE_B}}
        user = self.get_or_create_user(1)
        self.login(user=user.username)
        response = self.client.post("/store/", data, format="json")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.first().voting_id, VOTING_PK)
        self.assertEqual(Vote.objects.first().voter_id, 1)
        self.assertEqual(Vote.objects.first().options.count(), 1)
        self.assertEqual(Vote.objects.first().options.first().a, CTE_A)
        self.assertEqual(Vote.objects.first().options.first().b, CTE_B)

    def test_store_vote_multiple_options(self):
        VOTING_PK = 346
        census = Census(voting_id=VOTING_PK, voter_id=2)
        census.save()
        self.gen_voting_multiple_options(VOTING_PK)
        data = {
            "voting": VOTING_PK,
            "voter": 2,
            "vote": [{"a": 20, "b": 30}, {"a": 40, "b": 50}, {"a": 60, "b": 70}],
        }
        user = self.get_or_create_user(2)
        self.login(user=user.username)
        response = self.client.post("/store/", data, format="json")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.first().voting_id, VOTING_PK)
        self.assertEqual(Vote.objects.first().voter_id, 2)
        self.assertEqual(Vote.objects.first().options.count(), 3)

        # Validate the options
        options = Vote.objects.first().options.all()
        self.assertEqual(options[0].a, 20)
        self.assertEqual(options[0].b, 30)
        self.assertEqual(options[1].a, 40)
        self.assertEqual(options[1].b, 50)
        self.assertEqual(options[2].a, 60)
        self.assertEqual(options[2].b, 70)

    def test_vote(self):
        self.gen_votes_single()
        response = self.client.get("/store/", format="json")
        self.assertEqual(response.status_code, 401)

        self.login(user="noadmin")
        response = self.client.get("/store/", format="json")
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.get("/store/", format="json")
        self.assertEqual(response.status_code, 200)
        votes = response.json()

        self.assertEqual(len(votes), Vote.objects.count())
        self.assertEqual(votes[0], VoteSerializer(Vote.objects.all().first()).data)

    def test_filter(self):
        votings, voters = self.gen_votes_single()
        v = votings[0]

        response = self.client.get("/store/?voting_id={}".format(v), format="json")
        self.assertEqual(response.status_code, 401)

        self.login(user="noadmin")
        response = self.client.get("/store/?voting_id={}".format(v), format="json")
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.get("/store/?voting_id={}".format(v), format="json")
        self.assertEqual(response.status_code, 200)
        votes = response.json()

        self.assertEqual(len(votes), Vote.objects.filter(voting_id=v).count())

        v = voters[0]
        response = self.client.get("/store/?voter_id={}".format(v), format="json")
        self.assertEqual(response.status_code, 200)
        votes = response.json()

        self.assertEqual(len(votes), Vote.objects.filter(voter_id=v).count())

    def test_hasvote(self):
        votings, voters = self.gen_votes_single()
        vo = Vote.objects.first()
        v = vo.voting_id
        u = vo.voter_id

        response = self.client.get(
            "/store/?voting_id={}&voter_id={}".format(v, u), format="json"
        )
        self.assertEqual(response.status_code, 401)

        self.login(user="noadmin")
        response = self.client.get(
            "/store/?voting_id={}&voter_id={}".format(v, u), format="json"
        )
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.get(
            "/store/?voting_id={}&voter_id={}".format(v, u), format="json"
        )
        self.assertEqual(response.status_code, 200)
        votes = response.json()

        self.assertEqual(len(votes), 1)
        self.assertEqual(votes[0]["voting_id"], v)
        self.assertEqual(votes[0]["voter_id"], u)

    def test_voting_status(self):
        data = {"voting": 5001, "voter": 1, "vote": {"a": 30, "b": 55}}
        census = Census(voting_id=5001, voter_id=1)
        census.save()
        # not opened
        self.voting.start_date = timezone.now() + datetime.timedelta(days=1)
        self.voting.save()
        user = self.get_or_create_user(1)
        self.login(user=user.username)
        response = self.client.post("/store/", data, format="json")
        self.assertEqual(response.status_code, 401)

        # not closed
        self.voting.start_date = timezone.now() - datetime.timedelta(days=1)
        self.voting.save()
        self.voting.end_date = timezone.now() + datetime.timedelta(days=1)
        self.voting.save()
        response = self.client.post("/store/", data, format="json")
        self.assertEqual(response.status_code, 200)

        # closed
        self.voting.end_date = timezone.now() - datetime.timedelta(days=1)
        self.voting.save()
        response = self.client.post("/store/", data, format="json")
        self.assertEqual(response.status_code, 401)
