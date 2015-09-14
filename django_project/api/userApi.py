from bson.json_util import dumps
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.template import Template,Context
import pymongo
from datetime import datetime
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
def fMerchant(request,user,vendor):
    try:
        collection = db.user
        #verified = collection.find_one({"userID":user})

        inc = 0
        updateQuery = {}
        if request.GET['follow'].lower() == "true":
            updateQuery = {"$set": {
                "followed."+str(vendor): datetime.now().strftime("%d/%m/%Y")
            }}
            inc = 1
        else:
            updateQuery = {"$unset": {
                "followed."+str(vendor): "blah"  # works like a charm
            }}
            inc = -1
            pass

        collection.update({"userID":user}, updateQuery, False)
        db.merchants.update_one({"vendor_id": int(vendor)}, {"$inc": {"followers": inc}})
        return HttpResponse(dumps({"success": '1'}), content_type="application/json")
    except Exception, e:
        return HttpResponse(dumps({"success": '0', 'error': "Exception: "+str(e)}),content_type="application/json")

@csrf_exempt
def user_exist(request):
    try:
        result = dict()
        data = json.loads(request.body)
        email = data['email']
        doc = db.user.find_one({"email": email})
        if doc is not None:
            result['success'] = '1'
            result['userID'] = doc['userID']
            result['name'] = doc['fname'] + ' ' + doc['lname']
            result['email'] = doc['email']
            if 'cname' in doc:
                result['cname'] = doc['cname']
            else:
                result['cname'] = ""
            regid = data['regId']
            if regid not in doc['regId']:
                db.user.update_one({"email": email}, {"$push": {"regId": regid}})

            return HttpResponse(dumps(result), content_type="application/json")
        else:
            result['success']='0'
            result['reason'] = "NO INFORMATION FOUND FOR GIVEN EMAIL : "+ email
            return HttpResponse(dumps(result), content_type="application/json")
    except Exception, e:
        return HttpResponse(dumps({"success": 0, "exception": str(e)}))
        
""" generating user ID"""
def userIdGenPartial():
    p1 = ''.join(random.choice(string.ascii_lowercase) for _ in range(2))
    p2 = ''.join(random.choice(string.digits) for _ in range(4))
    return p1 + p2

def userIdGen():
    res = userIdGenPartial()
    collection = db.user
    while db.user.find({"userID": res}).count() > 0:
        res = userIdGenPartial()
    return res
# ---------------------- #

@csrf_exempt
def signup(request):	   
    global db
    try:
        data = json.loads(request.body)
        data = data['data']
        failure = dict()
        collection = db.user
        if collection.find({"email": data['email']}).count() is not 0:
            return HttpResponse(failure,content_type="application/json")
        key = userIdGen()
        data.update({"userID":key})
        data.update({"verified":"N"})

        data['regId'] = [data['regId']]
        data['timestamp'] = datetime.now()
        collection.insert(data)
        res = { "success":'1', "userID": key }

        #mResult = conf_mail(data['cemail'], key+'_'+verification_code)
        return HttpResponse(dumps(res),content_type="application/json")
    except Exception, e:
        failure['success'] = '0'
        failure['reason'] = str(e)
        return HttpResponse(dumps(failure), content_type="application/json")

@csrf_exempt
def getdata(request):
    failure = dict()
    try:
        id = request.GET['userID']
        collection = db.user
        data = collection.find({"userID":id})
	if data.count() is 1:
            return HttpResponse(dumps(data[0]),content_type="application/json")
	else:
	    failure['success'] = '0'
	    failure['reason'] = "NO USER FOUND"
	    return HttpResponse(dumps(failure),content_type="application/json")    
    except:
        failure['success'] = '0'
        failure['reason'] = "NO USER FOUND"
        return HttpResponse(dumps(failure),content_type="application/json")

#-------------Mailing Function-----------------#
'''
def conf_mail(email,code):
    import sendgrid
    sg = sendgrid.SendGridClient('bandishshah', 'bandishshah@123')
    message = sendgrid.Mail()
    message.add_to(email)
    message.set_subject("Verify your Corporate ID")
    message.set_html("Click <a href='http://api.jlabs.co/perkkx/verifyUser/" + code + "'>Here</a> to verify your account and get all deals." )
    message.set_from('Verify <no-reply@perkkx.com>')
    return sg.send(message)
'''

def conf_mail(email, code):
    import mandrill
    mclient = mandrill.Mandrill('8kCnFImdpMfZZOyHlS7BFA')
    message = {
        'html': """
            <p>
                <a href='http://api.jlabs.co/perkkx/verifyUser/%s'>Click here</a> to verify your account
                and get all deals.
            </p>
            """ % str(code),
        'subject': "Verify your Corporate ID",
        'from_name': 'Verify <no-reply@perkkx.com>',
        'from_email': 'no-reply@perkkx.com',
        'to': [
            {'email': email}
        ]
    }
    return mclient.messages.send(message=message, async=True)

