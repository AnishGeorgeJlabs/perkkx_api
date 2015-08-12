from data import basic_success, jsonResponse, db, basic_failure, basic_error
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def login(request):
    try:
        data = json.loads(request.body)
        if db.credentials.count({"username": data['username'], "password": data['password']}) > 0:
            return basic_success
        else:
            return basic_failure
    except Exception, e:
        return basic_error(e)

@csrf_exempt
def formPost(request):
    try:
        data = json.loads(request.body)
        # Do processing here
        res = {'success': True, 'data_received': data}
        return jsonResponse(res)
    except Exception, e:
        return basic_error(e)

