from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from userdb.tests.factories import UserFactory
from ..models import KeyPair
from .factories import KeyPairFactory


class TestKeyPairAPI(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Shared setup
        cls.path_name = "api:key_pairs"

        cls.user_a = UserFactory()
        cls.user_b = UserFactory()

    def test_keypair_list_allows_correct_methods(self):
        """Does the Allow response header specify the correct methods?"""
        self.client.force_login(user=self.user_a)
        response = self.client.head(reverse(self.path_name))
        allow = response["Allow"]
        self.assertEqual(allow, "GET, POST, HEAD, OPTIONS")

    def test_anon_user_cannot_view_keypairs_list(self):
        """Are anon users forbidden from the keypairs list endpoint?"""
        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_view_own_keypairs_list(self):
        """Can a user view their own keypairs?"""
        KeyPairFactory(user=self.user_a)
        KeyPairFactory(user=self.user_a)
        self.client.force_login(user=self.user_a)
        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_keypair_list_only_returns_keypairs_for_logged_in_user(self):
        """Does the keypairs list only include keypairs for the logged in user?"""
        own_keypair = KeyPairFactory(user=self.user_a)
        KeyPairFactory(user=self.user_b)
        self.client.force_login(user=self.user_a)
        response = self.client.get(reverse(self.path_name))
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0].get("id"), str(own_keypair.id))

    def test_user_can_create_keypair(self):
        """Can a user create a new keypair?"""
        self.client.force_login(user=self.user_a)
        pub_key = (
            "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQD3qr3/ulCGWhFokV8KNIURXwy30jeRLrqBTqGye3hKM6n9CGzVl7JXgph+8NhTyVJ3xc"
            "6dV3MVRcglU2Rxb1o+QJfnLv+YTxs17MDy5yV8/HUFL5yUEEizCA/fYa9MMWi1PVsSDJkTagYBjDdTNxpuJB2IvggevXjeKx7gzTInjsnE"
            "zszCgwjpfkwJ51Hglm7QnKfGJUGlwhELl8tmrqrwyvGaIyL5vfCUk9+JK8xWHMB5D2XNV+dVmyluD+izAcTu7ulm9diSdMX+u9yX5Ko5YP"
            "JnZyxYY/4zaRc7LEqf3yfq4KaIks0Mn3FdC/UPM2Y4Zw6+/KwId1LRxsARSRJlSNvLcL2qGzwrjc7EqZSuDu9selZJs4TcIyFs1cIkEmQZ"
            "+/hMJ5WVxJ6aSvuA0C9FU8PbQuRAC4asgnvpNoFdihGUym/xGBEbaRhQSG4aqQZX6ctvlA0u4q2tdzFauqZnpxS3eGHtPuzD1QDInb0kA9"
            "s6UlfZDsQ+OOGe177O1cE= someuser@MacBook-Pro.local"
        )
        name = "test_key"
        data = {"publicKey": pub_key, "name": name}
        response = self.client.post(reverse(self.path_name), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(KeyPair.objects.count(), 1)

    # Auto default

    # No duplicates

    # Deletion

    # Security for detail endpoint
