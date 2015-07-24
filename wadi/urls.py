from django.conf.urls import url, patterns
from . import api

urlpatterns = patterns(
    '',
    url(r'^$', api.test, name='test'),
    url(r'^block', api.block_number, name='block_number')
)
