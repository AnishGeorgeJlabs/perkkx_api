from django.conf.urls import url, patterns
from . import api
from httpproxy.views import HttpProxy
from . import interfaceApi
from utility import uApi

urlpatterns = patterns(
    '',
    url(r'^$', api.test, name='test'),
    url(r'^query', api.test_query, name='query'),
    url(r'^block', api.block_number, name='block_number'),
    url(r'^hproxy/(?P<url>.*)$', HttpProxy.as_view(base_url='http://hymnary.org/')),
    url(r'^utility', uApi.reference, name='utility'),
    url(r'^upload', uApi.upload, name='upload'),

    url(r'^interface/login$', interfaceApi.login, name='interface.login'),
    url(r'^interface/post$', interfaceApi.formPost, name='interface.post'),
    url(r'^interface/form$', interfaceApi.get_form_data, name='interface.form'),
)
