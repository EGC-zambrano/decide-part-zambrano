from django.urls import path
from . import views
from .views import BoothView


urlpatterns = [
    path("", views.index, name="homepage"),
    path("register/", views.register, name="register"),
    path("<int:voting_id>/", BoothView.as_view()),
]
