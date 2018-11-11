from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseForbidden
from .sc_scraper import ParseSCUser
from .forms import SCExportForm
from .models import ExportReport
from .decorators import paginate
from .tasks import export_from_sc

# Create your views here.

@login_required
def create_export(request):
    if request.method == 'POST':
        form = SCExportForm(request.POST)
        if form.is_valid():
            user = request.user.username
            sc_user = form.cleaned_data['sc_url'].split('/')[-1]
            config = { el:True for el in form.cleaned_data['fields'] }
            erase = form.cleaned_data['erase']


            # launch task
            export_from_sc.delay(username = user, sc_username = sc_user, config=config, erase_old=erase)

            return render(request, 'export_ratings/launched.html', {})
            
    else:
        form = SCExportForm()
    return render(request, 'export_ratings/create.html', {'form' : form})


def parse_sc_user(request):
    username = request.GET.get('user')
    if username:
        parser = ParseSCUser(username)
        if parser.load():
            try:
                results = parser.get_user_data()
                return JsonResponse(results)
            except (TypeError, KeyError):
                return HttpResponseNotFound()
    return HttpResponseNotFound()

@login_required
def get_export(request, export_id):
    export = get_object_or_404(ExportReport, pk = export_id)
    if export.user != request.user:
        return HttpResponseForbidden()
    return render(request, 'export_ratings/export.html', {'stats' : export.get_stats()})
    

@login_required
@paginate()
def get_new_ratings(request, export_id):
    export = get_object_or_404(ExportReport, pk = export_id)
    if export.user != request.user:
        return HttpResponseForbidden()
    return JsonResponse({'data' : export.get_new_ratings()})

@login_required
@paginate()
def get_conflicts(request, export_id):
    export = get_object_or_404(ExportReport, pk = export_id)
    if export.user != request.user:
        return HttpResponseForbidden()
    return JsonResponse({'data' : export.get_conflicts()})

@login_required
@paginate()
def get_not_found(request, export_id):
    export = get_object_or_404(ExportReport, pk = export_id)
    if export.user != request.user:
        return HttpResponseForbidden()
    return JsonResponse({'data' : export.get_not_found()})
