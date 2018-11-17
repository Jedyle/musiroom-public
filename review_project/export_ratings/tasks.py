from celery import task
from .scraper import compute_file
from django.contrib.auth.models import User
from albums.models import Album
from albums.views import load_album_if_not_exists
from star_ratings.models import UserRating, Rating
from django.core.files.base import ContentFile
from notifications.signals import notify
from review_project.utils import make_clickable_link as _link
from django.db import transaction, IntegrityError
import json
import os

from .models import ExportReport


"""
from export_ratings.tasks import *
config = {'EP' : True}
export_from_sc("Risitas", "Armadeon", config, 'ERASE_OLD')
"""

def export_success_str(export):
    return  "Vos données ont été exportées avec succès. Consultez le rapport d'export {}.".format(_link(export, title="ici"))


def get_failures(errorfile):
    failures = []
    with open(errorfile, 'r') as errfile:
        for line in errfile:
            res = line.split('///')
            failures.append({
                'rating' : res[2],
                'album' : res[0],
                'artists' : res[1]
                })
    return failures

def rate(user, successfile, erase_old):
    new_ratings = []
    conflicts = []
    with open(successfile, 'r') as infile:
        for line in infile:
            print(line)
            mbid, rating = line.split(' ')
            try:
                album = Album.objects.get(mbid = mbid)
            except Album.DoesNotExist:
                album = load_album_if_not_exists(mbid)[0]
            print(album)
            if album is not None:
                if not UserRating.objects.has_rated(album, user):
                    Rating.objects.rate(album, rating, user=user)
                    new_ratings.append({
                        'mbid' : mbid,
                        'rating' : rating,
                        'title' : album.title,
                        })
                else:
                    if erase_old:
                        Rating.objects.rate(album, rating, user=user)
                    conflicts.append({
                        'mbid' : mbid,
                        'rating' : rating,
                        'title' : album.title,
                        })
    return new_ratings, conflicts
    

@task
def export_from_sc(username, sc_username, config, erase_old):
    
    #successfile, errorfile = compute_file(sc_username, config, temp_dir = "tmp/")

    successfile = "tmp/Ripaillouxsuccess2018-11-16-20:54:55.527330"
    errorfile = "tmp/Ripaillouxfails2018-11-16-20:54:55.527385"

    print('Exports done', successfile, errorfile)

    user = User.objects.get(username=username)


    failures = []

    try:
        with transaction.atomic():
            new_ratings, conflicts = rate(user, successfile, erase_old)       
            failures = get_failures(errorfile)

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
    except (OSError, IntegrityError, NameError, KeyError, ValueError) as e:
        print(e)
        notify.send(sender = user, recipient = user, verb = "une erreur est survenue", to_str= "Une erreur est survenue lors de l'export. Veuillez recommencez l'opération ou contacter un administrateur.")

    os.remove(successfile)
    os.remove(errorfile)
    
    

    
                    
                    
                    
                
                
                                    
            
