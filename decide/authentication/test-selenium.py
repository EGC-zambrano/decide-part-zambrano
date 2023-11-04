from base.tests import BaseTestCase
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By


class LoginPageTestCase(StaticLiveServerTestCase):
    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()

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

    def test_sucessful_login(self):
        self.driver.get(f"{self.live_server_url}/signin")

        self.assertTrue(len(self.driver.find_elements(By.ID, "id_username")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_password")) == 1)

        self.driver.find_element(By.ID, "id_username").send_keys("testuser")
        self.driver.find_element(By.ID, "id_password").send_keys("testpass")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()

        self.assertTrue(self.driver.title == "Decide | Homepage")

    def test_failed_login(self):
        self.driver.get(f"{self.live_server_url}/signin")

        self.assertTrue(len(self.driver.find_elements(By.ID, "id_username")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_password")) == 1)

        self.driver.find_element(By.ID, "id_username").send_keys("testuser")
        self.driver.find_element(By.ID, "id_password").send_keys("wrongpass")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()

        self.assertTrue(self.driver.title == "Decide | Login")
        self.assertEquals(
            self.driver.find_element(By.CLASS_NAME, "form-errors").text,
            "Credenciales incorrectas",
        )
