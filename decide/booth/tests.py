from base.tests import BaseTestCase
from django.test import TestCase

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
