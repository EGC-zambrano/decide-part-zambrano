import datetime
import time

from allauth.socialaccount.models import SocialApp
from base.models import Auth
from base.tests import BaseTestCase
from census.models import Census
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.utils import timezone
from selenium import webdriver
from selenium.webdriver.common.by import By
from voting.models import Question, Voting


class WhiteVotes(StaticLiveServerTestCase):
    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()

        user = User.objects.get(username="noadmin")

        question = Question.objects.create(desc="Test question")
        self.voting1 = Voting.objects.create(
            name="Test1",
            desc="Test",
            start_date=timezone.make_aware(datetime.datetime(2023, 10, 11)),
            end_date=timezone.make_aware(datetime.datetime(2023, 10, 12)),
            question_id=question.id,
        )
        auth = Auth.objects.get_or_create(
            url=settings.BASEURL, defaults={"me": True, "name": "test auth"}
        )[0]
        self.voting1.auths.add(auth)
        Census.objects.create(voter_id=user.id, voting_id=self.voting1.id)

        app = SocialApp.objects.create(
            provider="google",
            name="Google",
            client_id="test",
            secret="test",
        )
        # Add the current site to the SocialApp's sites
        app.sites.add(Site.objects.get_current())

        # Opciones de Chrome
        options = webdriver.ChromeOptions()
        options.headless = True
        options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(options=options)
        self.user = User.objects.create_user(username="testuser", password="testpass")
        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    def test_white_vote_exists(self):
        self.driver.get(f"{self.live_server_url}/booth/{self.voting1.id}/")

        # Presiona el botón de toggler
        self.driver.find_element(By.CLASS_NAME, "navbar-toggler-icon").click()
        # Presiona el botón de login
        self.driver.find_element(By.CLASS_NAME, "btn-secondary").click()

        # Ingresa el usuario y contraseña
        self.driver.find_element(By.ID, "id_username").send_keys("noadmin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")

        self.driver.find_element(By.CLASS_NAME, "btn-primary").click()

        text_element = self.driver.find_element(
            By.XPATH, "//*[contains(text(), 'En blanco')]"
        )

        assert (
            "En blanco" in text_element.text
        ), "Text 'En blanco' not found on the page"
