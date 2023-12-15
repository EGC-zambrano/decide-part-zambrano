import datetime

from allauth.socialaccount.models import SocialApp
from base.models import Auth
from base.tests import BaseTestCase
from census.models import Census
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.test import Client, TestCase
from django.utils import timezone
from voting.models import Question, Voting
from booth.models import Opinion
from booth.form import OpinionForm

# Create your tests here.


class BoothTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def testBoothNotFound(self):
        # Se va a probar con el numero 10000 pues en las condiciones actuales en las que nos encontramos no parece posible que se genren 10000 votaciones diferentes
        response = self.client.get("/booth/vote/10000/")
        self.assertEqual(response.status_code, 404)

    def testBoothRedirection(self):
        # Se va a probar con el numero 10000 pues en las condiciones actuales en las que nos encontramos no parece posible que se genren 10000 votaciones diferentes
        response = self.client.get("/booth/vote/10000")
        self.assertEqual(response.status_code, 301)


class BoothVotingListTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        user = User.objects.create_user(username="testuser", password="testpass")
        question = Question.objects.create(desc="Test question")
        voting = Voting.objects.create(
            name="Test",
            desc="Test",
            start_date=timezone.make_aware(datetime.datetime(2023, 11, 11)),
            end_date=timezone.make_aware(datetime.datetime(2023, 11, 11)),
            question_id=question.id,
        )
        Census.objects.create(voter_id=user.id, voting_id=1)
        auth = Auth.objects.get_or_create(
            url=settings.BASEURL, defaults={"me": True, "name": "test auth"}
        )[0]
        voting.auths.add(auth)

        app = SocialApp.objects.create(
            provider="google",
            name="Google",
            client_id="test",
            secret="test",
        )
        # Add the current site to the SocialApp's sites
        app.sites.add(Site.objects.get_current())

    def tearDown(self):
        self.client = None

    def test_voting_list_view_with_authenticated_user(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get("/voting-list", follow=True)
        self.assertEqual(response.status_code, 200)

    def test_voting_list_view_with_unauthenticated_user(self):
        response = self.client.get("/voting-list")
        self.assertEqual(response.status_code, 302)


class BoothOpinionsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        user = User.objects.create_user(username="testuser", password="testpass")
        question = Question.objects.create(desc="Test question")
        voting = Voting.objects.create(
            name="Test",
            desc="Test",
            start_date=timezone.make_aware(datetime.datetime(2023, 11, 11)),
            end_date=timezone.make_aware(datetime.datetime(2023, 11, 11)),
            question_id=question.id,
        )
        Census.objects.create(voter_id=user.id, voting_id=1)
        auth = Auth.objects.get_or_create(
            url=settings.BASEURL, defaults={"me": True, "name": "test auth"}
        )[0]
        voting.auths.add(auth)

        app = SocialApp.objects.create(
            provider="google",
            name="Google",
            client_id="test",
            secret="test",
        )
        # Add the current site to the SocialApp's sites
        app.sites.add(Site.objects.get_current())

    def tearDown(self):
        self.client = None

    def test_opinions_view_with_authenticated_user(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get("/booth/opinions/1", follow=True)
        self.assertEqual(response.status_code, 200)

    def test_opinions_view_with_unauthenticated_user(self):
        response = self.client.get("/booth/opinions/1")
        self.assertEqual(response.status_code, 301)

    def test_opinions_form_view_with_authenticated_user(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get("/booth/opinions/1", follow=True)
        self.assertEqual(response.status_code, 200)
        form = OpinionForm({"text": "test opinion"})
        self.assertTrue(form.is_valid())
        opinion = form.save(commit=False)
        opinion.voting = Voting.objects.get(id=1)
        opinion.date = timezone.now()
        opinion.save()
        opinions = Opinion.objects.all()
        self.assertEqual(len(opinions), 1)
        self.assertEqual(opinions[0].text, "test opinion")
        self.assertEqual(opinions[0].voting.id, 1)

    def test_opinions_invalid_form_view_with_authenticated_user(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get("/booth/opinions/1", follow=True)
        self.assertEqual(response.status_code, 200)
        form = OpinionForm({"text": ""})
        self.assertFalse(form.is_valid())
        opinions = Opinion.objects.all()
        self.assertEqual(len(opinions), 0)
