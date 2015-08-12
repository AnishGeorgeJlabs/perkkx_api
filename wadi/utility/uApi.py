from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

def reference(request):
    filename = request.GET['file']
    context = {
        'filename': filename
    }
    return render(request, 'wadi/file.html',context)

def upload(request):
    file = request.FILES['upload']
    name = request.POST['file']