from bson.json_util import dumps
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import re
from . import db

failure = dumps({"success": 0})
'''
dbclient = pymongo.MongoClient("mongodb://45.55.232.5:27017")
db = dbclient.perkkx
'''


@csrf_exempt
def search(request):
    merchants = db.merchants
    try:
        q = request.GET['q']
    except:
        return HttpResponse(failure)
    query = {"vendor_name": re.compile(q, re.IGNORECASE)}
    if 'cat' in request.GET:
        cats = map(lambda k: int(k), request.GET['cat'].split(','))
        query.update({'cat': {"$in": cats}})

    result = merchants.distinct("vendor_name", query)
    success = dumps({"success": 1, "data": result})
    return HttpResponse(success, content_type="application/json")
