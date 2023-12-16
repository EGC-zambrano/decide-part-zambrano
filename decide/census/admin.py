from django.http import HttpResponseRedirect
from django.urls import path
from django.shortcuts import render
from django.contrib import admin

from .models import Census
from django import forms
from django.contrib import messages


class CensusImportForm(forms.Form):
    csv_file = forms.FileField()


@admin.register(Census)
class CensusAdmin(admin.ModelAdmin):
    list_display = ("voting_id", "voter_id")
    list_filter = ("voting_id",)
    search_fields = ("voter_id",)

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path("import_census/", self.import_view),
        ]
        return new_urls + urls

    def import_view(self, request):
        if request.method == "POST":
            form = CensusImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES["csv_file"]

                if not csv_file.name.endswith(".csv"):
                    messages.error(request, "File is not in CSV format.")
                    return HttpResponseRedirect(request.path_info)

                file_data = csv_file.read().decode("utf-8")
                csv_data = file_data.split("\n")
                for row in csv_data:
                    if len(row) == 0:
                        continue
                    fields = row.split(",")
                    Census.objects.create(voting_id=fields[0], voter_id=fields[1])
                self.message_user(
                    request,
                    f"Successfully imported {len(csv_data)-1} census instances.",
                )
                return HttpResponseRedirect("/admin/census/census/")
        else:
            form = CensusImportForm()
        return render(request, "admin/import_census.html", {"form": form})
