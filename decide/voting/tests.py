import itertools
import random

from base import mods
from base.tests import BaseTestCase
from census.models import Census
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.utils import timezone
from mixnet.mixcrypt import ElGamal, MixCrypt
from mixnet.models import Auth
from selenium import webdriver
from selenium.webdriver.common.by import By
from voting.models import Question, QuestionOption, Voting
from selenium.webdriver.chrome.webdriver import WebDriver
from django.core.exceptions import BadRequest


class VotingTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def encrypt_msg(self, msg, v, bits=settings.KEYBITS):
        pk = v.pub_key
        p, g, y = (pk.p, pk.g, pk.y)
        k = MixCrypt(bits=bits)
        k.k = ElGamal.construct((p, g, y))
        return k.encrypt(msg)

    def create_voting(self):
        q = Question(desc="test question")
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option="option {}".format(i + 1))
            opt.save()
        v = Voting(name="test voting", question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(
            url=settings.BASEURL, defaults={"me": True, "name": "test auth"}
        )
        a.save()
        v.auths.add(a)

        return v

    def create_white_voting(self):
        q = Question(desc="test question", voteBlank=True)
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option="option {}".format(i + 1))
            opt.save()
        v = Voting(name="test voting", question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(
            url=settings.BASEURL, defaults={"me": True, "name": "test auth"}
        )
        a.save()
        v.auths.add(a)

        return v

    def test_white_vote_is_first_option(self):
        v = self.create_white_voting()

        # Retrieve the options for the voting's question
        options = QuestionOption.objects.filter(question=v.question)

        # Check if the first option is 'En blanco'
        first_option = options.first()
        self.assertEqual(
            first_option.option, "Voto En Blanco", "En blanco is not the first option"
        )

    def create_white_voting_false(self):
        q = Question(desc="test question", voteBlank=False)
        q.save()

        opt = QuestionOption(question=q, option="Voto En Blanco")
        opt.save()
        v = Voting(name="test voting", question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(
            url=settings.BASEURL, defaults={"me": True, "name": "test auth"}
        )
        a.save()
        v.auths.add(a)

        return v

    def test_white_vote_is_false_tally(self):
        v = self.create_white_voting_false()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        clear = self.store_votes(v)

        self.login()  # set token
        v.tally_votes(self.token)

        tally = v.tally
        tally.sort()
        tally = {k: len(list(x)) for k, x in itertools.groupby(tally)}

        for q in v.question.options.all():
            self.assertEqual(tally.get(q.number, 0), clear.get(q.number, 0))

        self.assertEqual(len(v.postproc), 0)  # Expecting an empty postproc list

    def create_voters(self, v):
        for i in range(100):
            u, _ = User.objects.get_or_create(username="testvoter{}".format(i))
            u.is_active = True
            u.save()
            c = Census(voter_id=u.id, voting_id=v.id)
            c.save()

    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = "user{}".format(pk)
        user.set_password("qwerty")
        user.save()
        return user

    def store_votes(self, v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()

        clear = {}
        if v.question.options.count() == 1:
            opt = v.question.options.first()
            clear[opt.number] = 0
            for i in range(random.randint(0, 5)):
                a, b = self.encrypt_msg(opt.number, v)
                data = {
                    "voting": v.id,
                    "voter": voter.voter_id,
                    "vote": {"a": a, "b": b},
                }
                clear[opt.number] += 1
                user = self.get_or_create_user(voter.voter_id)
                self.login(user=user.username)
                voter = voters.pop()
                mods.post("store", json=data)
        else:
            for opt in v.question.options.all():
                clear[opt.number] = 0
                for i in range(random.randint(0, 5)):
                    a, b = self.encrypt_msg(opt.number, v)
                    data = {
                        "voting": v.id,
                        "voter": voter.voter_id,
                        "vote": {"a": a, "b": b},
                    }
                    clear[opt.number] += 1
                    user = self.get_or_create_user(voter.voter_id)
                    self.login(user=user.username)
                    voter = voters.pop()
                    mods.post("store", json=data)
        return clear

    def test_complete_voting(self):
        v = self.create_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        clear = self.store_votes(v)

        self.login()  # set token
        v.tally_votes(self.token)

        tally = v.tally
        tally.sort()
        tally = {k: len(list(x)) for k, x in itertools.groupby(tally)}

        for q in v.question.options.all():
            self.assertEqual(tally.get(q.number, 0), clear.get(q.number, 0))

        for q in v.postproc:
            self.assertEqual(tally.get(q["number"], 0), q["votes"])

    def test_create_voting_from_api(self):
        data = {"name": "Example"}
        response = self.client.post("/voting/", data, format="json")
        self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user="noadmin")
        response = mods.post("voting", params=data, response=True)
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        response = mods.post("voting", params=data, response=True)
        self.assertEqual(response.status_code, 400)

        data = {
            "name": "Example",
            "desc": "Description example",
            "question": "I want a ",
            "question_opt": ["cat", "dog", "horse"],
        }

        response = self.client.post("/voting/", data, format="json")
        self.assertEqual(response.status_code, 201)

    def test_create_boolean_voting_from_api(self):
        data = {"name": "Example boolean"}
        response = self.client.post("/voting/", data, format="json")
        self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user="noadmin")
        response = mods.post("voting", params=data, response=True)
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        response = mods.post("voting", params=data, response=True)
        self.assertEqual(response.status_code, 400)

        data = {
            "name": "Example boolean",
            "desc": "Description example boolean",
            "question_type": "B",
            "question": "Do you agree?",
            "question_opt": ["Sí", "No"],
        }

        response = self.client.post("/voting/", data, format="json")
        self.assertEqual(response.status_code, 201)

    def test_update_voting(self):
        voting = self.create_voting()

        data = {"action": "start"}

        # login with user no admin
        self.login(user="noadmin")
        response = self.client.put("/voting/{}/".format(voting.pk), data, format="json")
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        data = {"action": "bad"}
        response = self.client.put("/voting/{}/".format(voting.pk), data, format="json")
        self.assertEqual(response.status_code, 400)

        # STATUS VOTING: not started
        for action in ["stop", "tally"]:
            data = {"action": action}
            response = self.client.put(
                "/voting/{}/".format(voting.pk), data, format="json"
            )
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), "Voting is not started")

        data = {"action": "start"}
        response = self.client.put("/voting/{}/".format(voting.pk), data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "Voting started")

        # STATUS VOTING: started
        data = {"action": "start"}
        response = self.client.put("/voting/{}/".format(voting.pk), data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), "Voting already started")

        data = {"action": "tally"}
        response = self.client.put("/voting/{}/".format(voting.pk), data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), "Voting is not stopped")

        data = {"action": "stop"}
        response = self.client.put("/voting/{}/".format(voting.pk), data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "Voting stopped")

        # STATUS VOTING: stopped
        data = {"action": "start"}
        response = self.client.put("/voting/{}/".format(voting.pk), data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), "Voting already started")

        data = {"action": "stop"}
        response = self.client.put("/voting/{}/".format(voting.pk), data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), "Voting already stopped")

        data = {"action": "tally"}
        response = self.client.put("/voting/{}/".format(voting.pk), data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "Voting tallied")

        # STATUS VOTING: tallied
        data = {"action": "start"}
        response = self.client.put("/voting/{}/".format(voting.pk), data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), "Voting already started")

        data = {"action": "stop"}
        response = self.client.put("/voting/{}/".format(voting.pk), data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), "Voting already stopped")

        data = {"action": "tally"}
        response = self.client.put("/voting/{}/".format(voting.pk), data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), "Voting already tallied")

    def test_reopen_voting(self):
        voting = self.create_voting()
        self.login()

        # Not started yet
        data = {"action": "reopen"}
        response = self.client.put("/voting/{}/".format(voting.pk), data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), "Voting is not started")

        data = {"action": "start"}
        response = self.client.put("/voting/{}/".format(voting.pk), data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "Voting started")

        # Not stopped yet
        data = {"action": "reopen"}
        response = self.client.put("/voting/{}/".format(voting.pk), data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), "Voting is already open")

        data = {"action": "stop"}
        response = self.client.put("/voting/{}/".format(voting.pk), data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "Voting stopped")

        # Correct reopen
        data = {"action": "reopen"}
        response = self.client.put("/voting/{}/".format(voting.pk), data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "Voting reopened")

    def test_multiple_option_voting(self):
        v = (
            self.create_voting_multiple_options()
        )  # Add a new method to create a multiple option voting
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        clear = self.store_votes_multiple_options(v)

        self.login()  # set token
        v.tally_votes(self.token)

        tally = v.tally
        tally.sort()
        tally = {k: len(list(x)) for k, x in itertools.groupby(tally)}

        for q in v.question.options.all():
            self.assertEqual(tally.get(q.number, 0), clear.get(q.number, 0))

        for q in v.postproc:
            self.assertEqual(tally.get(q["number"], 0), q["votes"])

    def create_voting_multiple_options(self):
        q = Question(
            desc="test question multiple options", question_type="M"
        )  # Specify question_type as 'M'
        q.save()
        for i in range(5):
            opt = QuestionOption(
                question=q, option="option {}".format(i + 1), number=i + 1
            )
            opt.save()
        v = Voting(name="test voting multiple options", question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(
            url=settings.BASEURL, defaults={"me": True, "name": "test auth"}
        )
        a.save()
        v.auths.add(a)

        return v

    def store_votes_multiple_options(self, v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()

        clear = {}
        for _ in range(5):
            selected_options = []
            for opt in v.question.options.all():
                if random.choice([True, False]):
                    selected_options.append(opt.number)
                    clear[opt.number] = clear.get(opt.number, 0) + 1

            encrypted_options = []
            for option_number in selected_options:
                a, b = self.encrypt_msg(option_number, v)
                encrypted_options.append({"a": a, "b": b})

            data = {
                "voting": v.id,
                "voter": voter.voter_id,
                "vote": encrypted_options,
            }

            user = self.get_or_create_user(voter.voter_id)
            self.login(user=user.username)
            voter = voters.pop()
            mods.post("store", json=data)

        return clear


class LogInSuccessTests(StaticLiveServerTestCase):
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

    def successLogIn(self):
        self.cleaner.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")
        self.assertTrue(self.cleaner.current_url == self.live_server_url + "/admin/")


class LogInErrorTests(StaticLiveServerTestCase):
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

    def usernameWrongLogIn(self):
        self.cleaner.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("usuarioNoExistente")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("usuarioNoExistente")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.assertTrue(
            self.cleaner.find_element_by_xpath(
                "/html/body/div/div[2]/div/div[1]/p"
            ).text
            == "Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive."
        )

    def passwordWrongLogIn(self):
        self.cleaner.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("wrongPassword")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.assertTrue(
            self.cleaner.find_element_by_xpath(
                "/html/body/div/div[2]/div/div[1]/p"
            ).text
            == "Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive."
        )


class QuestionsTests(StaticLiveServerTestCase):
    def setUp(self):
        # Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
        self.cleaner: WebDriver = self.driver

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    def createQuestionSuccess(self):
        self.cleaner.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.cleaner.get(self.live_server_url + "/admin/voting/question/add/")

        self.cleaner.find_element(By.ID, "id_desc").click()
        self.cleaner.find_element(By.ID, "id_desc").send_keys("Test")
        self.cleaner.find_element(By.ID, "id_options-0-number").click()
        self.cleaner.find_element(By.ID, "id_options-0-number").send_keys("1")
        self.cleaner.find_element(By.ID, "id_options-0-option").click()
        self.cleaner.find_element(By.ID, "id_options-0-option").send_keys("test1")
        self.cleaner.find_element(By.ID, "id_options-1-number").click()
        self.cleaner.find_element(By.ID, "id_options-1-number").send_keys("2")
        self.cleaner.find_element(By.ID, "id_options-1-option").click()
        self.cleaner.find_element(By.ID, "id_options-1-option").send_keys("test2")
        self.cleaner.find_element(By.NAME, "_save").click()

        self.assertTrue(
            self.cleaner.current_url == self.live_server_url + "/admin/voting/question/"
        )

    def createCensusEmptyError(self):
        self.cleaner.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.cleaner.get(self.live_server_url + "/admin/voting/question/add/")

        self.cleaner.find_element(By.NAME, "_save").click()

        self.assertTrue(
            self.cleaner.find_element_by_xpath(
                "/html/body/div/div[3]/div/div[1]/div/form/div/p"
            ).text
            == "Please correct the errors below."
        )
        self.assertTrue(
            self.cleaner.current_url
            == self.live_server_url + "/admin/voting/question/add/"
        )


class BooleanQuestionTestCase(BaseTestCase):
    def setUp(self):
        self.question = Question.objects.create(
            question_type="B", desc="What is your favorite color?", voteBlank=False
        )
        self.question.save()

    def test_save_boolean_question(self):
        self.assertEqual(QuestionOption.objects.count(), 2)
        self.assertEqual(QuestionOption.objects.first().option, "Sí")
        self.assertEqual(QuestionOption.objects.last().option, "No")

    def test_str_representation(self):
        self.assertEqual(str(self.question), "What is your favorite color?")

    def test_one_option_boolean_question(self):
        self.question = Question.objects.create(
            question_type="B", desc="What is your favorite color?", voteBlank=False
        )
        self.question.save()

        opt = QuestionOption(question=self.question, option="option {}".format(1))
        with self.assertRaises(BadRequest):
            opt.save()

    def test_multiple_option_boolean_question(self):
        self.question = Question.objects.create(
            question_type="B", desc="What is your favorite color?", voteBlank=False
        )
        self.question.save()

        opt1 = QuestionOption(question=self.question, option="option {}".format(1))
        opt2 = QuestionOption(question=self.question, option="option {}".format(2))
        opt3 = QuestionOption(question=self.question, option="option {}".format(3))
        with self.assertRaises(BadRequest):
            opt1.save()
            opt2.save()
            opt3.save()


class BooleanWhiteTestCase(BaseTestCase):
    def setUp(self):
        self.question = Question.objects.create(
            question_type="B", desc="What is your favorite color?", voteBlank=True
        )
        self.question.save()

    def test_boolean_question_and_white(self):
        self.assertEqual(QuestionOption.objects.count(), 3)
        self.assertEqual(QuestionOption.objects.first().option, "Sí")
        self.assertEqual(QuestionOption.objects.all()[1].option, "No")
        self.assertEqual(QuestionOption.objects.last().option, "Voto En Blanco")
