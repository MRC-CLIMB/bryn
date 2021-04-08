from rest_framework.serializers import ModelSerializer

from core.serializers import HashidsIntegerField
from .models import Announcement, FrequentlyAskedQuestion


class AnnouncementSerializer(ModelSerializer):
    id = HashidsIntegerField(read_only=True)

    class Meta:
        model = Announcement
        fields = [
            "id",
            "title",
            "content",
            "category",
            "created_at",
            "updated_at",
        ]


class FrequentlyAskedQuestionSerializer(ModelSerializer):
    id = HashidsIntegerField(read_only=True)

    class Meta:
        model = FrequentlyAskedQuestion
        fields = [
            "id",
            "title",
            "content",
            "category",
        ]
