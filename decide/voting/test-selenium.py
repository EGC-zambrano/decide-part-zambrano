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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from voting.models import Question, Voting


class TestTest2(StaticLiveServerTestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.vars = {}

    def tearDown(self):
        self.driver.quit()

    def test_test2(self):
        self.driver.get(f"{self.live_server_url}/booth/15/")
        self.driver.set_window_size(945, 1016)
        self.driver.find_element(By.ID, "username").send_keys("sammy")
        self.driver.find_element(By.ID, "password").send_keys("edgarmaness")
        self.driver.find_element(By.CSS_SELECTOR, ".navbar-toggler-icon").click()
        self.driver.find_element(By.CSS_SELECTOR, ".btn-secondary").click()
        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
        self.driver.find_element(By.ID, "q1").click()
        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
