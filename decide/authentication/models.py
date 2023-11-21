from django.contrib import admin
from django.db import models
from django.contrib.auth.models import User
from django.db import models

class EmailCheck(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    emailChecked = models.BooleanField()
