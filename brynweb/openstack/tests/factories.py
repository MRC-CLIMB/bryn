import factory

from userdb.tests.factories import UserFactory


class KeyPairFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "openstack.KeyPair"

    name = factory.Sequence(lambda n: "user%d" % n)
    public_key = factory.Sequence(
        lambda n: (
            "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQD3qr3/ulCGWhFokV8KNIURXwy30jeRLrqBTqGye3hKM6n9CGzVl7JXgph+8NhTyVJ3x"
            "c6dV3MVRcglU2Rxb1o+QJfnLv+YTxs17MDy5yV8/HUFL5yUEEizCA/fYa9MMWi1PVsSDJkTagYBjDdTNxpuJB2IvggevXjeKx7gzTInjs"
            "nEzszCgwjpfkwJ51Hglm7QnKfGJUGlwhELl8tmrqrwyvGaIyL5vfCUk9+JK8xWHMB5D2XNV+dVmyluD+izAcTu7ulm9diSdMX+u9yX5Ko"
            "5YPJnZyxYY/4zaRc7LEqf3yfq4KaIks0Mn3FdC/UPM2Y4Zw6+/KwId1LRxsARSRJlSNvLcL2qGzwrjc7EqZSuDu9selZJs4TcIyFs1cIk"
            "EmQZ+/hMJ5WVxJ6aSvuA0C9FU8PbQuRAC4asgnvpNoFdihGUym/xGBEbaRhQSG4aqQZX6ctvlA0u4q2tdzFauqZnpxS3eGHtPuzD1QDIn"
            f"b0k{n}9s6UlfZDsQ+OOGe177O1cE= someuser@MacBook-Pro.local"
        )
    )
    user = factory.SubFactory(UserFactory)
