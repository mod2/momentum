from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'momentum.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/', 'django.contrib.auth.views.login', { 'template_name': 'login.html' }, name='login'),
    url(r'^logout/', 'django.contrib.auth.views.logout', { 'template_name': 'logout.html', 'next_page': '/login/' }, name='logout'),

    url(r'^$', 'momentum.views.dashboard', name='dashboard'),
    url(r'^update-goals/$', 'momentum.views.update_goals', name='update_goals'),
    url(r'^status/$', 'momentum.views.status', name='status'),
    url(r'^(.+?)/timer/$', 'momentum.views.timer', name='timer'),
    url(r'^(.+?)/save/$', 'momentum.views.save', name='save_amount'),
    url(r'^(.+?)/$', 'momentum.views.goal', name='goal'),
)
