import factory

from django.contrib.auth import get_user_model
from faker import Factory

User = get_user_model()

faker = Factory.create()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: "user%d" % n)
    email = factory.LazyAttribute(lambda obj: "%s@example.com" % obj.username)


class TeamFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "userdb.Team"

    name = factory.Sequence(lambda n: "team%d" % n)
    position = faker.job()
    department = "Some Department"
    institution = faker.company()
    phone_number = faker.phone_number()
    research_interests = faker.text()
    research_interests = faker.text()
    research_interests = faker.text()
    verified = True


class InvitationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "userdb.Invitation"

    email = factory.Sequence(lambda n: "%d@example.com" % n)
    message = "Join our team!"
    to_team = factory.SubFactory(TeamFactory)
    made_by = factory.SubFactory(UserFactory)
