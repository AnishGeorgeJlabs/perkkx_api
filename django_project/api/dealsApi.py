from bson.json_util import dumps
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import Template,Context
import pymongo
import datetime
import random
import string
import json
import math
import re
from unidecode import unidecode
from dateutil.tz import *
from math import pi, sin , cos , atan2,sqrt

failure = dumps({ "success": 0 })
dbclient = pymongo.MongoClient("mongodb://45.55.232.5:27017")
db = dbclient.perkkx

dayMap = {0:1,1:2,2:3,3:4,4:5,5:6,6:0}

def distance(obj):
    R = 6371
    dLat = (obj['l2'] - obj['l1']) * pi / 180
    dLon = (obj['ln2'] - obj['ln1']) * pi / 180
    lat1 = obj['l1'] * pi / 180
    lat2 = obj['l2'] * pi / 180
    a = sin(dLat/2) * sin(dLat/2) + sin(dLon/2) * sin(dLon/2) * cos(lat1) * cos(lat2)
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    d = R * c
    return d

@csrf_exempt
def get_deals(request,user, category, typ):
    global db
    try:
        mCollection = db.merchants
        dCollection = db.deals
        data = []
        try:
            pages = int(request.GET['pages'])
        except:
            pages = 1
        if 'lat' in request.GET.keys() and 'lon' in request.GET.keys():
            lat = re.sub("[^0-9\.]","",request.GET['lat'])
            lon = re.sub("[^0-9\.]","",request.GET['lon'])
        else:
            lat = False
        if 'r' in request.GET.keys():
            r = int(request.GET['r'])
        else:
            r = False
        if 'open' in request.GET.keys():
            ope = True
        else:
            ope = False
        reverse = False
        if 'sort' in request.GET.keys():
            if 'rating' in request.GET['sort']:
                sort = 'rating'
                reverse = True
            elif 'price' in request.GET['sort']:
                sort = 'price'
            elif 'r' in request.GET['sort']:
                sort = 'distance'
            else:
                sort = 'distance'
        else:
            sort = 'distance'

        search = {"cat": int(category)}
        if 'subcat' in request.GET.keys():
            search.update({"subcat":{"$in":[int(x.replace("u","").strip("'")) for x in request.GET['subcat'].split(",")]}})
        if 'ser' in request.GET.keys():
            search.update({"spec_event.title":{"$in":request.GET['ser'].split(",")}})
        if 'cuisine' in request.GET.keys():
            search.update({"cuisine":{"$in":request.GET['cuisine'].split(",")}})
        if 'mtype' in request.GET.keys():
            search.update({"massage.type":int(request.GET['mtype'])})
        if 'tag' in request.GET.keys():
            search.update({"icons":{"$in":request.GET['tag'].split(",")}})
        if 'vendor' in request.GET.keys():
            search.update({"vendor_id":{"$in":[int(x.replace("u","").strip("'")) for x in request.GET['vendor'].split(",")]}})
        if 'area' in request.GET.keys():
            search.update({"address.text":{"$in":[re.compile(x.replace("_"," "),re.IGNORECASE) for x in request.GET['area'].split(",")]}})
        if 'name' in request.GET.keys():
        	search.update({"vendor_name":request.GET['name']})
        if 'type' in request.GET.keys():
            search.update({"type":{"$in":[re.compile(x.replace("_"," "),re.IGNORECASE) for x in request.GET['type'].split(",")]}})
        if 'rate' in request.GET.keys():
            rating = [float(int(x) - 0.1) for x in request.GET['rate'].split(",")]
            search.update({"rating":{"$gt":min(rating)}})
        if 'price' in request.GET.keys():
            low,high = request.GET['price'].split("-")
            low = int(low) - 1
            high = int(high) - 1
            search.update({"price":{"$gt":low,"$lt":high}})
        mer = mCollection.find(search)
        for m in mer:
            deals = dCollection.find({"vendor_id": m["vendor_id"], "type": typ})
            if deals.count() == 0:
                continue
            for deal in deals:
                merdata = {}
                merdata.update(m)
                timing = merdata['timing']
                today = timing[datetime.datetime.today().weekday()]
                now = datetime.datetime.strptime(datetime.datetime.now().time().strftime("%H:%M"),"%H:%M")
                if datetime.datetime.strptime(today['close_time'],"%H:%M") > now and datetime.datetime.strptime(today['open_time'],"%H:%M") < now:
                    op = True
                else:
                    op = False
                if "subcat" in merdata:
                    merdata.pop("subcat")
                    merdata['subcat'] = int(category)
                price = merdata.pop("price")
                try:
                    price = int(float(re.sub("[^\d+\.]","",price).strip(".")))
                except:
                    pass    
                if merdata['address']['lat'] and merdata['address']['lng']:
                    if lat:
                        data_for_distance = {
                        "l1":float(lat),
                        "ln1":float(lon),
                        "l2":float(re.sub("[^0-9\.]","",str(merdata['address']['lat']))),
                        "ln2":float(re.sub("[^0-9\.]","",str(merdata['address']['lng'])))
                        }
                        merdata.update({"distance":distance(data_for_distance)})
                    else:
	                    merdata.update({"distance":False})
                else:
                    merdata.update({"distance":False})
                merdata.pop("cat")
                merdata.update({"cat":int(category)})
                merdata['price'] = price
                merdata.update({"open":op})
                merdata['open_time'] = today['open_time']
                merdata['close_time'] = today['close_time']
                merdata.update(deal)
                data.append(merdata)
        start = (pages-1)*10
        end = start + 10
        if end > len(data):
            end = len(data)
        if start > len(data):
            start = len(data) - 10
        if r:
            newlist = [x for x in data if x['distance']<r]
        else:
            newlist = data
        if ope:
            delta = [x for x in newlist if x['open'] is True]
        else:
            delta = newlist
        newlist = sorted(delta, key=lambda k: k[sort] if k[sort] is not False else 100,reverse=reverse)
        res = {
            "total": len(newlist),
            "data": newlist[start:end],
            "page": pages
        }
        return HttpResponse(dumps(res), content_type="application/json")
    except Exception, e:
        return HttpResponse(dumps({"exception": "error : "+str(e), "type": typ}), content_type="application/json")

@csrf_exempt
def get_totals(request):
    global db
    res = {
        "single": [],
        "group": []
    }
    for i in range(1,5):        # each category
        mers = db.merchants.find({"cat": i}, {"vendor_id": True})
        s = 0
        g = 0
        for mer in mers:
            s += db.deals.find({"vendor_id": mer['vendor_id'], "type": 'single', "rcodes" : {"$not": {"$size": 0}}}).count()
            g += db.deals.find({"vendor_id": mer['vendor_id'], "type": 'group', "rcodes" : {"$not": {"$size": 0}}}).count()
        res["single"].append(s)
        res["group"].append(g)
    return HttpResponse(dumps(res), content_type="application/json")
