from data import jsonResponse
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
