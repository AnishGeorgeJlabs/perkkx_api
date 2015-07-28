from django.conf.urls import url, patterns
from . import api

urlpatterns = patterns(
    '',
    url(r'^$', api.test, name='test'),
)
