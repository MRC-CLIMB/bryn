from django.contrib.messages import get_messages

from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import MessageSerializer


class MessagesListView(APIView):
    """
    API List endpoint for Django messages framework
    """

    def get(self, request):
        serialized_messages = MessageSerializer(
            [message for message in get_messages(request)], many=True
        )
        return Response(serialized_messages.data)
