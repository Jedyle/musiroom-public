from pinax.badges.models import BadgeAward
from user_profile.tests.factories import UserFactory
from user_profile.badges import distinct_badges_for_user


def test_distinct_badges():
    user = UserFactory()
    award00 = BadgeAward.objects.create(user=user, slug="music_lover", level=0)
    award01 = BadgeAward.objects.create(user=user, slug="music_lover", level=1)
    award10 = BadgeAward.objects.create(user=user, slug="reviewer", level=0)
    award11 = BadgeAward.objects.create(user=user, slug="reviewer", level=1)
    award12 = BadgeAward.objects.create(user=user, slug="reviewer", level=2)
    award30 = BadgeAward.objects.create(user=user, slug="top10", level=0)
    user_badges = distinct_badges_for_user(user)
    assert user_badges.count() == 3
    assert award01 in user_badges
    assert award12 in user_badges
    assert award30 in user_badges
