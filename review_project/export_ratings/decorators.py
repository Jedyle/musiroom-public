from django.http import JsonResponse
import json

def to_int(a):
    try :
        i = int(a)
        return i
    except ValueError:
        return 1

def paginate(per_page = 10, key = 'data'):

    def decorator(func):

        def wrapper(request, *args, **kwargs):

            print(func(request, *args, **kwargs).content.decode('utf-8'))
            results = json.loads(func(request, *args, **kwargs).content.decode('utf-8'))
            page = to_int(request.GET.get('page', 1))
            if page <= 0:
                results[key] = []
            else :
                n = len(results[key])
                results[key] = results[key][(page-1)*per_page:page*per_page]
            return JsonResponse(results)

        return wrapper

    return decorator
            

