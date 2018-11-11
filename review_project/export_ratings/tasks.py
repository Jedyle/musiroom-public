from celery import task
from .scraper import compute_export
from django.contrib.auth.models import User
from albums.models import Album
from albums.views import load_album_if_not_exists
from star_ratings.models import UserRating, Rating
from django.core.files.base import ContentFile
from notifications.signals import notify
from review_project.utils import make_clickable_link as _link
import json

from .models import ExportReport


"""
from export_ratings.tasks import *
config = {'EP' : True}
export_from_sc("Risitas", "Armadeon", config, 'ERASE_OLD')
"""

def export_success_str(export):
    return  "Vos données ont été exportées avec succès. Consultez le rapport d'export {}.".format(_link(export, title="ici"))
    

@task
def export_from_sc(username, sc_username, config, erase_old):
    print('Start')
    success, failures = compute_export(sc_username, config)

    print('Exports done')

    user = User.objects.get(username=username)

    new_ratings = []
    conflicts = []
    
    for element in success:
        try:
            album = Album.objects.get(mbid = element['mbid'])
        except Album.DoesNotExist:
            album = load_album_if_not_exists(element['mbid'])[0]
        if album is not None:
            if not UserRating.objects.has_rated(album, user):
                Rating.objects.rate(album, element['rating'], user=user)
                new_ratings.append(element)
            else:
                if erase_old:
                    Rating.objects.rate(album, element['rating'], user=user)
                conflicts.append(element)

    json_output = {
        'from' : 'Senscritique',
        'erase_old' : erase_old,
        'what_to_export' : config,
        'newly_created' : new_ratings,
        'conflicts' : conflicts,
        'not_found' : failures
        }

    print('Saving output')

    report_file = ContentFile(json.dumps(json_output))
    report = ExportReport(user = user)
    report.save()
    report.report.save(name = "", content=report_file)

    print("Done !")

    notify.send(sender = user, recipient = user, verb = "a exporté ses données", target = report, to_str = export_success_str(report))
    

    

    
                    
                    
                    
                
                
                                    
            
