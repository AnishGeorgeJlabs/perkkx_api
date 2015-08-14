from data import basic_success, jsonResponse, db, basic_failure, basic_error
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime
from bson.objectid import ObjectId
from external.sheet import get_scheduler_sheet

@csrf_exempt
def login(request):
    try:
        data = json.loads(request.body)
        if db.credentials.count({"username": data['username'], "password": data['password']}) > 0:
            return jsonResponse({"success": True})
        else:
            return jsonResponse({"success": False})
    except Exception, e:
        return basic_error(e)

@csrf_exempt
def formPost(request):
    try:
        data = json.loads(request.body)
        # Do processing here

        campaign = data['campaign_config']
        date = campaign['date']
        time = datetime.strptime(campaign['time'], "%H:%M")
        hour = time.hour
        minute = time.minute
        english = campaign['text']['english']
        arabic = campaign['text']['arabic']
        result = db.queries.insert_one(data)
        url = 'http://45.55.72.208/wadi/query?id='+str(result.inserted_id)
        row = ['Once', 'external', date, hour, minute, english, arabic, url]
        wrk_sheet = get_scheduler_sheet()

        size = len(wrk_sheet.get_all_values())
        wrk_sheet.insert_row(row, size+1)

        res = {'success': True, 'data_received': data, "row created ": row}
        return jsonResponse(res)
    except Exception, e:
        return basic_error(e)

def query(request):
    id = request.GET['id']

    obj = db.queries.find_one({"_id": ObjectId(id)})
    if obj:
        options = obj['target_config']
        if 'customer' not in options:
            options['mode'] = 'all'
        else:
            cust = options['customer']
            if len(cust) == 2:
                options['mode'] = 'all'
            else:
                options['mode'] = cust[0]
        pipeline = [k for k, v in options.items if k != 'mode']
        pipeline.append('customer')

        return jsonResponse({"pipeline": pipeline, "options": options})
    else:
        raise Http404

def get_form_data(request):
    data = db.form.find({}, {"_id": False})
    '''
    result = {}
    for item in data:
        result[item['operation']] = item
    '''
    return jsonResponse(data)
