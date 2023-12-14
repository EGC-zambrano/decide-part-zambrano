import json

from base import mods
from census.models import Census
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from voting.models import Voting

from booth.form import OpinionForm


def index(request):
    return render(request, "booth/homepage.html")


@login_required(login_url="/signin")
def voting_list(request):
    votings_ids = Census.objects.filter(voter_id=request.user.id).values_list(
        "voting_id", flat=True
    )
    user_votings = Voting.objects.filter(id__in=votings_ids, start_date__isnull=False)

    user_votings = user_votings.order_by("-end_date")

    return render(request, "booth/voting-list.html", {"user_votings": user_votings})


@login_required(login_url="/signin")
def opinions(request, voting_id):
    try:
        voting = Voting.objects.get(id=voting_id)
    except:
        return redirect("voting-list")

    try:
        Census.objects.get(voting_id=voting_id, voter_id=request.user.id)
    except:
        return redirect("voting-list")

    opinions = voting.opinions.all().order_by("-date")

    if request.method == "POST":
        form = OpinionForm(request.POST)
        if form.is_valid():
            opinion = form.save(commit=False)
            opinion.voting = voting
            opinion.save()
            return redirect("opinions", voting_id=voting_id)
    else:
        form = OpinionForm()

    return render(
        request,
        "booth/opinions.html",
        {"voting": voting, "opinions": opinions, "form": form},
    )


class BoothView(TemplateView):
    template_name = "booth/booth.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vid = kwargs.get("voting_id", 0)

        try:
            r = mods.get("voting", params={"id": vid})
            # Casting numbers to string to manage in javascript with BigInt
            # and avoid problems with js and big number conversion
            for k, v in r[0]["pub_key"].items():
                r[0]["pub_key"][k] = str(v)

            context["voting"] = json.dumps(r[0])
        except:
            raise Http404

        context["KEYBITS"] = settings.KEYBITS

        return context
