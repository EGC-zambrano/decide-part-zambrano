import base64
import os
import time
from allauth.socialaccount.models import SocialApp
from base.tests import BaseTestCase
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def click_captcha(driver):
    # Wait for element with id recaptcha-anchor to be appear
    WebDriverWait(driver, 10).until(
        EC.frame_to_be_available_and_switch_to_it(
            (
                By.CSS_SELECTOR,
                "iframe[name^='a-'][src^='https://www.google.com/recaptcha/api2/anchor?']",
            )
        )
    )
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//span[@id='recaptcha-anchor']"))
    ).click()  # Wait for element with id recaptcha-anchor to be present

    # Wait, we use time.sleep because the element with id recaptcha-accessible-status is only present if we are running the tests in non-headless mode
    # If we were running the tests in headless mode, we could wait for the element with id recaptcha-anchor to have text "verficado"
    time.sleep(2)

    # Return to default content
    driver.switch_to.default_content()


class LoginPageTestCase(StaticLiveServerTestCase):
    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()

        # Opciones de Chrome
        options = webdriver.ChromeOptions()
        options.headless = True
        options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(options=options)
        self.user = User.objects.create_user(
            username="testuser", password="testpass", email="test@email.com"
        )
        super().setUp()

        app = SocialApp.objects.create(
            provider="google",
            name="Google",
            client_id="test",
            secret="test",
        )
        # Add the current site to the SocialApp's sites
        app.sites.add(Site.objects.get_current())

        # Enable recaptcha
        os.environ["DISABLE_RECAPTCHA"] = "0"

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        # Disable recaptcha
        os.environ["DISABLE_RECAPTCHA"] = "1"

        self.base.tearDown()

    def test_password_reset(self):
        self.driver.get(f"{self.live_server_url}/signin")

        self.driver.find_element(By.LINK_TEXT, "Recuperar Contraseña").click()

        self.assertEqual(
            self.driver.current_url,
            f"{self.live_server_url}/password_reset/",
        )
        self.driver.find_element(By.ID, "id_email").send_keys("test@email.com")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()

        self.assertEqual(
            self.driver.current_url,
            f"{self.live_server_url}/authentication/password_reset_done/",
        )

    def test_password_reset_unknown_email(self):
        self.driver.get(f"{self.live_server_url}/signin")

        self.driver.find_element(By.LINK_TEXT, "Recuperar Contraseña").click()

        self.driver.find_element(By.ID, "id_email").send_keys("unknown@email.com")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()

        self.assertEqual(
            self.driver.current_url,
            f"{self.live_server_url}/password_reset/",
        )

    def test_sucessful_login(self):
        self.driver.get(f"{self.live_server_url}/signin")

        self.assertTrue(len(self.driver.find_elements(By.ID, "id_username")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_password")) == 1)

        self.driver.find_element(By.ID, "id_username").send_keys("testuser")
        self.driver.find_element(By.ID, "id_password").send_keys("testpass")
        click_captcha(self.driver)
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()

        self.assertTrue(self.driver.title == "Decide | Homepage")

    def test_failed_login(self):
        self.driver.get(f"{self.live_server_url}/signin")

        self.assertTrue(len(self.driver.find_elements(By.ID, "id_username")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_password")) == 1)

        self.driver.find_element(By.ID, "id_username").send_keys("testuser")
        self.driver.find_element(By.ID, "id_password").send_keys("wrongpass")
        click_captcha(self.driver)
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()

        self.assertTrue(self.driver.title == "Decide | Login")
        self.assertEquals(
            self.driver.find_element(By.CLASS_NAME, "form-errors").text,
            "Credenciales incorrectas",
        )

    def test_nocaptcha(self):
        self.driver.get(f"{self.live_server_url}/signin")

        self.assertTrue(len(self.driver.find_elements(By.ID, "id_username")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_password")) == 1)

        self.driver.find_element(By.ID, "id_username").send_keys("testuser")
        self.driver.find_element(By.ID, "id_password").send_keys("wrongpass")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()

        self.assertTrue(self.driver.title == "Decide | Login")
        self.assertEquals(
            self.driver.find_element(By.CLASS_NAME, "form-errors").text,
            "Error en el formulario",
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


class LoginGithubTestCase(StaticLiveServerTestCase):
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

        self.driver.find_element(By.CLASS_NAME, "github-button").click()
        self.assertTrue(self.driver.current_url.startswith("https://github.com/login"))


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

        # Enable recaptcha
        os.environ["DISABLE_RECAPTCHA"] = "0"

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        # Disable recaptcha
        os.environ["DISABLE_RECAPTCHA"] = "1"

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
        click_captcha(self.driver)
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()

        self.assertEqual(self.driver.title, "Decide | Homepage")

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
        click_captcha(self.driver)
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
        click_captcha(self.driver)
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
        click_captcha(self.driver)
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()

        self.assertTrue(self.driver.title == "Decide | Registration")

    def test_nocaptcha(self):
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

    def test_email_registration(self):
        self.driver.get(f"{self.live_server_url}/register")

        self.assertTrue(len(self.driver.find_elements(By.ID, "id_username")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_first_name")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_last_name")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_email")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_password1")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_password2")) == 1)

        self.driver.find_element(By.ID, "id_username").send_keys("luffy")
        self.driver.find_element(By.ID, "id_first_name").send_keys("John")
        self.driver.find_element(By.ID, "id_last_name").send_keys("Doe")
        self.driver.find_element(By.ID, "id_email").send_keys("john.doe@example.com")
        self.driver.find_element(By.ID, "id_password1").send_keys("strong_password123")
        self.driver.find_element(By.ID, "id_password2").send_keys("strong_password123")
        click_captcha(self.driver)
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()

        self.driver.find_element(By.LINK_TEXT, "Iniciar Sesión").click()

        self.driver.find_element(By.ID, "id_username").send_keys("luffy")
        self.driver.find_element(By.ID, "id_password").send_keys("strong_password123")
        click_captcha(self.driver)
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()

        encoded = base64.b64encode(bytes("luffy", encoding="utf-8")).decode("utf-8")
        urlVerificar = f"{self.live_server_url}/verificar/{encoded}"
        self.driver.get(urlVerificar)
        self.driver.find_element(By.LINK_TEXT, "Votaciones").click()

        self.assertTrue(self.driver.title == "Decide | Votings")

    def test_email_registration_neg(self):
        self.driver.get(f"{self.live_server_url}/register")

        self.assertTrue(len(self.driver.find_elements(By.ID, "id_username")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_first_name")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_last_name")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_email")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_password1")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_password2")) == 1)

        self.driver.find_element(By.ID, "id_username").send_keys("luffy")
        self.driver.find_element(By.ID, "id_first_name").send_keys("John")
        self.driver.find_element(By.ID, "id_last_name").send_keys("Doe")
        self.driver.find_element(By.ID, "id_email").send_keys("john.doe@example.com")
        self.driver.find_element(By.ID, "id_password1").send_keys("strong_password123")
        self.driver.find_element(By.ID, "id_password2").send_keys("strong_password123")
        click_captcha(self.driver)
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        self.driver.find_element(By.LINK_TEXT, "Iniciar Sesión").click()

        self.driver.find_element(By.ID, "id_username").send_keys("luffy")
        self.driver.find_element(By.ID, "id_password").send_keys("strong_password123")
        click_captcha(self.driver)
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()

        self.driver.find_element(By.LINK_TEXT, "Votaciones").click()
        self.assertEqual(self.driver.title, "Decide | Homepage")


class LogoutTestCase(StaticLiveServerTestCase):
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

    def test_sucessful_logout(self):
        self.driver.get(f"{self.live_server_url}/signin")

        self.assertTrue(len(self.driver.find_elements(By.ID, "id_username")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_password")) == 1)

        self.driver.find_element(By.ID, "id_username").send_keys("testuser")
        self.driver.find_element(By.ID, "id_password").send_keys("testpass")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()

        self.assertTrue(self.driver.title == "Decide | Homepage")

        self.driver.get(f"{self.live_server_url}/logout")

        self.assertTrue(self.driver.title == "Decide | Homepage")
        self.assertTrue(
            len(self.driver.find_elements(By.LINK_TEXT, "Registrarse")) == 1
        )
        self.assertTrue(
            len(self.driver.find_elements(By.LINK_TEXT, "Iniciar Sesión")) == 1
        )


class ChangePasswordViewTestCase(StaticLiveServerTestCase):
    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()

        # Opciones de Chrome
        options = webdriver.ChromeOptions()
        options.headless = True
        options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(options=options)
        self.user = User.objects.create_user(username="passuser", password="testpass")
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

    def test_change_password_view(self):
        self.driver.get(f"{self.live_server_url}/signin")

        self.assertTrue(len(self.driver.find_elements(By.ID, "id_username")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_password")) == 1)

        self.driver.find_element(By.ID, "id_username").send_keys("passuser")
        self.driver.find_element(By.ID, "id_password").send_keys("testpass")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()

        self.driver.get(f"{self.live_server_url}/change-password")

        self.assertTrue(len(self.driver.find_elements(By.ID, "id_old_password")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_new_password1")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "id_new_password2")) == 1)

        self.driver.find_element(By.ID, "id_old_password").send_keys("testpass")
        self.driver.find_element(By.ID, "id_new_password1").send_keys("newtestpass")
        self.driver.find_element(By.ID, "id_new_password2").send_keys("newtestpass")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()

        self.assertTrue(self.driver.title == "Decide | Homepage")

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newtestpass"))
