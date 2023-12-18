import random
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from .models import Census
from base import mods
from base.tests import BaseTestCase
from datetime import datetime

from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from census.admin import CensusAdmin
import io


class CensusTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.census = Census(voting_id=1, voter_id=1)
        self.census.save()

    def tearDown(self):
        super().tearDown()
        self.census = None

    def test_check_vote_permissions(self):
        response = self.client.get(
            "/census/{}/?voter_id={}".format(1, 2), format="json"
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), "Invalid voter")

        response = self.client.get(
            "/census/{}/?voter_id={}".format(1, 1), format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "Valid voter")

    def test_list_voting(self):
        response = self.client.get("/census/?voting_id={}".format(1), format="json")
        self.assertEqual(response.status_code, 401)

        self.login(user="noadmin")
        response = self.client.get("/census/?voting_id={}".format(1), format="json")
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.get("/census/?voting_id={}".format(1), format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"voters": [1]})

    def test_add_new_voters_conflict(self):
        data = {"voting_id": 1, "voters": [1]}
        response = self.client.post("/census/", data, format="json")
        self.assertEqual(response.status_code, 401)

        self.login(user="noadmin")
        response = self.client.post("/census/", data, format="json")
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.post("/census/", data, format="json")
        self.assertEqual(response.status_code, 409)

    def test_add_new_voters(self):
        data = {"voting_id": 2, "voters": [1, 2, 3, 4]}
        response = self.client.post("/census/", data, format="json")
        self.assertEqual(response.status_code, 401)

        self.login(user="noadmin")
        response = self.client.post("/census/", data, format="json")
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.post("/census/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(data.get("voters")), Census.objects.count() - 1)

    def test_destroy_voter(self):
        data = {"voters": [1]}
        response = self.client.delete("/census/{}/".format(1), data, format="json")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(0, Census.objects.count())


class CensusTest(StaticLiveServerTestCase):
    def setUp(self):
        # Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    def createCensusSuccess(self):
        self.cleaner.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.cleaner.get(self.live_server_url + "/admin/census/census/add")
        now = datetime.now()
        self.cleaner.find_element(By.ID, "id_voting_id").click()
        self.cleaner.find_element(By.ID, "id_voting_id").send_keys(
            now.strftime("%m%d%M%S")
        )
        self.cleaner.find_element(By.ID, "id_voter_id").click()
        self.cleaner.find_element(By.ID, "id_voter_id").send_keys(
            now.strftime("%m%d%M%S")
        )
        self.cleaner.find_element(By.NAME, "_save").click()

        self.assertTrue(
            self.cleaner.current_url == self.live_server_url + "/admin/census/census"
        )

    def createCensusEmptyError(self):
        self.cleaner.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.cleaner.get(self.live_server_url + "/admin/census/census/add")

        self.cleaner.find_element(By.NAME, "_save").click()

        self.assertTrue(
            self.cleaner.find_element_by_xpath(
                "/html/body/div/div[3]/div/div[1]/div/form/div/p"
            ).text
            == "Please correct the errors below."
        )
        self.assertTrue(
            self.cleaner.current_url
            == self.live_server_url + "/admin/census/census/add"
        )

    def createCensusValueError(self):
        self.cleaner.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.cleaner.get(self.live_server_url + "/admin/census/census/add")
        now = datetime.now()
        self.cleaner.find_element(By.ID, "id_voting_id").click()
        self.cleaner.find_element(By.ID, "id_voting_id").send_keys("64654654654654")
        self.cleaner.find_element(By.ID, "id_voter_id").click()
        self.cleaner.find_element(By.ID, "id_voter_id").send_keys("64654654654654")
        self.cleaner.find_element(By.NAME, "_save").click()

        self.assertTrue(
            self.cleaner.find_element_by_xpath(
                "/html/body/div/div[3]/div/div[1]/div/form/div/p"
            ).text
            == "Please correct the errors below."
        )
        self.assertTrue(
            self.cleaner.current_url
            == self.live_server_url + "/admin/census/census/add"
        )


class ImportCSVCensusTestCase(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.factory = RequestFactory()
        self.admin = CensusAdmin(Census, self.site)

    def test_get_urls(self):
        request = self.factory.get("/admin/census/census/")
        urls = self.admin.get_urls()
        self.assertEqual(len(urls), 7)
        self.assertEqual(urls[0].pattern._route, "import_census/")
        self.assertEqual(urls[0].callback, self.admin.import_view)
        self.assertEqual(urls[1].pattern._route, "")
        self.assertEqual(urls[1].callback.__name__, "changelist_view")

    def test_import_view_get(self):
        request = self.factory.get("/admin/census/census/import_census/")
        response = self.admin.import_view(request)
        self.assertEqual(response.status_code, 200)

    def test_import_view_post_valid_csv(self):
        admin = CensusAdmin(Census, None)
        request = self.factory.post(
            "/admin/import/",
            {"csv_file": io.BytesIO(b"1,100\n2,200\n")},
        )
        request.method = "POST"
        request.FILES["csv_file"].name = "test.csv"
        request.session = {}
        request._messages = FallbackStorage(request)
        response = admin.import_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/census/census/")
        self.assertEqual(Census.objects.count(), 2)

    def test_import_view_post_empty_csv(self):
        admin = CensusAdmin(Census, None)
        request = self.factory.post("/admin/import/", {"csv_file": io.BytesIO(b"")})
        request.method = "POST"
        request.FILES["csv_file"].name = "test.csv"
        request.session = {}
        request._messages = FallbackStorage(request)
        response = admin.import_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/import/")
        self.assertEqual(Census.objects.count(), 0)

    def test_import_view_post_invalid_file(self):
        request = self.factory.post("/admin/census/census/import_census/")
        setattr(request, "session", "session")
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        file_content = b"1,John\n2,Alice\n"
        csv_file = io.BytesIO(file_content)
        csv_file.name = "invalid_file.txt"
        request.FILES["csv_file"] = csv_file
        request.FILES["csv_file"].seek(0)
        response = self.admin.import_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/census/census/import_census/")
        self.assertEqual(Census.objects.count(), 0)
