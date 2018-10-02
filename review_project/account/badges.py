from pinax.badges.base import Badge, BadgeAwarded, BadgeDetail
from pinax.badges.registry import badges
from star_ratings.models import UserRating
from ratings.models import Review
from django.contrib.auth.models import User
from datetime import datetime, timedelta, time
from django.contrib.staticfiles.templatetags.staticfiles import static
from albums.models import AlbumGenre
from discussions.models import Discussion

class MusicophileBadge(Badge):
    slug = "musicophile"
    levels = [
        BadgeDetail(
            name = "Musicophile débutant",
            description = "Un bon début pour ce membre qui a noté au moins 1 album. Mais ce serait dommage qu'il s'arrête là, n'est ce pas ?"
            ),
        BadgeDetail(
            name = "Musicophile, niveau bronze",
            description = "Un membre actif qui a noté pas moins de 200 oeuvres. Mais il lui reste encore du chemin à parcourir pour rentrer dans un cercle encore plus fermé."
            ),
        BadgeDetail(
            name = "Musicophile, niveau argent",
            description = "Un membre cultivé qui a noté pas moins de 500 oeuvres. Il ambitionne sans doute de tutoyer les sommets de la culture musicale, mais il lui reste encore du travail."
            ),
        BadgeDetail(
            name = "Musicophile, niveau or",
            description = "Ce membre est un boulimique de musique, il a noté pas moins de 1000 oeuvres sur ce site. Mais quelque chose nous dit qu'il a encore faim."
            ), 
        ]

    images = [
        static('images/badges/MusicophileBeginner.png'),
        static('images/badges/MusicophileBronze.png'),
        static('images/badges/MusicophileSilver.png'),
        static('images/badges/MusicophileGold.png'),
        ]

    multiple = False

    events = [
        "daily_award",
        ]

    def award(self, **state):
        user = state["user"]
        rating_count = UserRating.objects.filter(user = user).count()
        if rating_count >= 1000:
            return BadgeAwarded(level = 4)
        elif rating_count >= 500:
            return BadgeAwarded(level = 3)
        elif rating_count >= 200:
            return BadgeAwarded(level = 2)
        elif rating_count >= 1:
            return BadgeAwarded(level = 1)


class CritiqueBadge(Badge):
    slug = "critique"
    levels = [
        BadgeDetail(
            name = "Critique en herbe",
            description = "Ce membre a dégainé sa plume électronique pour écrire sa première critique. C'est un début prometteur."
            ),
        BadgeDetail(
            name = "Critique, niveau bronze",
            description = "Un membre actif qui a critiqué pas moins de 20 oeuvres. L'histoire ne nous dit pas si ses critiques font 1 ligne ou 300 lignes chacunes. Mais du chemin reste à parcourir sur la route des chroniqueurs."
            ),
        BadgeDetail(
            name = "Critique, niveau argent",
            description = "Un critique averti qui a écrit sur plus de 50 oeuvres. Il n'est pas loin de toucher au Graal du chroniqueur."
            ),
        BadgeDetail(
            name = "Critique, niveau or",
            description = "Ce membre ne peut s'empêcher de donner son avis sur tout : il a d'ailleurs critiqué plus de 100 oeuvres sur ce site. Il est d'ailleurs sans doute en train de rédiger un nouveau pamphlet à l'heure actuelle."
            ), 
        ]

    images = [
        static('images/badges/CritiqueBeginner.png'),
        static('images/badges/CritiqueBronze.png'),
        static('images/badges/CritiqueSilver.png'),
        static('images/badges/CritiqueGold.png'),
        ]

    multiple = False

    events = [
        "daily_award",
        ]

    def award(self, **state):
        user = state["user"]
        rating_count = Review.objects.filter(rating__user = user).count()
        if rating_count >= 100:
            return BadgeAwarded(level = 4)
        elif rating_count >= 50:
            return BadgeAwarded(level = 3)
        elif rating_count >= 20:
            return BadgeAwarded(level = 2)
        elif rating_count >= 1:
            return BadgeAwarded(level = 1)


