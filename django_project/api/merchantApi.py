from bson.json_util import dumps
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import Template, Context
import pymongo
from datetime import datetime, timedelta
import random
import string
import json
import re
from mongo_filter import merchant_filter_small, deal_compact_filter

failure = dumps({"success": 0})
dbclient = pymongo.MongoClient("mongodb://45.55.232.5:27017")
db = dbclient.perkkx


def con_hours(t):
    return timedelta(hours=t.hour, minutes=t.minute)


def deal_valid(deal):
    if not deal:
        return False
    today = datetime.today()
    if 'expiry' in deal and today >= datetime.strptime(deal['expiry'], "%d/%m/%Y"):
        return False

    if 'deal_start' in deal and \
                    today < datetime.strptime(deal['deal_start'], "%d/%m/%Y"):
        return False

    if 'valid_days' in deal and \
                    ((today.weekday() + 1) % 7) not in deal['valid_days']:
        return False
    '''
    try:
        deal.pop('valid_days')
    except:
        pass
    '''

    if 'valid_time' in deal:
        res = check_time_between(
            open=datetime.strptime(deal['valid_time'][0], "%H:%M"),
            close=datetime.strptime(deal['valid_time'][1], "%H:%M"),
            now=datetime.now()
        )
        # deal.pop('valid_time')         Let us show dynamic deal data for now
        return res

    return True


def check_time_between(open, close, now):
    open = con_hours(open)
    close = con_hours(close)
    now = con_hours(now)
    if close < open:
        close += timedelta(hours=24)

    if open <= now < close:
        return True
    else:
        return False


def process_merchant(mer, long_version):
    if not long_version and 'special_event' in mer:
        sparr = mer.pop('special_event')
        mer['special'] = sparr[0]['title']

    if 'timing' in mer:
        if not long_version:
            timing = mer.pop('timing')
        else:
            timing = mer['timing']
        dayToday = (datetime.today().weekday() + 1) % 7
        today = timing[dayToday]  # Because sunday is 0
        op = check_time_between(
            open=datetime.strptime(today['open_time'], "%H:%M"),
            close=datetime.strptime(today['close_time'], "%H:%M"),
            now=datetime.now()
        )
        mer.update({"open": op})
        if not long_version:
            mer['open_time'] = today['open_time']
            mer['close_time'] = today['close_time']
        else:
            mer['today'] = dayToday

    if 'price' in mer:
        try:
            price = mer["price"]
            price = int(float(re.sub("[^\d+\.]", "", price).strip(".")))
            mer['price'] = price
        except:
            pass


def custom_filter(deal):
    if deal_valid(deal):
        if 'gmin' in deal:
            deal.pop('gmin')
        if 'group_size' in deal:
            deal.pop('group_size')
        return True
    else:
        return False


@csrf_exempt
def merchants(request, user, vendor):
    global db
    merchant = db.merchants.find_one({"vendor_id": int(vendor)}, merchant_filter_small)
    if merchant is None:
        return HttpResponse(dumps({}), content_type="application/json")

    if db.user.count({"userID": user, "followed." + str(vendor): {"$exists": True}}) > 0:
        merchant['followed'] = True
    else:
        merchant['followed'] = False

    process_merchant(merchant, long_version=True)

    category = merchant['cat'][0]
    if category == 5:
        merchant['all_deals'] = db.deals.find({'vendor_id': int(vendor)}, deal_compact_filter)
    else:
        """ Works like a charm :sunglasses: """
        all_deals = db.deals.aggregate([
            {"$match": {"vendor_id": int(vendor)}},
            {"$project": {"_id": False, "deal": True, "expiry": True, "cID": True, "group_size": True, "gmin": True,
                          "valid_days": True, "valid_time": True, "deal_start": True}},
            {"$group": {"_id": {"gsize": "$group_size", "gmin": "$gmin"},
                        "deals": {
                            "$addToSet": "$$ROOT"
                        }}},
            {"$sort": {"_id.gmin": 1}},
            {"$project": {"size": "$_id.gsize", "_id": False, "deals": True}}
        ])
        all_deals = list(all_deals)
        merchant['all_deals'] = filter(
            lambda group: len(group['deals']) > 0,
            map(
                lambda group: {'size': group['size'], 'deals': filter(custom_filter, group['deals'])},
                all_deals
            )
        )

    merchant['one_time_deals'] = list(db.one_time_deals.find({'vendor_id': int(vendor)}, deal_compact_filter))

    return HttpResponse(dumps(merchant), content_type="application/json")
