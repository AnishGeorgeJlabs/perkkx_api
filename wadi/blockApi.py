from data import basic_success, jsonResponse, db, basic_failure, basic_error
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime

''' Cannot be used
@csrf_exempt
def block(request):
    if request.method == 'GET':
        if 'type' not in request.GET:
            return jsonResponse({"success": False, "error": "No type specified"})
        type = request.GET['type']

        lst = list(db.blocked.find({"type": type}, {"_id": False, "type": False}))
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
            # obj.pop("_id")
            result = db.blocked.insert_one(obj)
            return jsonResponse({"success": True, "_id": str(result.inserted_id)})
        else:
            return jsonResponse({"success": True, "message": "Already exists"})
'''


@csrf_exempt
def block(request):
    """
    GET/POST based method for blocking a phone and/or email
    :param request:
    :return:
    """
    if request.method == 'GET':
        data = request.GET
    else:
        data = json.loads(request.body)

    res = {}
    # ----- Email ------ #
    if 'email' in data and db.blocked_email.count({"email": data['email']}) == 0:
        resEm = db.blocked_email.insert_one({
            "email": data['email'],
            "timestamp": datetime.now()
        })
        res['email entry'] = str(resEm.inserted_id)

    # ----- Phone ------ #
    if 'phone' in data:
        ph = data['phone']
        if 'language' in data:
            language = map(
                lambda l: 'English' if 'eng' in l.lower() else 'Arabic',
                data['language'].split(',')
            )
        else:
            language = ['English', 'Arabic']

        if db.blocked_phone.count({"phone": ph}) == 0:
            resPh = db.blocked_phone.insert_one({
                "phone": ph,
                "language": language,
                "timestamp": datetime.now()
            })
            res['phone entry'] = str(resPh.inserted_id)
        else:
            db.blocked_phone.update_one(
                {
                    "phone": ph
                },
                {
                    "$addToSet": {
                        "language": {"$each": language}
                    },
                    "$set": {
                        "timestamp": datetime.now()
                    }
                })
            res['phone entry'] = 'Updated'
    if not res:
        return jsonResponse({"success": False})
    else:
        return jsonResponse({"success": True, "result": res})


def get_blocked(request):
    """
    GET based method for retrieving blocked [phone, language] or email list
    :param request:
    :return:
    """
    return jsonResponse({"success": False, "message": "Work in progress"})
