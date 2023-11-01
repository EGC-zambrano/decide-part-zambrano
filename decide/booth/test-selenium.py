from base.tests import BaseTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By


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
