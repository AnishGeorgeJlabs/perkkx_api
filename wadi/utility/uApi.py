from django.http import HttpResponse
from django.shortcuts import render

def reference(request):
    filename = request.GET['file']
    context = {
        'filename': filename
    }
    return render(request, 'wadi/file.html',context)

def upload(request):
    file = request.FILES['upload']
    name = request.POST['file']