from django.conf.urls import patterns, url
from rango import views

urlplatterns = platterns ('',
	url(r'^$', views.index, name = 'index'))