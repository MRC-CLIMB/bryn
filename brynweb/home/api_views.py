from django.db.models import Q
from django.db.models.functions import Now
from rest_framework.generics import ListAPIView

from .models import Announcement, FrequentlyAskedQuestion
from .serializers import AnnouncementSerializer, FrequentlyAskedQuestionSerializer


class AnnouncementListView(ListAPIView):
    """
    Announcement list view (published, not expired)
    """

    permission_classes = []
    serializer_class = AnnouncementSerializer
    queryset = (
        Announcement.objects.filter(published=True)
        .filter(Q(expiry__gt=Now()) | Q(expiry=None))
        .order_by("-updated_at")
    )


class FrequentlyAskedQuestionListView(ListAPIView):
    """
    FrequentlyAskedQuestion list view (published)
    """

    permission_classes = []
    serializer_class = FrequentlyAskedQuestionSerializer
    queryset = FrequentlyAskedQuestion.objects.filter(published=True)
