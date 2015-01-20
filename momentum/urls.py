from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'momentum.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', 'momentum.views.dashboard', name='dashboard'),
    url(r'^(.+?)/timer/$', 'momentum.views.timer', name='timer'),
    url(r'^(.+?)/$', 'momentum.views.goal', name='goal'),
)
