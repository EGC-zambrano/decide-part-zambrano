from base.tests import BaseTestCase
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site


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

        app = SocialApp.objects.create(
            provider="google",
            name="Google",
            client_id="test",
            secret="test",
        )
        # Add the current site to the SocialApp's sites
        app.sites.add(Site.objects.get_current())

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


class LoginGoogleTestCase(StaticLiveServerTestCase):
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

        app = SocialApp.objects.create(
            provider="google",
            name="Google",
            client_id="test",
            secret="test",
        )
        # Add the current site to the SocialApp's sites
        app.sites.add(Site.objects.get_current())

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    def test_sucessful_login(self):
        self.driver.get(f"{self.live_server_url}/signin")

        self.driver.find_element(By.CSS_SELECTOR, ".google-button").click()
        self.assertEqual(
            self.driver.current_url,
            f"{self.live_server_url}/authentication/accounts/google/login/",
        )


class RegisterViewTestCase(StaticLiveServerTestCase):
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

        app = SocialApp.objects.create(
            provider="google",
            name="Google",
            client_id="test",
            secret="test",
        )
        # Add the current site to the SocialApp's sites
        app.sites.add(Site.objects.get_current())

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    def test_sucessful_registration(self):
        self.driver.get(f"{self.live_server_url}/register")

        self.assertTrue(len(self.driver.find_elements(By.ID, "id_username")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_first_name")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_last_name")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_email")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_password1")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_password2")) == 1)

        self.driver.find_element(By.ID, "id_username").send_keys("new_user")
        self.driver.find_element(By.ID, "id_first_name").send_keys("John")
        self.driver.find_element(By.ID, "id_last_name").send_keys("Doe")
        self.driver.find_element(By.ID, "id_email").send_keys("john.doe@example.com")
        self.driver.find_element(By.ID, "id_password1").send_keys("strong_password123")
        self.driver.find_element(By.ID, "id_password2").send_keys("strong_password123")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()

        self.assertTrue(self.driver.title == "Decide | Login")

    def test_failed_registration(self):
        self.driver.get(f"{self.live_server_url}/register")

        self.assertTrue(len(self.driver.find_elements(By.ID, "id_username")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_first_name")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_last_name")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_email")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_password1")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_password2")) == 1)

        self.driver.find_element(By.ID, "id_username").send_keys("")
        self.driver.find_element(By.ID, "id_first_name").send_keys("")
        self.driver.find_element(By.ID, "id_last_name").send_keys("")
        self.driver.find_element(By.ID, "id_email").send_keys("john")
        self.driver.find_element(By.ID, "id_password1").send_keys("strong_password")
        self.driver.find_element(By.ID, "id_password2").send_keys("strong_password123")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()

        self.assertTrue(self.driver.title == "Decide | Registration")

    def test_invalid_password(self):
        self.driver.get(f"{self.live_server_url}/register")

        self.assertTrue(len(self.driver.find_elements(By.ID, "id_username")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_first_name")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_last_name")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_email")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_password1")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_password2")) == 1)

        self.driver.find_element(By.ID, "id_username").send_keys("testuser")
        self.driver.find_element(By.ID, "id_first_name").send_keys("Jonh")
        self.driver.find_element(By.ID, "id_last_name").send_keys("Doe")
        self.driver.find_element(By.ID, "id_email").send_keys("john@doe.com")
        self.driver.find_element(By.ID, "id_password1").send_keys("2short")
        self.driver.find_element(By.ID, "id_password2").send_keys("2short")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()

        self.assertTrue(self.driver.title == "Decide | Registration")

    def test_user_already_exists(self):
        self.driver.get(f"{self.live_server_url}/register")

        self.assertTrue(len(self.driver.find_elements(By.ID, "id_username")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_first_name")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_last_name")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_email")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_password1")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_password2")) == 1)

        self.driver.find_element(By.ID, "id_username").send_keys("testuser")
        self.driver.find_element(By.ID, "id_first_name").send_keys("John")
        self.driver.find_element(By.ID, "id_last_name").send_keys("Doe")
        self.driver.find_element(By.ID, "id_email").send_keys("john@doe.com")
        self.driver.find_element(By.ID, "id_password1").send_keys("strong_password123")
        self.driver.find_element(By.ID, "id_password2").send_keys("strong_password123")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()

        self.assertTrue(self.driver.title == "Decide | Registration")
