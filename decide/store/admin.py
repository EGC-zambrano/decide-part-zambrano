from django.contrib import admin

from .models import Vote, VoteOption

class VoteOptionInline(admin.TabularInline):
    # Show only as many VoteOptions as there are in the Vote
    extra = 0
    model = VoteOption

class VoteAdmin(admin.ModelAdmin):
    inlines = [VoteOptionInline]
    list_display = ('voting_id', 'voter_id')

admin.site.register(Vote, VoteAdmin)
