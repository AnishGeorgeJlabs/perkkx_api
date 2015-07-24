from data import cl_blocked, basic_success, jsonResponse
from django.views.decorators.csrf import csrf_exempt

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

    cl_blocked.insert_one({
        "number": num,
        "language": lan
    })

    return basic_success
