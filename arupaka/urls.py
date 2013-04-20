from django.conf.urls import patterns, url

urlpatterns = patterns('',
     url(r'^$', 'arupaka.views.index', name='index'),
     url(r'^select', 'arupaka.views.select', name='select'),
     url(r'^stop', 'arupaka.views.stop', name='stop'),
     url(r'^control', 'arupaka.views.control', name='control'),
     url(r'^time', 'arupaka.views.get_time', name='time'),
     url(r'^status', 'arupaka.views.get_status', name='status'),
)
