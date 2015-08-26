from data import basic_success, jsonResponse, db, basic_failure, basic_error
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def block(request):
    if request.method == 'GET':
        if 'type' not in request.GET:
            return jsonResponse({"success": False, "error": "No type specified"})
        type = request.GET['type']

        lst = list(db.blocked.find({"type": type}, {"_id": False}))
        return jsonResponse({"success": True, "data": lst})

    else:
        data = json.loads(request.body)
        if 'type' not in data:
            return jsonResponse({"success": False, "error": "No type specified"})

        type = data['type']
        obj = {'type': type}
        if type == 'email':
            obj['email'] = data['email']
        elif type == 'phone':
            obj['phone'] = data['phone']
            obj['language'] = data['language']
        else:
            return jsonResponse({"success": False, "error": "Unknown type"})

        if db.blocked.count(obj) == 0:
            result = db.blocked.insert_one(obj)
            return jsonResponse({"success": True, "_id": str(result.insert_id)})
        else:
            return jsonResponse({"success": True, "message": "Already exists"})