@csrf_exempt
def updateuser(request):
    global db
    failure = dict()
    try:
        data = json.loads(request.body)
        data = data['data']
        collection = db.user
        key = data['userID']
        data.pop('userID')
        verified = collection.find_one({"userID":key})
        try:
            if 'cemail' in data.keys():

                whitelist_conf = db.configuration.find_one({"name": "cemail_whitelist"})
                if whitelist_conf:
                    whitelist = whitelist_conf.get('emails', [])
                else:
                    whitelist = []
                if data['cemail'] in whitelist:
                    data['verified'] = 'Y'
                else:
                    if db.user.count({"cemail": data['cemail']}) > 0:
                        return HttpResponse(dumps({"success": 0, "reason": "This corporate email id is already registered with us"}))
                    verify = ''.join(random.choice(string.ascii_lowercase) for _ in range(4))
                    code = key + "_" + verify
                    result = conf_mail(data['cemail'],code)
                    data['veri_code'] = verify
                    if 'verified' not in verified:
                        data['verified'] = "N"
        except:
            print "hi"
        collection.update({"userID":key},{"$set": data} ,False)
        return HttpResponse(dumps({"success": '1'}),content_type="application/json")
    except:
        failure['success'] = '0'
        failure['reason'] = "UPDATATION CAN'T BE PROCEEDED"
        return HttpResponse(dumps(failure),content_type="application/json")

def resend_email(request):
    try:
        userID = request.GET['userID']
        user = db.user.find_one({"userID": userID})
        if not user:
            return HttpResponse(dumps({"success": 0, "reason": "User doesn't exist"}),content_type="application/json")
        if 'cemail' not in user:
            return HttpResponse(dumps({"success": 0, "reason": "No corporate email"}),content_type="application/json")

        if 'veri_code' in user:
            verify = user['veri_code']
        else:
            verify = ''.join(random.choice(string.ascii_lowercase) for _ in range(4))
            db.user.update_one({"userID": userID}, {"$set": {"veri_code": verify}})

        conf_mail(user['cemail'], userID + '_' + verify)
        return HttpResponse(dumps({"success": 1}),content_type="application/json")
    except Exception, e:
        return HttpResponse(dumps({"success": 0, "error": "Exception: "+str(e)}),content_type="application/json")

@csrf_exempt
def user_coupons(request,uid):
    global db
    try:
        usedDeals = db.order_data.find({"userID":uid})
        pending = []
        expired = []
        used = []
        for x in usedDeals:
            vendorData = db.merchants.find_one({"vendor_id":int(x['vendor_id'])})
            try:
                address = vendorData['address']['area']
            except:
                address = vendorData.get('web_address', '')

            dealData = db.deals.find_one({"cID":x['cID']})
            if not dealData:
                dealData = db.one_time_deals.find_one({"cID": x['cID']})

            rep = {"vendor_name":vendorData['vendor_name'],
                "address":address,
                "code":x['rcode'],
                "deal": dealData['deal'],
                "expiry":dealData.get('expiry', '1/1/2090'),
                "used_on":x['used_on'].strftime("%d/%m/%Y %H:%M:%S"),
                "status":x['ustatus'],
                "cID": x['cID'],
                "vendor_id": x['vendor_id']
            }
            if x['ustatus'] in "pending":
                pending.append(rep)
            elif x['ustatus'] in "used":
                ratingDoc = db.ratings.find_one({"cID": rep['cID'], "userID": uid}, {"rating": True,"comment": True})
                if ratingDoc:
                    rep['rating'] = ratingDoc['rating']
                    rep['comment'] = ratingDoc['comment']
                used.append(rep)
            elif x['ustatus'] in "expired":
                expired.append(rep)
        return HttpResponse(dumps({"pending":pending,"expired":expired,"used":used}),content_type="application/json")
    except Exception, e:
        failure = {"success": 0, "reason": str(e)}
        return HttpResponse(dumps(failure),content_type="application/json")

@csrf_exempt
def getFacility(request):
    failure = {"success": 0}
    if "domain" in request.GET.keys():
        domain = request.GET['domain']
        collection = db.corp
        data = list(collection.find({"domain": domain}, {"_id": False, "domain": False}))
        '''
        data = []
        search = {"domain": domain}
        temp = collection.find(search)
        if temp.count() > 0:
            for x in temp:
                x.pop("domain")
                x.pop("_id")
                data.append(x)
        '''
        if len(data) > 0:
            return HttpResponse(dumps({"success": 1, "data": data}),content_type="application/json")
        else:
            failure.update({"reason": "domain not found"})
            return HttpResponse(dumps(failure),content_type="application/json")
    else:
        failure.update({"reason": "Bad Request"})
        return HttpResponse(dumps(failure),content_type="application/json")

@csrf_exempt
def verifyUser(request,code):
    code = code.split("_")
    if len(code) == 2:
        collection = db.user
        data = collection.find_one({"userID":code[0]})
        if data:
            try:
                if data['verified'] == "Y":
                    return HttpResponse("Already Verified")
                if data['veri_code'] in code[1].strip():
                    collection.update_one({"userID":code[0]},{"$set": {"verified": 'Y'}})
                    return HttpResponse("User has been verified. Continue to app")
                else:
                    return HttpResponse("Invalid URL")
            except:
                return HttpResponse("Invalid Username")
        else:
            return HttpResponse("Invalid Username")
    else:
        return HttpResponse("Invalid Format")

def share_link(request):
    userID = request.GET.get('userID')
    if userID and db.user.count({"userID": userID}) > 0:
        db.user_share.update_one({
            "userID": userID
        }, {"$inc": {"clicked": 1}})

    return redirect("https://play.google.com/store/apps/details?id=com.jlabs.perkkxapp")

