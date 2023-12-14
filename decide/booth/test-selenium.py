import datetime, os

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


class HomepageTestCase(StaticLiveServerTestCase):
    def setUp(self):
        # Crea un usuario admin y otro no admin
        self.base = BaseTestCase()
        self.base.setUp()

        # Opciones de Chrome
        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    def test_simpleCorrectLogin(self):
        # Abre la ruta del navegador
        self.driver.get(f"{self.live_server_url}/")

        # Verifica que el nombre de la página sea el correcto
        self.assertTrue(self.driver.title == "Decide | Homepage")

        # Verifica que los elementos de la homepage existen
        self.assertTrue(len(self.driver.find_elements(By.CLASS_NAME, "header")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.TAG_NAME, "footer")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.CLASS_NAME, "hero")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "hero-text")) == 1)


class VotingListViewTestCase(StaticLiveServerTestCase):
    def setUp(self):
        # Crea un usuario admin y otro no admin
        self.base = BaseTestCase()
        self.base.setUp()

        user = User.objects.get(username="noadmin")
        # Crea 2 votaciones, una cerrada y otra abierta
        question = Question.objects.create(desc="Test question")
        voting1 = Voting.objects.create(
            name="Test1",
            desc="Test",
            start_date=timezone.make_aware(datetime.datetime(2023, 10, 11)),
            end_date=timezone.make_aware(datetime.datetime(2023, 10, 12)),
            question_id=question.id,
        )
        auth = Auth.objects.get_or_create(
            url=settings.BASEURL, defaults={"me": True, "name": "test auth"}
        )[0]
        voting1.auths.add(auth)
        Census.objects.create(voter_id=user.id, voting_id=voting1.id)

        voting2 = Voting.objects.create(
            name="Test2",
            desc="Test",
            start_date=timezone.make_aware(datetime.datetime(2023, 11, 11)),
            question_id=question.id,
        )
        auth = Auth.objects.get_or_create(
            url=settings.BASEURL, defaults={"me": True, "name": "test auth"}
        )[0]
        voting2.auths.add(auth)
        Census.objects.create(voter_id=user.id, voting_id=voting2.id)

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
        self.driver = webdriver.Chrome(options=options)

        # Disable recaptcha
        os.environ["DISABLE_RECAPTCHA"] = "1"

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    def test_voting_list(self):
        # Abre la ruta del navegador
        self.driver.get(f"{self.live_server_url}")

        self.driver.find_element(By.LINK_TEXT, "Votaciones").click()

        # Verifica que el nombre de la página sea el correcto
        self.assertTrue(self.driver.title == "Decide | Login")

        # Verifica que los elementos de la página de login existen
        self.assertTrue(len(self.driver.find_elements(By.CLASS_NAME, "header")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.TAG_NAME, "footer")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.CLASS_NAME, "form-card")) == 1)

        # Ingresa el usuario y contraseña
        self.driver.find_element(By.ID, "id_username").send_keys("noadmin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")

        # Presiona el botón de login
        self.driver.find_element(By.CLASS_NAME, "btn-primary").click()

        # Verifica que el nombre de la página sea el correcto
        self.assertTrue(self.driver.title == "Decide | Votings")

        # Verifica que los elementos de la página de listar existen
        self.assertTrue(len(self.driver.find_elements(By.CLASS_NAME, "header")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "voting-list")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.TAG_NAME, "footer")) == 1)
        self.assertTrue(
            len(self.driver.find_elements(By.CLASS_NAME, "voting-card")) == 2
        )

        # Verifica que existe una votación cerrada y otra abierta
        self.assertTrue(
            len(self.driver.find_elements(By.CLASS_NAME, "voting-closed")) == 1
        )

        self.assertTrue(
            len(self.driver.find_elements(By.CLASS_NAME, "voting-open")) == 1
        )

        # Verifica la barra de búsqueda
        search_bar = self.driver.find_element(By.ID, "search-bar")
        search_bar.send_keys("Test1")
        self.assertTrue(
            len(self.driver.find_elements(By.CLASS_NAME, "voting-open")) == 1
        )
        search_bar.clear()

        search_bar.send_keys("Test2")
        self.assertTrue(
            len(self.driver.find_elements(By.CLASS_NAME, "voting-closed")) == 1
        )
        search_bar.clear()

        # Verifica el filtrado
        select_filter = self.driver.find_element(By.ID, "filter")
        select_filter.find_element(By.XPATH, "//option[. = 'Open']").click()

        self.assertTrue(
            len(self.driver.find_elements(By.CLASS_NAME, "voting-open")) == 1
        )

        select_filter.find_element(By.XPATH, "//option[. = 'Closed']").click()

        self.assertTrue(
            len(self.driver.find_elements(By.CLASS_NAME, "voting-closed")) == 1
        )


