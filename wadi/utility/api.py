from django.http import HttpResponse
from django.shortcuts import render

def reference(request):
    filename = request.GET['file']
    context = {
        'filename': filename
    }
    return render(request, './templates/index.html',context)
