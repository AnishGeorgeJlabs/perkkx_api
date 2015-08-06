import pymongo
from django.http import HttpResponse
from bson.json_util import dumps

# Utility methods
def jsonResponse(obj):
    return HttpResponse(dumps(obj), content_type='application/json')

basic_success = jsonResponse({"result": True})
basic_failure = jsonResponse({"result": False})
def basic_error(e):
    return jsonResponse({
        "result": False,
        "error": str(e)
    })

# Data base
dbclient = pymongo.MongoClient("mongodb://45.55.232.5:27017")
db = dbclient.wadi

cl_blocked = db.blocked