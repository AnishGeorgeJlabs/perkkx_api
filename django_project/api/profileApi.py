from bson.json_util import dumps
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import Template,Context
import pymongo
import datetime
import random
import string
import json
from mailer import Mailer
from mailer import Message
from . import db

'''
dbclient = pymongo.MongoClient("mongodb://45.55.232.5:27017")
db = dbclient.perkkx
'''

@csrf_exempt
def get_savings(request, userID):       # Dummy
    collection = db.order_data
    deals = collection.find({"userID":userID, "mstatus":"used", "discount": {"$exists": True}},
                            {"discount": True, "_id": False})
    total = 0
    for x in deals:
        total = total + x['discount']
    result = {
    "count":deals.count(),
    "saving":total
    }
    return HttpResponse(dumps(result), content_type='application/json')

@csrf_exempt
def get_followed(request, userID):      # Dummy
    try:
        collection = db.user
        result = collection.find_one({"userID":userID})
        merchants = result['followed']
        data = []
        merchant = db.merchants
        for x,y in merchants.items():
            mm = merchant.find_one({"vendor_id":int(x)})
            try:
                if 'address' in mm and 'area' in mm['address']:
                    address = mm['address']['area']
                elif 'address' in mm:
                    address = mm['address']['text']
                else:
                    address = mm['web_address']
            except:
                address = ''
            temp = {
            "vendor_name": mm['vendor_name'],
            "address":  address,
            "cat": mm['cat'],
            "rating": mm['rating'],
            "date": y
            }
            data.append(temp)
        return HttpResponse(dumps({"data":data}), content_type='application/json')
    except Exception, e:
        return HttpResponse(dumps({"sucess":0, "error": "exception: "+str(e)}), content_type='application/json')

@csrf_exempt
def pre_app_check(request):
    try:
        userID = request.GET['userID']
        data = {}
        user = db.user.find_one({"userID": userID})
        # Section 1, corporate info
        data['cinfo'] = True if 'cname' in user else False
        # Section 2, verified
        data['verified'] = True if user['verified'] == "Y" else False
        if not data['verified']:
            ocount = db.order_data.count({"userID": userID})
            data['allowed'] = ocount == 0
            if ocount == 1:
                pending = db.order_data.find_one({"userID": userID, "ustatus": "pending"})
                if pending:
                    data['rcode'] = pending['rcode']
                    merchant = db.merchants.find_one({'vendor_id': pending['vendor_id']}, {"_id": False, "vendor_name": True})
                    data['vendor_name'] = merchant['vendor_name']

        # Section 3, codes
        if data['verified']:
            records = db.order_data.find({"userID": userID, "ustatus": "pending"},
                                         {"_id": False, "rcode": True, "cID": True, "mstatus": True, "paid": True, "discount": True,"vendor_id":True})
            data['codes'] = []
            for x in records:
                vendor_data = db.merchants.find_one({"vendor_id":x['vendor_id']},
                                                    {"_id": False,"vendor_name":True,"address.area":True, 'web_address': True})
                x.update(vendor_data)
                data['codes'].append(x)

        return HttpResponse(dumps({"success": 1, "data": data}), content_type='application/json')
    except Exception, e:
        return HttpResponse(dumps({"success": 0, "error": "Exception "+str(e)}), content_type='application/json')

@csrf_exempt
def suggest_merchant(request):
    try:
        req_data = json.loads(request.body)
        userID = req_data['userID']
        data = req_data['data']
        db.suggested_merchants.insert_one({"userID": userID, "timestamp": datetime.datetime.now(), "merchant_data": data})
        return HttpResponse(dumps({"success": 1}), content_type='application/json')
    except Exception, e:
        return HttpResponse(dumps({"success": 0, "error": "Exception "+str(e)}), content_type='application/json')
