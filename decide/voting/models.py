from base import mods
from base.models import Auth, Key
from django.db import models
from django.db.models import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver


class Question(models.Model):
    QUESTION_TYPES = (
        ("S", "Single"),
        ("M", "Multiple"),
        ("P", "Priority"),
    )

    question_type = models.CharField(max_length=1, choices=QUESTION_TYPES, default="S")
    desc = models.TextField()

    def __str__(self):
        return self.desc


class QuestionOption(models.Model):
    question = models.ForeignKey(
        Question, related_name="options", on_delete=models.CASCADE
    )
    number = models.PositiveIntegerField(blank=True, null=True)
    option = models.TextField()

    def save(self):
        if not self.number:
            self.number = self.question.options.count() + 2
        return super().save()

    def __str__(self):
        return "{} ({})".format(self.option, self.number)


class Voting(models.Model):
    name = models.CharField(max_length=200)
    desc = models.TextField(blank=True, null=True)
    question = models.ForeignKey(
        Question, related_name="voting", on_delete=models.CASCADE
    )

    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    pub_key = models.OneToOneField(
        Key, related_name="voting", blank=True, null=True, on_delete=models.SET_NULL
    )
    auths = models.ManyToManyField(Auth, related_name="votings")

    tally = JSONField(blank=True, null=True)
    postproc = JSONField(blank=True, null=True)

    def create_pubkey(self):
        if self.pub_key or not self.auths.count():
            return

        auth = self.auths.first()
        data = {
            "voting": self.id,
            "auths": [{"name": a.name, "url": a.url} for a in self.auths.all()],
        }
        key = mods.post("mixnet", baseurl=auth.url, json=data)
        pk = Key(p=key["p"], g=key["g"], y=key["y"])
        pk.save()
        self.pub_key = pk
        self.save()

    def get_votes(self, token=""):
        # gettings votes from store
        votes = mods.get(
            "store", params={"voting_id": self.id}, HTTP_AUTHORIZATION="Token " + token
        )
        vote_list_p = []
        # anon votes
        if self.question.question_type == "S":
            votes_format = []
            vote_list = []
            for vote in votes:
                for option in vote["options"]:
                    votes_format.append(option["a"])
                    votes_format.append(option["b"])
                    vote_list.append(votes_format)
                    votes_format = []

        elif self.question.question_type == "P":
            votes_format = []
            votes_format_p = []
            vote_list = []
            for vote in votes:
                for option in vote["options"]:
                    votes_format.append(option["a"])
                    votes_format.append(option["b"])

                    if option["p"]:
                        votes_format_p.append(option["a"])
                        votes_format_p.append(option["b"])
                        votes_format_p.append(option["p"])
                    vote_list.append(votes_format)
                    vote_list_p.append(votes_format_p)
                    votes_format = []
                    votes_format_p = []
        return vote_list, vote_list_p

    def tally_votes(self, token=""):
        """
        The tally is a shuffle and then a decrypt
        """

        votes, votes_p = self.get_votes(token)

        auth = self.auths.first()
        shuffle_url = "/shuffle/{}/".format(self.id)
        decrypt_url = "/decrypt/{}/".format(self.id)
        auths = [{"name": a.name, "url": a.url} for a in self.auths.all()]

        # first, we do the shuffle
        data = {"msgs": votes_p}
        response = mods.post(
            "mixnet",
            entry_point=shuffle_url,
            baseurl=auth.url,
            json=data,
            response=True,
        )
        if response.status_code != 200:
            # TODO: manage error
            pass

        # then, we can decrypt that
        data = {"msgs": response.json()}
        response = mods.post(
            "mixnet",
            entry_point=decrypt_url,
            baseurl=auth.url,
            json=data,
            response=True,
        )

        if response.status_code != 200:
            # TODO: manage error
            pass

        self.tally = response.json()
        self.save()

        self.do_postproc()

    def do_postproc(self):
        tally = self.tally
        options = self.question.options.all()

        if self.question.question_type == "S":
            opts = []
            for opt in options:
                if isinstance(tally, list):
                    votes = tally.count(opt.number)
                else:
                    votes = 0
                opts.append(
                    {"option": opt.option, "number": opt.number, "votes": votes}
                )

            data = {"type": "IDENTITY", "options": opts}
            postp = mods.post("postproc", json=data)

            self.postproc = postp
            self.save()

        elif self.question.question_type == "P":
            opts = []
            vote_priority = {}
            votes = {}
            n_options = len(options)
            for opt in options:
                if isinstance(tally, list):
                    for vote in tally:
                        if vote[0] == opt.number:
                            if vote[0] in vote_priority:
                                vote_priority[vote[0]] += n_options - vote[1] + 1
                                votes[vote[0]] += 1
                            else:
                                vote_priority[vote[0]] = n_options - vote[1] + 1
                                votes[vote[0]] = 1
                opts.append(
                    {
                        "option": opt.option,
                        "number": opt.number,
                        "votes": votes[opt.number],
                        "points": vote_priority[opt.number],
                    }
                )
            data = {"type": "IDENTITY", "options": opts}
            postp = mods.post("postproc", json=data)

            self.postproc = postp
            self.save()

    def __str__(self):
        return self.name
