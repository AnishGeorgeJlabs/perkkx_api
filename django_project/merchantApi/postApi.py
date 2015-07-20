from django.views.decorators.csrf import csrf_exempt
import pymongo
from datetime import datetime, date
import calendar
from .data_query import db, response
import json

def _time_transform(data):
    tm = datetime.fromtimestamp(int(data / 1000))
    return tm

def _copy_bill(dest, source):
    dest['submitted_on'] = _time_transform(source['submitted_on'])
    dest['paid'] = source['paid']
    dest['discount'] = source['discount']

def update_order_data (query, req_data):
    collection = db.order_data
    record = collection.find_one(query)

    if not record:
        return True                             # Just a safety precaution, dont think this code will ever execute
    elif record['mstatus'] == 'used':           # Special case of multi-user operation
        return True
    ## This happens when one operator has entered the bill details in pending section but the other operator
    ## has not refreshed his list. So, he can still make a POST for the given query, so we return true and not
    ## make a bill update.

    # Section 0: Update cID if original is different
    record['cID'] = req_data['cID']
    record['mstatus'] = "used"
    _copy_bill(record, req_data)

    result = collection.update(query, record, False)        # IMPORTANT, cannot be updateOne
    return result['updatedExisting']

" Post data from the merchnat app "
@csrf_exempt
def post(request, vendor_id):
    try:
        req_data = json.loads(request.body.decode())
        collection = db.order_data
        
        if 'orig_cID' in req_data:
            query = {
                "vendor_id": int(vendor_id),
                "cID": req_data["orig_cID"],
                "userID": req_data["rcode"][:-2],
                "rcode": req_data["rcode"]
            }
            while not update_order_data(query, req_data):
                pass
            return response({ "success": 1, "debug": "case1" })
            
        else:
            newData = {
                "rcode": req_data["rcode"],
                "userID": req_data["rcode"][:-2],
                "cID": req_data["cID"],
                "used_on": _time_transform(req_data["used_on"]),
                "ustatus": 'pending',               # We allow the user to set feedback
                "vendor_id": int(vendor_id),
                "mstatus": 'used'
            }
            _copy_bill(newData, req_data)
            
            collection.insert(newData)
            return response({ "success": 1 , "debug": "case2"})

    except Exception, e:
        return response({"success": 0, "error": str(e)})


@csrf_exempt
def login(request):
    try:
        data = json.loads(request.body)
        collection = db.credentials
        if data['mode'] == "login":
            cred = collection.find_one({"username": data['username'], "password": data['password']})
            if cred:
                vendor = db.merchants.find_one({"vendor_id": cred['vendor_id']}, {"vendor_name": True, "_id": False})
                result = { "vendor_name": vendor['vendor_name'], "vendor_id": cred['vendor_id'] }
                if 'address' in vendor:
                    result.update({"address": vendor['address']})
                return response({"result": True, "data": result})
            else:
                return response({"result": False})
        elif data['mode'] == "change_pass":
            result = collection.update({"username": data['username'], "password": data["password_old"]},
                                           {"$set": {"password": data["password"]}})
            return response({"result": result['updatedExisting']})
        else:
            return response({"result": False, "error": "Unknown mode"})
    except Exception, e:
        return response({"result": False, "error": "Excepton: "+str(e)})

@csrf_exempt
def signup(request):
    failure = {"result": False}
    try:
        data = json.loads(request.body)
        if db.merchants.count({"vendor_id": data['vendor_id']}) == 0:
            return response(failure)

        collection = db.credentials
        if collection.count({"username": data['username']}) > 0:
            return response(failure)

        collection.insert_one({
            "vendor_id": data['vendor_id'],
            "username": data['username'],
            "password": data['password']
        })
        return response({"result": True})
    except Exception, e:
        return response({"result": False, "error": "Excepton: "+str(e)})