class OpinionsViewTestCase(StaticLiveServerTestCase):
    def setUp(self):
        # Crea un usuario admin y otro no admin
        self.base = BaseTestCase()
        self.base.setUp()

        user = User.objects.get(username="noadmin")
        # Crea la votacion
        question = Question.objects.create(desc="Test question")
        voting1 = Voting.objects.create(
            name="Test1",
            desc="Test",
            start_date=timezone.make_aware(datetime.datetime(2023, 10, 11)),
            end_date=timezone.make_aware(datetime.datetime(2023, 10, 12)),
            question_id=question.id,
        )
        auth = Auth.objects.get_or_create(
            url=settings.BASEURL, defaults={"me": True, "name": "test auth"}
        )[0]
        voting1.auths.add(auth)
        Census.objects.create(voter_id=user.id, voting_id=voting1.id)

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
        self.driver = webdriver.Chrome(options=options)

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    def test_opinions(self):
        # Abre la ruta del navegador
        self.driver.get(f"{self.live_server_url}")

        self.driver.find_element(By.LINK_TEXT, "Votaciones").click()

        # Verifica que el nombre de la página sea el correcto
        self.assertTrue(self.driver.title == "Decide | Login")

        # Verifica que los elementos de la página de login existen
        self.assertTrue(len(self.driver.find_elements(By.CLASS_NAME, "header")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.TAG_NAME, "footer")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.CLASS_NAME, "form-card")) == 1)

        # Ingresa el usuario y contraseña
        self.driver.find_element(By.ID, "id_username").send_keys("noadmin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")

        # Presiona el botón de login
        self.driver.find_element(By.CLASS_NAME, "btn-primary").click()

        # Verifica que el nombre de la página sea el correcto
        self.assertTrue(self.driver.title == "Decide | Votings")

        # Verifica que los elementos de la página de listar existen
        self.assertTrue(len(self.driver.find_elements(By.CLASS_NAME, "header")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.ID, "voting-list")) == 1)
        self.assertTrue(len(self.driver.find_elements(By.TAG_NAME, "footer")) == 1)
        self.assertTrue(
            len(self.driver.find_elements(By.CLASS_NAME, "voting-card")) == 1
        )

        # Verifica que existe el boton de Opiniones
        self.assertTrue(
            len(self.driver.find_elements(By.CLASS_NAME, "opinions-card")) == 1
        )

    def test_form_opinions(self):
        # Abre la ruta del navegador
        self.driver.get(f"{self.live_server_url}")

        self.driver.find_element(By.LINK_TEXT, "Votaciones").click()

        # Ingresa el usuario y contraseña
        self.driver.find_element(By.ID, "id_username").send_keys("noadmin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")

        # Presiona el botón de login
        self.driver.find_element(By.CLASS_NAME, "btn-primary").click()

        # Verifica que existe el boton de Opiniones
        self.driver.find_element(By.LINK_TEXT, "Opiniones").click()

        # Verifica que hay dos h2
        self.assertTrue(len(self.driver.find_elements(By.TAG_NAME, "h2")) == 2)

        # Verifica que hay una form con textarea
        self.assertTrue(len(self.driver.find_elements(By.TAG_NAME, "textarea")) == 1)

        # Verifica que hay un boton de enviar
        self.assertTrue(len(self.driver.find_elements(By.ID, "submit-opinion")) == 1)
