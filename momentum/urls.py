from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views

from momentum import views as momentum_views

urlpatterns = [
    url(r'^meta/admin/', include(admin.site.urls)),
    url(r'^login/', auth_views.login, { 'template_name': 'login.html' }, name='login'),
    url(r'^logout/', auth_views.logout, { 'template_name': 'logout.html', 'next_page': '/login/' }, name='logout'),

    url(r'^$', momentum_views.dashboard, name='dashboard'),

    url(r'^(?P<context_slug>[^\/]+)/organize/$', momentum_views.organize, name='organize'),
    url(r'^(?P<context_slug>[^\/]+)/update-goals/$', momentum_views.update_goals, name='update_goals'),
    url(r'^(?P<context_slug>[^\/]+)/status/$', momentum_views.status, name='status'),
    url(r'^(?P<context_slug>[^\/]+)/id/(?P<goal_id>[^\/]+)/timer/$', momentum_views.timer, name='timer'),
    url(r'^(?P<context_slug>[^\/]+)/id/(?P<goal_id>[^\/]+)/save/$', momentum_views.save, name='save_amount'),
    url(r'^(?P<context_slug>[^\/]+)/id/(?P<goal_id>[^\/]+)/$', momentum_views.goal, name='goal'),
    url(r'^(?P<context_slug>[^\/]+)/$', momentum_views.context_detail, name='context'),
]
