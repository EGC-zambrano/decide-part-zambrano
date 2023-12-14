from django.urls import path

from . import views
from .views import BoothView

urlpatterns = [
    path("", views.index, name="homepage"),
    path("vote/<int:voting_id>/", BoothView.as_view()),
    path("opinions/<int:voting_id>/", views.opinions, name="opinions"),
    path("voting-list", views.voting_list, name="voting-list"),
]