class ContributeurBadge(Badge):
    slug = "contributeur"
    levels = [
        BadgeDetail(
            name = "Contributeur débutant",
            description = "Ce membre a contribué à la renommée de La Musithèque en proposant son premier genre pour un album."
            ),
        BadgeDetail(
            name = "Contributeur, niveau bronze",
            description = "On remercie vivement ce membre qui a proposé plus de 50 genres pour différents albums. Il contribue ainsi à la renommée nationale de La Musithèque."
            ),
        BadgeDetail(
            name = "Contributeur, niveau argent",
            description = "Ce membre a donné de son temps pour proposer plus de 100 genres pour différents albums. Il contribue ainsi à la renommée mondiale de La Musithèque."
            ),
        BadgeDetail(
            name = "Contributeur, niveau or",
            description = "Ce membre est un véritable philanthrope, il a contribué à la renommée interstellaire de La Musithèque en proposant pas moins de 200 genres sur des albums. On ne l'oubliera jamais."
            ), 
        ]

    images = [
        static('images/badges/ContributeurBeginner.png'),
        static('images/badges/ContributeurBronze.png'),
        static('images/badges/ContributeurSilver.png'),
        static('images/badges/ContributeurGold.png'),
        ]

    multiple = False

    events = [
        "daily_award",
        ]

    def award(self, **state):
        user = state["user"]
        tag_count = AlbumGenre.objects.filter(user = user).count()
        if tag_count >= 200:
            return BadgeAwarded(level = 4)
        elif tag_count >= 100:
            return BadgeAwarded(level = 3)
        elif tag_count >= 50:
            return BadgeAwarded(level = 2)
        elif tag_count >= 1:
            return BadgeAwarded(level = 1)


class PipeletteBadge(Badge):
    slug = "pipelette"
    levels = [
        BadgeDetail(
            name = "Timide (niveau 1)",
            description = "Ce membre commence timidement son séjour sur La Musithèque en postant sa première discussion."
            ),
        BadgeDetail(
            name = "Gazouilleur (niveau 2)",
            description = "Ce membre participe à la vie de La Musithèque, il a déjà proposé plus de 20 discussions."
            ),
        BadgeDetail(
            name = "Pipelette (niveau 3)",
            description = "Ce membre est très certainement chanteur dans un groupe à succès, car il ne peut s'empêcher de parler. Il a déjà démarré plus de 50 discussions sur le site."
            ),
        BadgeDetail(
            name = "Grand Orateur (niveau 4)",
            description = "Tel Bruce Dickinson, ce membre est un orateur hors pair et un showman de tous les instants. Il a déjà écrit plus de 100 discussions sur le site."
            ), 
        ]

    images = [
        static('images/badges/PipeletteBeginner.png'),
        static('images/badges/PipeletteBronze.png'),
        static('images/badges/PipeletteSilver.png'),
        static('images/badges/PipeletteGold.png'),
        ]

    multiple = False

    events = [
        "daily_award",
        ]

    def award(self, **state):
        user = state["user"]
        disc_count = Discussion.objects.filter(author = user).count()
        if disc_count >= 100:
            return BadgeAwarded(level = 4)
        elif disc_count >= 50:
            return BadgeAwarded(level = 3)
        elif disc_count >= 20:
            return BadgeAwarded(level = 2)
        elif disc_count >= 1:
            return BadgeAwarded(level = 1)


class PionnierBadge(Badge):
    slug = "pionnier"
    levels = [
        BadgeDetail(
            name = "Pionnier",
            description = "Tel les Beatles, ce membre est un pionnier à la pointe de l'innovation musicale. Il appartient en effet au cercle très fermé des 200 premiers membres du site."
            ), 
        ]

    images = [
        static('images/badges/Pionnier.png'),
        ]

    multiple = False

    events = [
        "daily_award",
        ]

    def award(self, **state):
        user = state["user"]
        if user in User.objects.order_by('date_joined')[:200]:
            return BadgeAwarded(level = 1)


class Top10Badge(Badge):
    slug = "top10"
    levels = [
        BadgeDetail(
            name = "Top 10",
            description = "Ce membre est fier d'afficher ses goûts musicaux sur la toile. Il a ajouté 10 oeuvres à son top albums."
            ), 
        ]

    images = [
        static('images/badges/Top_10.png'),
        ]

    multiple = False

    events = [
        "daily_award",
        ]

    def award(self, **state):
        user = state["user"]
        print(user)
        top = user.account.top_albums
        if top.albums.count() >= 10:
            return BadgeAwarded(level = 1)


def regular_badge_update():
    users = User.objects.all()

    for user in users:
        badges.possibly_award_badge('daily_award', user=user)
