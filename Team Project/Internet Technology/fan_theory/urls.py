from django.conf.urls import url, include
from fan_theory import views
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.shortcuts import render, redirect

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'about/$', views.about, name='about'),
	url(r'^add_category/$', views.add_category, name='add_category'),
	url(r'^category_list/$', views.show_category_list, name='category_list'),
	url(r'^category/(?P<category_name_slug>[\w\-]+)$', views.show_category, name='show_category'),
	url(r'^category/(?P<category_name_slug>[\w\-]+)/add_fan_theory/$', views.add_fan_theory, name='add_fan_theory'),
	url(r'^category/(?P<category_name_slug>[\w\-]+)/(?P<fan_theory_name_slug>[\w\-]+)/$', views.show_fan_theory, name='show_fan_theory'),
	url(r'^register/$', views.register,name='register'),
	url(r'^login/$', views.user_login, name='login'),
	url(r'^logout/$', views.user_logout, name='logout'),
	url(r'^user_profile/(?P<user_profile_name>[\w\-]+)/$', views.show_user_profile, name='show_user_profile'),
	url(r'^edit_profile/$', views.edit_user_profile, name='edit_user_profile'),
	url(r'^vote/$', views.vote, name='vote'),
	url(r'^my_comments/$', views.my_comments, name='my_comments'),
	url(r'^oauth/', include('social_django.urls', namespace='social')),
	url(r'^settings/$', views.settings, name='settings'),
    url(r'^settings/password/$', views.password, name='password'),
]
