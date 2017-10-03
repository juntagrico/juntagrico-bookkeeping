"""
test URL Configuration for juntagrico_bookkeeping development
"""
from django.conf.urls import include, url
from django.contrib import admin
import juntagrico
import juntagrico_bookkeeping.views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('juntagrico.urls')),
    url(r'^', include('juntagrico_bookkeeping.urls')),
    url(r'^$', juntagrico.views.home),
]
