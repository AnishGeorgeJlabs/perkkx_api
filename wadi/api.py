from data import cl_blocked, basic_success, jsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def test(request):
    if request.method == "GET":
        extra = {
            "method": "GET",
            "requestData": request.GET
        }
    else:
        extra = {
            "method": "POST",
            "requestData": request.body
        }
    return jsonResponse({
        "result": True,
        "Message": "Test api, ECHO",
        "extra": extra
    })


@csrf_exempt
def block_number(request):
    num = request.GET['number']
    lan = 'English' if request.GET['language'].lower() in 'english' else 'Arabic'
    data = {
        "number": num,
        "language": lan
    }
    if cl_blocked.count(data) == 0:
        cl_blocked.insert_one(data)

    return basic_success

@csrf_exempt
def test_query(request):
    return jsonResponse({
        "pipeline": ['category', 'customer'],
        'options': {
            'mode': 'all',
            'cat_list': ['Sports Shoes', 'Pumps']
        }
    })

