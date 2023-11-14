import datetime
import time
import random
from allauth.socialaccount.models import SocialApp
from base import mods
from base.models import Auth
from base.tests import BaseTestCase
from census.models import Census
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.utils import timezone
from mixnet.mixcrypt import MixCrypt
from mixnet.mixcrypt import ElGamal
from selenium import webdriver
from selenium.webdriver.common.by import By
from voting.models import Question, Voting, QuestionOption


class VisualizerTestCase(StaticLiveServerTestCase):
    
    def create_votings(self):
            # Setup votaciones
            q = Question(desc="test question")
            q.save()
            for i in range(5):
                opt = QuestionOption(question=q, option="option {}".format(i + 1))
                opt.save()
            v_open = Voting(name="test voting", question=q, start_date=timezone.now())
            v_open.save()

            v_closed = Voting(name="test voting closed", question=q, start_date=timezone.now())
            v_closed.save()

            v_not_started = Voting(name="test voting not started", question=q)
            v_not_started.save()

            a, _ = Auth.objects.get_or_create(
                url=settings.BASEURL, defaults={"me": True, "name": "test auth"}
            )
            a.save()
            v_open.auths.add(a)
            v_closed.auths.add(a)
            v_not_started.auths.add(a)

            # Close voting
            v_closed.end_date = timezone.now()
            v_closed.save()

            return v_open, v_closed, v_not_started

    def setUp(self):
        self.v_open, self.v_closed, self.v_not_started = self.create_votings()

        # Selenium Setup
        self.base = BaseTestCase()
        self.base.setUp()

        # Opciones de Chrome
        options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(options=options)
        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    def test_votacion_cerrada(self):
        # Abre la ruta del navegador
        self.driver.get(f"{self.live_server_url}/visualizer/{self.v_closed.id}")


        self.assertTrue(len(self.driver.find_elements(By.ID, "app-visualizer")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.CLASS_NAME, "show-charts")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.CLASS_NAME, "chart")) == 2)
        self.assertTrue(len(self.driver.find_elements(By.ID, "bar-chart")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "pie-chart")) == 1)


    def test_votacion_abierta(self):
        # Abre la ruta del navegador
        self.driver.get(f"{self.live_server_url}/visualizer/{self.v_open.id}")

        self.assertTrue(len(self.driver.find_elements(By.ID, "app-visualizer")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, 'voting-open')) == 1)


    def test_votacion_no_empezada(self):
        # Abre la ruta del navegador
        self.driver.get(f"{self.live_server_url}/visualizer/{self.v_not_started.id}")

        self.assertTrue(len(self.driver.find_elements(By.ID, "app-visualizer")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, 'voting-not-started')) == 1)



