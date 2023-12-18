import json
import requests

from random import choice

from locust import HttpUser, SequentialTaskSet, TaskSet, task, between


HOST = "http://localhost:8000"
VOTING = 1
USER = "decideuser"
PASS = "decidepass123"


class LoadHomepage(TaskSet):
    @task
    def load_homepage(self):
        self.client.get("/")


class DefVisualizer(TaskSet):
    @task
    def index(self):
        self.client.get("/visualizer/{0}/".format(VOTING))


class DefVotingCreation(TaskSet):
    def on_start(self):
        self.client.post("/authentication/login/", {"username": USER, "password": PASS})
        response = self.client.get("/admin/voting/voting/add/")
        self.csrftoken = response.cookies["csrftoken"]

    @task
    def create_voting(self):
        self.client.post(
            "/admin/voting/voting/add/",
            {
                "csrfmiddlewaretoken": self.csrftoken,
                "title": "Test Voting locust",
                "description": "This is a test voting",
                "question": "1",
                "auths": "1",
            },
            headers={"X-CSRFToken": self.csrftoken},
        )


class DefUserCreation(TaskSet):
    counter = 0

    @task
    def create_user(self):
        DefUserCreation.counter += 1
        self.client.post(
            "/register/",
            {
                "first_name": f"Pepito{DefUserCreation.counter}",
                "last_name": f"Gonzalez{DefUserCreation.counter}",
                "email": f"test{DefUserCreation.counter}@test.com",
                "username": f"gonsale{DefUserCreation.counter}",
                "password1": "decidepass123",
                "password2": "decidepass123",
                "g-recaptcha-response": "test",
            },
        )


class HomepageUser(HttpUser):
    host = HOST
    tasks = [LoadHomepage]
    wait_time = between(3, 5)


class Visualizer(HttpUser):
    host = HOST
    tasks = [DefVisualizer]
    wait_time = between(3, 5)


class VotingCreation(HttpUser):
    host = HOST
    tasks = [DefVotingCreation]
    wait_time = between(3, 5)


class UserCreation(HttpUser):
    host = HOST
    tasks = [DefUserCreation]
    wait_time = between(3, 5)
