from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    url(r'^gestionDNS$', views.ListeDNS.as_view(), name="page_DNS"),
    url(r'^switchDNS/(?P<ordiId>[0-9a-zA-Z]+)$', views.changeDNSactif, name="change_DNS"),
    url(r'^mailings$', views.MailingList.as_view(), name="page_mailing"),
]
