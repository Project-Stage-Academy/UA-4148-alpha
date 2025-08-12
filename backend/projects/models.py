from decimal import Decimal
from django.db import models
from django.db.models import Sum
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class Investor(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    def __str__(self):
        return self.name

    def total_funding(self) -> Decimal:
        
        agg = self.subscriptions.aggregate(total_amount=Sum('investment_amount'))
        total_amount = agg.get('total_amount') 

        if total_amount is not None:
            return Decimal(total_amount)

        agg2 = self.subscriptions.aggregate(total_share=Sum('share'))
        total_share = agg2.get('total_share') or Decimal("0.00")

        return (Decimal(total_share) / Decimal("100")) * (self.budget or Decimal("0.00"))
class Subscription(models.Model):
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE, related_name='subscriptions')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='subscriptions')

    share = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text=_("Investment share in percentage (0.00 - 100.00)")
    )

    investment_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Optional explicit investment amount in project currency")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('investor', 'project')  

    def __str__(self):
        return f"{self.investor} → {self.project} ({self.share}%)"

    def clean(self):
        
        if self.share is None:
            raise ValidationError({'share': _('Share must be set')})

        if self.share < Decimal("0.00") or self.share > Decimal("100.00"):
            raise ValidationError({'share': _('Share must be between 0 and 100')})

        qs = Subscription.objects.filter(project=self.project).exclude(pk=self.pk)
        agg = qs.aggregate(total_share=Sum('share'))
        total_existing = agg.get('total_share') or Decimal("0.00")

        if (Decimal(total_existing) + Decimal(self.share)) > Decimal("100.00"):
            raise ValidationError({
                'share': _('Total share for all subscriptions of this project would exceed 100%.')
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
