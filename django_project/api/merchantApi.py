from bson.json_util import dumps
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import Template,Context
import pymongo
import datetime
import random
import string
import json
import re
from mongo_filter import merchant_filter_small, deal_compact_filter
from dealsApi import deal_valid

failure = dumps({ "success": 0 })
dbclient = pymongo.MongoClient("mongodb://45.55.232.5:27017")
db = dbclient.perkkx


def con_hours(t):
    return datetime.timedelta(hours=t.hour, minutes=t.minute)

def process_merchant (mer):
    timing = mer.pop('timing')
    today = timing[(datetime.datetime.today().weekday() + 1) % 7]   # Because sunday is 0
    now = con_hours(datetime.datetime.now())
    close = con_hours(datetime.datetime.strptime(today['close_time'], "%H:%M"))
    open = con_hours(datetime.datetime.strptime(today['open_time'], "%H:%M"))
    if close < open:
        close += datetime.timedelta(hours=24)

    if open <= now < close:
        op = True
    else:
        op = False
    price = mer.pop("price")
    try:
        price = int(float(re.sub("[^\d+\.]","",price).strip(".")))
    except:
        pass

    else:
        mer.update({"distance":False})

    mer['price'] = price
    mer.update({"open":op})
    mer['open_time'] = today['open_time']
    mer['close_time'] = today['close_time']


@csrf_exempt
def merchants(request, mID):
    global db
    merchant = db.merchants.find_one({"vendor_id": int(mID)}, merchant_filter_small)
    if merchant is None:
        return HttpResponse(dumps({}), content_type="application/json")
    s = []
    g = []
    deals = db.deals.find(
        {"vendor_id": merchant['vendor_id']},
        deal_compact_filter
    )
    process_merchant(merchant)
    for deal in deals:
        if not deal_valid(deal):
            continue
        type = deal.pop('type')
        if type == 'single':
            s.append(deal)
        else:
            g.append(deal)
    merchant['deals'] = {
        "single": s,
        "group": g
    }
    return HttpResponse(dumps(merchant), content_type="application/json")

