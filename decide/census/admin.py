from django.http import HttpResponseRedirect
from django.urls import path
from django.shortcuts import render
from django.contrib import admin

from .models import Census
from django import forms
import csv


class CensusImportForm(forms.Form):
    csv_file = forms.FileField()


@admin.register(Census)
class CensusAdmin(admin.ModelAdmin):
    list_display = ("voting_id", "voter_id")
    list_filter = ("voting_id",)
    search_fields = ("voter_id",)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("import_census/", self.import_view),
        ]
        return my_urls + urls

    def import_view(self, request):
        if request.method == "POST":
            form = CensusImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES["csv_file"]
                reader = csv.reader(csv_file)
                header = next(reader)
                for row in reader:
                    voting_id, voter_id = row[0], row[1]
                    Census.objects.create(voting_id=voting_id, voter_id=voter_id)
                self.message_user(
                    request, f"Successfully imported {len(reader)} records."
                )
                return HttpResponseRedirect("..")
        else:
            form = CensusImportForm()
        return render(request, "census/import_census.html", {"form": form})


admin.site.register(Census, CensusAdmin)
