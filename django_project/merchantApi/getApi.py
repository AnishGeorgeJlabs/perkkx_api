from django.views.decorators.csrf import csrf_exempt
from django.template import Template, Context
import pymongo
from datetime import datetime, timedelta
import calendar
from .data_query import db, get_data, response
import time
import re


def _get_unix_timestamp(data):  # data is datetime
    return int(data.strftime("%s")) * 1000


def get_dealOpts(vendor_id, userID):
    deals = db.deals.find({"vendor_id": vendor_id})
    deals += [
        deal for deal in db.one_time_deals.find({"vendor_id": vendor_id})
        if db.order_data.count({"cID": deal['cID'], "userID": userID}) == 0
    ]
    dealOpts = []
    for d in deals:
        if datetime.strptime(d["expiry"], "%d/%m/%Y") > datetime.now():
            dealOpts.append({
                "deal": d["deal"],
                "cID": d["cID"]
            })
    return dealOpts


@csrf_exempt
def validate_code(request):
    invalid_code = {"valid": False, "error": "Invalid code"}
    try:
        vendor_id = int(request.GET['vendor_id'])
        code = request.GET['rcode'].lower()
        res = db.order_data.find_one({"rcode": code, "userID": code[:-2], "vendor_id": vendor_id},
                                     {"_id": False, "used_on": True, "rcode": True, "cID": True, "userID": True,
                                      "mstatus": True})
        if res:
            if res["mstatus"] == "pending" or res['mstatus'] == 'disputed':
                res.pop("mstatus")

                cid = res['cID']
                dealOpts = get_dealOpts(vendor_id, code[:-2])

                res['dealOpts'] = dealOpts

                indexArr = [idx for idx, val in enumerate(dealOpts) if val['cID'] == cid]
                if indexArr:
                    res['selectedIndex'] = indexArr[0]
                else:
                    res['selectedIndex'] = 0

                res["used_on"] = _get_unix_timestamp(res["used_on"])
                return response({"valid": True, "data": res})
            else:
                return response(invalid_code)
        else:
            user = db.user.find_one({"userID": code[:-2]})
            if not user:
                return response({"valid": False, "error": "Wrong user id " + code[:-2]})

            if db.order_data.count({"rcode": code, "mstatus": {"$ne": "used"}}) > 0:
                return response({"valid": False, "error": "repeated rcode: "})

            dealOpts = get_dealOpts(vendor_id)
            if not dealOpts:
                return response({"valid": False, "error": "No dealOpts"})

            result = {
                "used_on": int(time.time() * 1000),
                "rcode": code,
                "userID": code[:-2],
                "dealOpts": dealOpts,
                "selectedIndex": 0
            }
            return response({"valid": True, "data": result})

    except Exception, e:
        return response({"valid": False, "error": "Invalid code and error " + str(e)})


@csrf_exempt
def get(request, typ, vendor_id):
    """GET requests for typ [pending, used, expired, disputed] and vendor_id"""
    expiryLimit = timedelta(weeks=(6 * 4))  # 6 months
    today = datetime.now()

    if typ not in ['pending', 'used', 'expired', 'disputed']:
        return response({"error": "Unknown type"})

    page, total_pages, init_data = get_data(request, int(vendor_id), typ)

    error = ""
    result_list = []
    for data in init_data:
        # Step 1. Get the deal value
        deal = db.deals.find_one({"cID": data["cID"]}, {"deal": True, "expiry": True})  # common

        if not deal:
            deal = db.one_time_deals.find_one({"cID": data['cID']}, {"deal": True, "expiry": True})
            if not deal:
                error += "dealMiss: " + data["cID"] + "   "
                continue  # Testing use case, when we have inconsistent database
        data["deal"] = deal["deal"]

        # Step 2. Get expiry
        if typ not in ["used"] and 'expiry' in deal:
            expiry = datetime.strptime(deal['expiry'], "%d/%m/%Y")
            if expiry - today < expiryLimit:
                data['expiry'] = _get_unix_timestamp(expiry)

        # Step 3. Get used_on
        if typ != "expired":
            data["used_on"] = _get_unix_timestamp(data["used_on"])
        else:
            del data["used_on"]

        # Step 4. Change submitted_on to proper format
        if typ == "used":
            data["submitted_on"] = _get_unix_timestamp(data["submitted_on"])

        result_list.append(data)

    result = {
        "page": page,
        "total_pages": total_pages,
        "data": result_list
    }
    if error != "":
        result.update({"debug": error})

    return response(result)


@csrf_exempt
def get_count(request, vendor_id):
    "GET the counts for each type of deals in used, expired, disputed"
    try:
        collection = db.order_data
        result = {
            "used": collection.count({"vendor_id": int(vendor_id), "mstatus": "used"}),
            "disputed": collection.count({"vendor_id": int(vendor_id), "mstatus": "disputed"})
        }
        return response(result)
    except Exception, e:
        return response({"error": str(e)})
