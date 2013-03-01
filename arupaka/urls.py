from django.conf.urls import patterns, url

urlpatterns = patterns('',
     url(r'^$', 'arupaka.views.index', name='index'),
     url(r'^play$', 'arupaka.views.play', name='play'),
     url(r'^stop', 'arupaka.views.stop', name='stop'),
)
