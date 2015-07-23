from bson.json_util import dumps
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import Template,Context
import pymongo
from datetime import datetime, timedelta
import random
import string
import json
import re
from mongo_filter import merchant_filter_small, deal_compact_filter

failure = dumps({ "success": 0 })
dbclient = pymongo.MongoClient("mongodb://45.55.232.5:27017")
db = dbclient.perkkx


def con_hours(t):
    return timedelta(hours=t.hour, minutes=t.minute)

def deal_valid(deal):
    today = datetime.today()
    if today >= datetime.strptime(deal['expiry'], "%d/%m/%Y"):
        return False
    if 'valid_days' in deal and \
            ((today.weekday() + 1) % 7) not in deal['valid_days']:
        return False
    if 'valid_time' in deal:
        return check_time_between(
            open=datetime.strptime(deal['valid_time'][0], "%H:%M"),
            close=datetime.strptime(deal['valid_time'][1], "%H:%M"),
            now=datetime.now()
        )

    return True


def check_time_between (open, close, now):
    open = con_hours(open)
    close = con_hours(close)
    now = con_hours(now)
    if close < open:
        close += timedelta(hours=24)

    if open <= now < close:
        return False
    else:
        return True


def process_merchant (mer, save_timing):
    if not save_timing:
        timing = mer.pop('timing')
    else:
        timing = mer['timing']
    dayToday = (datetime.today().weekday() + 1) % 7
    today = timing[dayToday]   # Because sunday is 0
    op = check_time_between(
        open=datetime.strptime(today['open_time'], "%H:%M"),
        close=datetime.strptime(today['close_time'], "%H:%M"),
        now=datetime.now()
    )
    price = mer.pop("price")
    try:
        price = int(float(re.sub("[^\d+\.]","",price).strip(".")))
    except:
        pass

    else:
        mer.update({"distance":False})

    mer['price'] = price
    mer.update({"open":op})
    if not save_timing:
        mer['open_time'] = today['open_time']
        mer['close_time'] = today['close_time']
    else:
        mer['today'] = dayToday


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
    process_merchant(merchant, save_timing=True)
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

