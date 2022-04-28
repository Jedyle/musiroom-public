from django.contrib.auth.models import User
from django.contrib.staticfiles.templatetags.staticfiles import static
from pinax.badges.models import BadgeAward
from pinax.badges.base import Badge, BadgeAwarded, BadgeDetail
from pinax.badges.registry import badges

from albums.models import AlbumGenre
from reviews.models import Review
from star_ratings.models import UserRating


class MusicLoverBadge(Badge):
    slug = "music_lover"
    levels = [
        BadgeDetail(
            name="Beginner Music Lover",
            description="This user has rated at least one album.",
        ),
        BadgeDetail(
            name="Music Lover - Bronze",
            description="This user has rated more than 200 albums !",
        ),
        BadgeDetail(
            name="Music Lover - Silver",
            description="This user has rated more than 500 albums !",
        ),
        BadgeDetail(
            name="Music Lover - Gold",
            description="This user has rated more than 1000 albums !",
        ),
    ]

    images = [
        static("images/badges/MusicophileBeginner.png"),
        static("images/badges/MusicophileBronze.png"),
        static("images/badges/MusicophileSilver.png"),
        static("images/badges/MusicophileGold.png"),
    ]

    multiple = False

    events = [
        "daily_award",
    ]

    def award(self, **state):
        user = state["user"]
        rating_count = UserRating.objects.filter(user=user).count()
        if rating_count >= 1000:
            return BadgeAwarded(level=4)
        elif rating_count >= 500:
            return BadgeAwarded(level=3)
        elif rating_count >= 200:
            return BadgeAwarded(level=2)
        elif rating_count >= 1:
            return BadgeAwarded(level=1)


class ReviewerBadge(Badge):
    slug = "reviewer"
    levels = [
        BadgeDetail(
            name="Beginner Reviewer",
            description="This user has written his first review.",
        ),
        BadgeDetail(
            name="Reviewer - Bronze",
            description="This user has written more than 20 reviews.",
        ),
        BadgeDetail(
            name="Reviewer - Silver",
            description="This user has written more than 50 reviews.",
        ),
        BadgeDetail(
            name="Reviewer - Gold",
            description="This user has written more than 100 reviews.",
        ),
    ]

    images = [
        static("images/badges/CritiqueBeginner.png"),
        static("images/badges/CritiqueBronze.png"),
        static("images/badges/CritiqueSilver.png"),
        static("images/badges/CritiqueGold.png"),
    ]

    multiple = False

    events = [
        "daily_award",
    ]

    def award(self, **state):
        user = state["user"]
        rating_count = Review.objects.filter(rating__user=user).count()
        if rating_count >= 100:
            return BadgeAwarded(level=4)
        elif rating_count >= 50:
            return BadgeAwarded(level=3)
        elif rating_count >= 20:
            return BadgeAwarded(level=2)
        elif rating_count >= 1:
            return BadgeAwarded(level=1)


class ContributorBadge(Badge):
    slug = "contributor"
    levels = [
        BadgeDetail(
            name="Beginner Contributor",
            description="This member has helped the community by suggesting a genre for an album.",
        ),
        BadgeDetail(
            name="Contributor - Bronze",
            description="Many thanks to this user who has suggested more than 50 genres for various albums.",
        ),
        BadgeDetail(
            name="Contributor - Silver",
            description="Many thanks to this user who has suggested more than 100 genres for various albums.",
        ),
        BadgeDetail(
            name="Contributor - Gold",
            description="Many thanks to this user who has suggested more than 200 genres for various albums..",
        ),
    ]

    images = [
        static("images/badges/ContributeurBeginner.png"),
        static("images/badges/ContributeurBronze.png"),
        static("images/badges/ContributeurSilver.png"),
        static("images/badges/ContributeurGold.png"),
    ]

    multiple = False

    events = [
        "daily_award",
    ]

    def award(self, **state):
        user = state["user"]
        tag_count = AlbumGenre.objects.filter(user=user).count()
        if tag_count >= 200:
            return BadgeAwarded(level=4)
        elif tag_count >= 100:
            return BadgeAwarded(level=3)
        elif tag_count >= 50:
            return BadgeAwarded(level=2)
        elif tag_count >= 1:
            return BadgeAwarded(level=1)


class PionneerBadge(Badge):
    slug = "pionneer"
    levels = [
        BadgeDetail(
            name="Pionneer",
            description="This user is among the happy few. He is one of the 200 first members of the community.",
        ),
    ]

    images = [
        static("images/badges/Pionnier.png"),
    ]

    multiple = False

    events = [
        "daily_award",
    ]

    def award(self, **state):
        user = state["user"]
        if user in User.objects.order_by("date_joined")[:200]:
            return BadgeAwarded(level=1)


class Top10Badge(Badge):
    slug = "top10"
    levels = [
        BadgeDetail(
            name="Top 10",
            description="This member has added his top 10 albums.",
        ),
    ]

    images = [
        static("images/badges/Top_10.png"),
    ]

    multiple = False

    events = [
        "daily_award",
    ]

    def award(self, **state):
        user = state["user"]
        top = user.profile.top_albums
        if top.albums.count() >= 10:
            return BadgeAwarded(level=1)


def regular_badge_update():
    users = User.objects.all()
    for user in users:
        badges.possibly_award_badge("daily_award", user=user)


def distinct_badges_for_user(username):
    return (
        BadgeAward.objects.filter(user__username=username)
        .order_by("slug", "-level")
        .distinct("slug")
    )


badges.register(MusicLoverBadge)
badges.register(ReviewerBadge)
badges.register(ContributorBadge)
badges.register(PionneerBadge)
badges.register(Top10Badge)
