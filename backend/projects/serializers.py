from rest_framework import serializers
from .models import Project, Subscription

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'budget']

class SubscriptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['investor', 'project', 'share', 'investment_amount']

    def validate(self, attrs):
        instance = Subscription(**attrs)
        if self.instance:
            instance.pk = self.instance.pk
        try:
            instance.full_clean()
        except serializers.ValidationError:
            raise
        except Exception as e:
            from django.core.exceptions import ValidationError as DjangoValidationError
            if isinstance(e, DjangoValidationError):
                raise serializers.ValidationError(e.message_dict)
            raise
        return attrs

    def create(self, validated_data):
        return Subscription.objects.create(**validated_data)
