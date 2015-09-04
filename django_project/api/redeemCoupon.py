from bson.json_util import dumps
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import Template, Context
import pymongo
import datetime
import random
import string
import json
from . import db

failure = dumps({"success": 0})
'''
dbclient = pymongo.MongoClient("mongodb://45.55.232.5:27017")
db = dbclient.perkkx
'''

limit = 2


@csrf_exempt
def test(request):
    collection = db.googleapitest
    collection.insert({"hi": "hi"})
    return HttpResponse("Bad Request", content_type="application/json")


@csrf_exempt
def get_ecom_coupon(request):
    try:
        collection = db.deals
        data = json.loads(request.body)

        '''
        result = collection.find_one({"vendor_id": data['vendor_id'], "cID": data["cID"]})
        if not result:
            result = db.one_time_deals.find_one({"vendor_id": data['vendor_id'], "cID": data["cID"]})
            collection = db.one_time_deals

        user = db.order_data.find_one({"userID": data['userID'], "cID": data["cID"]})
        if db.order_data.find({"userID": data['userID'], "ustatus": "pending"}).count() >= 2:
            return HttpResponse(dumps({"success": 0, "reason": "redeem limit reached"}),
                                content_type="application/json")
        else:
            codes = result['rcodes']
            code = codes.pop()
            result['rcodes'] = codes
            result['usedrcodes'].append(code)
            collection.update({"vendor_id": data['vendor_id'], "cID": data["cID"]}, {"$set": result}, False)
        '''

        result = collection.find_one_and_update(
            {"vendor_id": data['vendor_id'], "cID": data["cID"], "rcodes.0": {"$exists": True}, "type": "fixed"},
            {"$pop": {"rcodes": -1}},
            {"rcodes": {"$slice": 1}, "cID": True, "_id": False}
        )
        if result:
            code = result['rcodes'][0]                             # >>>>>>>> Code here
            collection.update_one(
                {"cID": result['cID'], "vendor_id": data['vendor_id']},
                {"$push": {'usedrcodes': code}}
            )
        else:
            result = collection.find_one(
                {"vendor_id": data['vendor_id'], "cID": data['cID'], "type": "generic"},
                {"rcodes": True, "cID": True}
            )
            if not result:
                return HttpResponse(dumps({"success": 0, "reason": "Deal just finished"}))

            code = str(random.choice(result['rcodes']))             # >>>>>>> Code here
            collection.update_one(
                {'cID': data['cID'], 'vendor_id': data['vendor_id']},
                {"$inc": {"usedrcodes."+code: 1 }}
            )

        user = db.order_data.find_one({"userID": data['userID'], "cID": data["cID"], "mstatus": "pending"})
        if user:
            return HttpResponse(dumps({"success": 0, "code": user['rcode'], "note": "Already used"}), content_type="application/json")
        else:
            couponRecord = {"vendor_id": data['vendor_id'], "cID": data["cID"], "userID": data['userID'], "rcode": code,
                            "used_on": datetime.datetime.now(), "ustatus": "pending", "mstatus": "pending"}
            db.order_data.insert(couponRecord)
            return HttpResponse(dumps({"success": 1, "code": code}), content_type="application/json")
    except:
        return HttpResponse(failure, content_type="application/json")


"""
{
    userID: aa1111,
    cID: A1
}
"""
success = {"success": 1}
failure = {"success": 0}


@csrf_exempt
def getUserDeals(request, userID):
    collection = db.order_data
    t = collection.find({
        "userID": userID,
        "ustatus": "pending"
    })
    data = []
    if t:
        for x in t:
            x = x


@csrf_exempt
def check_coupon(request):
    try:
        collection = db.order_data
        data = json.loads(request.body)
        # 1. Check if this user has already subscribed to deal
        t1 = collection.find_one({
            "userID": data["userID"],
            "cID": data["cID"],
            "mstatus": "pending"
        })
        if t1:
            result = failure.copy()
            result.update({"rcode": t1["rcode"]})
            return HttpResponse(dumps(result), content_type="application/json")

        # 2. Security check, validity of cID
        if db.deals.count({"cID": data["cID"]}) == 0 and db.one_time_deals.count({"cID": data['cID']}) == 0:
            result = failure.copy()
            result.update({"error": "Invalid cID"})
            return HttpResponse(dumps(result), content_type="application/json")

        # 3 Check if user is verified or not
        users = db.user
        user = users.find_one({"userID": data['userID']})
        if user['verified'] in 'N':
            t2 = collection.count({
                "userID": data['userID']
            })
            limit = 1
        else:
            t2 = collection.count({
                "userID": data["userID"],
                "ustatus": "pending"
            })
            limit = 2


        if t2 >= limit:
            return HttpResponse(dumps(failure), content_type="application/json")
        else:
            return HttpResponse(dumps(success), content_type="application/json")
    except Exception, e:
        result = failure.copy()
        result.update({"error": str(e)})
        return HttpResponse(dumps(result), content_type="application/json")


@csrf_exempt
def add_coupon(request):
    try:
        collection = db.order_data
        data = json.loads(request.body)
        vendor = db.deals.find_one({"cID": data["cID"]})
        if not vendor:
            vendor = db.one_time_deals.find_one({"cID": data['cID']})

        if vendor:
            collection.insert({
                "userID": data["rcode"][:-2],
                "rcode": data["rcode"],
                "ustatus": "pending",
                "mstatus": "pending",
                "vendor_id": vendor["vendor_id"],
                "cID": data["cID"],
                "used_on": datetime.datetime.now()  ## Mongo can store date directly !!
            })
            return HttpResponse(dumps(success), content_type="application/json")
        else:
            result = failure.copy()
            result.update({"error": "deal doesn't exist"})
            return HttpResponse(dumps(failure), content_type="application/json")
    except Exception, e:
        result = failure.copy()
        result.update({"error": str(e)})
        return HttpResponse(dumps(result), content_type="application/json")
