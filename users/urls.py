from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^registration/$', 'users.views.registration', name='registration'),
    url(r'^login/$', 'users.views.login', name='login'),
    url(r'^login_page/$', 'users.views.login_view', name='login'),
    url(r'^logout/$', 'users.views.logout', name='logout'),
    url(r'^update/$', 'users.views.update', name='update'),

    url(r'^mypage/$', 'users.views.mypage_view', name='mypage'),
    url(r'^mypage/(?P<page_num>(\d+))/$', 'users.views.mypage_view', name='mypage'),

)