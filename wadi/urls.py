from django.conf.urls import url, patterns
from . import api
from httpproxy.views import HttpProxy

urlpatterns = patterns(
    '',
    url(r'^$', api.test, name='test'),
    url(r'^query', api.test_query, name='query'),
    url(r'^block', api.block_number, name='block_number'),
    url(r'^hproxy/(?P<url>.*)$', HttpProxy.as_view(base_url='http://hymnary.org/'))
)
