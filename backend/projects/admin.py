from django.contrib import admin
from .models import Investor, Project, Subscription

@admin.register(Investor)
class InvestorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email')
    search_fields = ('name', 'email')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'budget', 'total_funding_display')
    search_fields = ('name',)

    def total_funding_display(self, obj):
        return obj.total_funding()
    total_funding_display.short_description = 'Total funding'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'investor', 'project', 'share', 'investment_amount', 'created_at')
    list_filter = ('project',)
    search_fields = ('investor__name', 'project__name')
