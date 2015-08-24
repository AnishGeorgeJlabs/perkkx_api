import pymongo
from django.http import HttpResponse
from bson.json_util import dumps

# Utility methods
def jsonResponse(obj):
    return HttpResponse(dumps(obj), content_type='application/json')

basic_success = jsonResponse({"result": True})

