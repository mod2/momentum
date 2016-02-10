from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views

from momentum import views as momentum_views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/', auth_views.login, { 'template_name': 'login.html' }, name='login'),
    url(r'^logout/', auth_views.logout, { 'template_name': 'logout.html', 'next_page': '/login/' }, name='logout'),

    url(r'^$', momentum_views.dashboard, name='dashboard'),
    url(r'^organize/$', momentum_views.organize, name='organize'),
    url(r'^update-goals/$', momentum_views.update_goals, name='update_goals'),
    url(r'^status/$', momentum_views.status, name='status'),
    url(r'^(.+?)/timer/$', momentum_views.timer, name='timer'),
    url(r'^(.+?)/save/$', momentum_views.save, name='save_amount'),
    url(r'^(.+?)/$', momentum_views.goal, name='goal'),
]
