from bson.json_util import dumps
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import Template,Context
import pymongo
from datetime import datetime
import random
import string
import json
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client import tools
import gspread
import os
from . import db

failure = dumps({ "success": 0 })
'''
dbclient = pymongo.MongoClient("mongodb://45.55.232.5:27017")
db = dbclient.perkkx
'''

def get_worksheet(i):
    storage = Storage("creds.dat")
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        flags = tools.argparser.parse_args(args=[])
        flow = flow_from_clientsecrets("client_secret.json", scope=["https://spreadsheets.google.com/feeds"])
        credentials = tools.run_flow(flow, storage, flags)
    if credentials.access_token_expired:
        credentials.refresh(httplib2.Http())
    gc = gspread.authorize(credentials)

    wks = gc.open_by_key('1ahDHKmAuvCSetymcEu6W_FS0W9ycksFrOGsapRj5UjM')
    return wks.get_worksheet(i)

@csrf_exempt
def addData(response,rowID):
    #return HttpResponse(os.getcwd())
    worksheet = get_worksheet(0)
    val = worksheet.get_all_records()
    row = val[int(rowID) - 2]
    db.new_deal.insert(row)
    return HttpResponse(dumps(row), content_type='application/json')