from django.contrib import admin
from django.utils import timezone

from .models import QuestionOption
from .models import Question
from .models import Voting

from .filters import StartedFilter


def start(modeladmin, request, queryset):
    for v in queryset.all():
        v.create_pubkey()
        v.start_date = timezone.now()
        v.status = "Started"  # Set the status to indicate the voting is started
        v.save()


def stop(ModelAdmin, request, queryset):
    for v in queryset.all():
        v.end_date = timezone.now()
        v.status = "Stopped"  # Set the status to indicate the voting is stopped
        v.save()


def tally(ModelAdmin, request, queryset):
    for v in queryset.filter(end_date__lt=timezone.now()):
        token = request.session.get("auth-token", "")
        v.tally_votes(token)


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption


class QuestionAdmin(admin.ModelAdmin):
    inlines = [QuestionOptionInline]


class VotingAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date")
    readonly_fields = ("start_date", "end_date", "pub_key", "tally", "postproc")
    date_hierarchy = "start_date"
    list_filter = (StartedFilter,)
    search_fields = ("name",)

    actions = [start, stop, tally]

    def get_actions(self, request):
        # Customize the list of available actions based on the current status
        actions = super().get_actions(request)
        # Reopen option is available if the status is "Stopped"
        if Voting.objects.filter(end_date__isnull=False):
            actions["reopen_selected"] = (
                VotingAdmin.reopen_selected,
                "reopen_selected",
                "Reopen selected votings",
            )

        return actions

    @staticmethod
    def reopen_selected(modeladmin, request, queryset):
        for v in queryset.all():
            v.end_date = None  # Reset end_date to None
            v.status = "Started"  # Set the status to indicate the voting is reopened
            v.tally = None
            v.save()


admin.site.register(Voting, VotingAdmin)
admin.site.register(Question, QuestionAdmin)
