"""
Tests for userdb serializers
"""

from rest_framework.test import APITestCase

from .factories import InvitationFactory
from ..serializers import InvitationSerializer


"""
Reminder: assertCountEqual
a and b have the same elements in the same number, regardless of their order.
"""


class TestInvitationSerializer(APITestCase):
    def setUp(self):
        self.serialized = InvitationSerializer(InvitationFactory())

    def test_invitation_serializer_has_expected_fields(self):
        """Does the Invitation serializer have the expected fields?"""
        data = self.serialized.data
        self.assertCountEqual(
            data.keys(),
            ["uuid", "email", "date", "message", "to_team"],  # made_by is hidden
        )

    def test_to_team_field_is_read_only(self):
        """Is the to_team field read only? (potential major security issue if not)"""
        self.assertEqual(self.serialized.get_fields()["to_team"].read_only, True)
