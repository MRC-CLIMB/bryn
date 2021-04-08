"""
Functional tests for the userdb API
"""

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from .factories import InvitationFactory, TeamFactory, UserFactory
from ..models import Invitation, TeamMember

User = get_user_model()


class TestInvitationAPI(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Shared setup
        cls.path_name = "api:invitations"

        cls.team_a = TeamFactory()
        cls.team_a_admin = UserFactory()
        cls.team_a_member1 = UserFactory()
        TeamMember.objects.create(team=cls.team_a, user=cls.team_a_admin, is_admin=True)
        TeamMember.objects.create(team=cls.team_a, user=cls.team_a_member1)

        cls.team_b = TeamFactory()
        cls.team_b_admin = UserFactory()
        TeamMember.objects.create(team=cls.team_b, user=cls.team_b_admin, is_admin=True)

    def test_invitation_list_allows_retrieve_create(self):
        self.client.force_login(user=self.team_a_admin)
        response = self.client.head(
            reverse(self.path_name, kwargs={"team_id": self.team_a.pk})
        )
        allow = response["Allow"]
        self.assertEqual(allow, "GET, POST, HEAD, OPTIONS")

    def test_anon_user_cannot_get_invitation_list(self):
        """Are non-authenticated users forbidden from list endpoint?"""
        response = self.client.get(
            reverse(self.path_name, kwargs={"team_id": self.team_a.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_member_can_create_invitation(self):
        """Can team admins create invitations?"""
        self.client.force_login(user=self.team_a_admin)
        data = {
            "email": "someonenew@gmail.com",
            "message": "join us!",
        }
        response = self.client.post(
            reverse(self.path_name, kwargs={"team_id": self.team_a.pk}), data=data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Invitation.objects.count(), 1)

    def test_admin_member_can_view_invitations(self):
        """Can team admins view invitations?"""
        InvitationFactory(to_team=self.team_a, made_by=self.team_a_admin)
        InvitationFactory(to_team=self.team_a, made_by=self.team_a_admin)
        self.client.force_login(user=self.team_a_admin)
        response = self.client.get(
            reverse(self.path_name, kwargs={"team_id": self.team_a.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_admin_from_another_team_cannot_view_invitations(self):
        """Are team admins restricted to only seeing their own invitations?"""
        InvitationFactory(to_team=self.team_a, made_by=self.team_a_admin)
        self.client.force_login(user=self.team_b_admin)
        response = self.client.get(
            reverse(self.path_name, kwargs={"team_id": self.team_a.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_admin_can_view_invitations(self):
        """Is a non-admin team member able to view invitations?"""
        InvitationFactory(to_team=self.team_a, made_by=self.team_a_admin)
        self.client.force_login(user=self.team_a_member1)
        response = self.client.get(
            reverse(self.path_name, kwargs={"team_id": self.team_a.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_cannot_create_invitation_to_another_team(self):
        """Are team admins forbidden from creating invitations to another team (setting to_team)?"""
        self.client.force_login(user=self.team_a_admin)
        data = {
            "email": "someonenew@gmail.com",
            "message": "join us!",
            "to_team": self.team_b.hashid,  # Should be ignored (read_only on Serializer)
        }
        response = self.client.post(
            reverse(self.path_name, kwargs={"team_id": self.team_a.pk}), data=data
        )
        self.assertEqual(
            response.data["to_team"], self.team_a.hashid
        )  # To team set from url resolver, not overridable

    def test_invitiations_list_only_shows_correct_team(self):
        """Does the invitations list only show teams for the team specified in the url?"""
        InvitationFactory(to_team=self.team_a, made_by=self.team_a_admin)
        InvitationFactory(to_team=self.team_a, made_by=self.team_a_admin)
        InvitationFactory(to_team=self.team_b, made_by=self.team_b_admin)
        InvitationFactory(to_team=self.team_b, made_by=self.team_b_admin)
        self.client.force_login(user=self.team_a_admin)
        response = self.client.get(
            reverse(self.path_name, kwargs={"team_id": self.team_a.pk})
        )
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0].get("to_team"), self.team_a.hashid)

    def test_invitation_list_only_shows_pending_invitations(self):
        pending = InvitationFactory(to_team=self.team_a, made_by=self.team_a_admin)
        InvitationFactory(to_team=self.team_a, made_by=self.team_a_admin, accepted=True)
        self.client.force_login(user=self.team_a_admin)
        response = self.client.get(
            reverse(self.path_name, kwargs={"team_id": self.team_a.pk})
        )
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["uuid"], str(pending.uuid))

    def test_non_admin_cannot_create_invitation(self):
        """Are non-amdmin team members forbidden from creating invitations?"""
        self.client.force_login(user=self.team_a_member1)
        data = {
            "email": "someonenew@gmail.com",
            "message": "join us!",
        }
        response = self.client.post(
            reverse(self.path_name, kwargs={"team_id": self.team_a.pk}), data=data
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anon_user_cannot_get_invitation_detail(self):
        """Are non-authorised users forbidden from viewing individual invitations?"""
        invitation = InvitationFactory(to_team=self.team_a, made_by=self.team_a_admin)
        response = self.client.get(
            reverse(
                self.path_name, kwargs={"team_id": self.team_a.pk, "pk": invitation.pk},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_member_can_get_invitation_detail(self):
        """Can team admins view individual invitations?"""
        invitation = InvitationFactory(to_team=self.team_a, made_by=self.team_a_admin)
        self.client.force_login(user=self.team_a_admin)
        response = self.client.get(
            reverse(
                self.path_name, kwargs={"team_id": self.team_a.pk, "pk": invitation.pk},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("uuid"), str(invitation.uuid))

    def test_non_admin_member_can_get_invitation_detail(self):
        """Are non-admin team members able to view individual invitations?"""
        invitation = InvitationFactory(to_team=self.team_a, made_by=self.team_a_admin)
        self.client.force_login(user=self.team_a_member1)
        response = self.client.get(
            reverse(
                self.path_name, kwargs={"team_id": self.team_a.pk, "pk": invitation.pk},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_user_can_delete_an_invitation(self):
        """Can a team admin delete an invitation?"""
        invitation = InvitationFactory(to_team=self.team_a, made_by=self.team_a_admin)
        self.client.force_login(user=self.team_a_admin)
        response = self.client.delete(
            reverse(
                self.path_name, kwargs={"team_id": self.team_a.pk, "pk": invitation.pk},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Invitation.objects.count(), 0)

    def test_cannot_delete_an_accepted_invitation(self):
        """Is delete prevented for accepted invitations"""
        invitation = InvitationFactory(
            to_team=self.team_a, made_by=self.team_a_admin, accepted=True
        )
        self.client.force_login(user=self.team_a_admin)
        response = self.client.delete(
            reverse(
                self.path_name, kwargs={"team_id": self.team_a.pk, "pk": invitation.pk},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(Invitation.objects.count(), 1)
        self.assertContains(
            response, "Accepted invitations cannot be deleted", status_code=405
        )

    def test_cannot_create_duplicate_pending_invitation(self):
        """Is creation of a duplicate (team, email, accepted=False) invitation forbidden?"""
        existing = InvitationFactory(
            to_team=self.team_a, made_by=self.team_a_admin, accepted=False
        )
        self.client.force_login(user=self.team_a_admin)
        data = {
            "email": existing.email,
            "message": "would you like to join again?",
        }
        response = self.client.post(
            reverse(self.path_name, kwargs={"team_id": self.team_a.pk}), data=data
        )
        self.assertContains(
            response,
            "There is already a pending invitation for this team and email address.",
            status_code=400,
        )

    def test_cannot_create_invitation_for_existing_team_member(self):
        """Is creation of an invitation for an existing team member forbidden?"""
        self.client.force_login(user=self.team_a_admin)
        data = {
            "email": self.team_a_member1.email,
            "message": "would you like to join again?",
        }
        response = self.client.post(
            reverse(self.path_name, kwargs={"team_id": self.team_a.pk}), data=data
        )
        self.assertContains(
            response,
            "There is already a current team member with this email address.",
            status_code=400,
        )

    def test_can_re_invite_a_past_team_member(self):
        """Can an invitation be created for a previous team member who has left?"""
        previous_invite = InvitationFactory(
            to_team=self.team_a, made_by=self.team_a_admin, accepted=True
        )
        self.client.force_login(user=self.team_a_admin)
        data = {
            "email": previous_invite.email,
            "message": "would you like to join again?",
        }
        response = self.client.post(
            reverse(self.path_name, kwargs={"team_id": self.team_a.pk}), data=data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Invitation.objects.filter(
                to_team=self.team_a, email=previous_invite.email
            ).count(),
            2,
        )


class TestUserProfileAPI(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Shared setup
        cls.path_name = "api:user_profile"

        cls.user_a = UserFactory()
        cls.user_b = UserFactory()

    def test_anon_user_cannot_view_user_profile(self):
        """Are non-authenticated users forbidden from user profile endpoint?"""
        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_profile_endpoint_returns_logged_in_user(self):
        """Does the user profile return the logged in user?"""
        self.client.force_login(user=self.user_a)
        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.data.get("username"), self.user_a.username)

    def test_user_can_update_profile(self):
        """Can the logged in user update his profile?"""
        self.client.force_login(user=self.user_a)
        response = self.client.patch(
            reverse(self.path_name), data={"first_name": "Jim"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get(pk=self.user_a.pk).first_name, "Jim")

    def test_updating_email_sets_new_email_pending_verification(self):
        """Does updating user email set Profile.new_email_pending_verification?"""
        self.user_a.profile.email_validated = True
        self.client.force_login(user=self.user_a)
        self.client.patch(reverse(self.path_name), data={"email": "something@new.com"})
        updated_user = User.objects.get(pk=self.user_a.pk)
        self.assertEqual(
            updated_user.profile.new_email_pending_verification, "something@new.com"
        )

    def test_user_profile_cannot_be_deleted(self):
        """Is user profile deletion not allowed?"""
        self.client.force_login(user=self.user_a)
        response = self.client.delete(reverse(self.path_name))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class TestTeamMemberAPI(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Shared setup
        cls.path_name = "api:team_members"

        cls.team_a = TeamFactory()
        cls.team_a_admin = UserFactory()
        cls.team_a_member1 = UserFactory()
        TeamMember.objects.create(team=cls.team_a, user=cls.team_a_admin, is_admin=True)
        TeamMember.objects.create(team=cls.team_a, user=cls.team_a_member1)

        cls.team_b = TeamFactory()
        cls.team_b_admin = UserFactory()
        TeamMember.objects.create(team=cls.team_b, user=cls.team_b_admin, is_admin=True)

    def test_team_members_list_allows_retrieve_only(self):
        self.client.force_login(user=self.team_a_admin)
        response = self.client.head(
            reverse(self.path_name, kwargs={"team_id": self.team_a.pk})
        )
        allow = response["Allow"]
        self.assertEqual(allow, "GET, HEAD, OPTIONS")

    def test_anon_user_cannot_get_team_members(self):
        """Are non-authenticated users forbidden from viewing team members?"""
        response = self.client.get(
            reverse(self.path_name, kwargs={"team_id": self.team_a.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_member_can_view_team_members(self):
        """Is a team member able to see team members?"""
        self.client.force_login(user=self.team_a_member1)
        response = self.client.get(
            reverse(self.path_name, kwargs={"team_id": self.team_a.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_user_from_different_team_cannot_view_team_members(self):
        """Is a user from a different team forbidden from viewing team members?"""
        self.client.force_login(user=self.team_b_admin)
        response = self.client.get(
            reverse(self.path_name, kwargs={"team_id": self.team_a.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anon_user_cannot_view_team_member_detail(self):
        """Are non-authenticated users forbidden from viewing team member detail?"""
        teammember = TeamMember.objects.get(user=self.team_a_admin, team=self.team_a)
        response = self.client.get(
            reverse(
                self.path_name, kwargs={"team_id": self.team_a.pk, "pk": teammember.pk},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_member_can_view_team_member_detail(self):
        """Is a team member able to view individual team member objects?"""
        self.client.force_login(user=self.team_a_member1)
        teammember = TeamMember.objects.get(user=self.team_a_admin, team=self.team_a)
        response = self.client.get(
            reverse(
                self.path_name, kwargs={"team_id": self.team_a.pk, "pk": teammember.pk},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_team_admin_can_delete_team_member(self):
        """Can a team admin delete a team membership?"""
        self.client.force_login(user=self.team_a_admin)
        user = UserFactory()
        member = TeamMember.objects.create(team=self.team_a, user=user)
        response = self.client.delete(
            reverse(
                self.path_name, kwargs={"team_id": self.team_a.pk, "pk": member.pk},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(
            TeamMember.DoesNotExist, msg="TeamMember should have been deleted"
        ):
            TeamMember.objects.get(user=user, team=self.team_a)

    def test_non_admin_member_cannot_delete_team_member(self):
        """Are non-admin team members forbidden from deleting team members?"""
        self.client.force_login(user=self.team_a_member1)
        user = UserFactory()
        member = TeamMember.objects.create(team=self.team_a, user=user)
        response = self.client.delete(
            reverse(
                self.path_name, kwargs={"team_id": self.team_a.pk, "pk": member.pk},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_admin_cannot_delete_own_membership(self):
        user = UserFactory()
        member = TeamMember.objects.create(team=self.team_a, user=user, is_admin=True)
        self.client.force_login(user=user)
        response = self.client.delete(
            reverse(
                self.path_name, kwargs={"team_id": self.team_a.pk, "pk": member.pk},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class TestTeamAPI(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Shared setup
        cls.path_name = "api:teams"

        cls.team_a = TeamFactory()
        cls.team_a_admin = UserFactory()
        cls.team_a_member1 = UserFactory()
        TeamMember.objects.create(team=cls.team_a, user=cls.team_a_admin, is_admin=True)
        TeamMember.objects.create(team=cls.team_a, user=cls.team_a_member1)

        cls.team_b = TeamFactory()
        cls.team_b_admin = UserFactory()
        TeamMember.objects.create(team=cls.team_b, user=cls.team_b_admin, is_admin=True)

    def test_anon_user_cannot_view_team_detail(self):
        """Are non-authenticated users forbidden from viewing team detail?"""
        response = self.client.get(
            reverse(self.path_name, kwargs={"team_id": self.team_a.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_detail_allows_retrieve_update_methods(self):
        self.client.force_login(user=self.team_a_admin)
        response = self.client.head(
            reverse(self.path_name, kwargs={"team_id": self.team_a.pk})
        )
        allow = response["Allow"]
        self.assertEqual(allow, "GET, PUT, PATCH, HEAD, OPTIONS")

    def test_member_can_view_team_detail(self):
        self.client.force_login(user=self.team_a_member1)
        response = self.client.get(
            reverse(self.path_name, kwargs={"team_id": self.team_a.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("name"), self.team_a.name)

    def test_non_member_cannot_view_team_detail(self):
        self.client.force_login(user=self.team_a_member1)
        response = self.client.get(
            reverse(self.path_name, kwargs={"team_id": self.team_b.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_admin_can_patch_team_detail(self):
        self.client.force_login(user=self.team_a_admin)
        response = self.client.patch(
            reverse(self.path_name, kwargs={"team_id": self.team_a.pk}),
            data={"department": "Changed my department"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("department"), "Changed my department")
