from django.urls import include, path

from .views import HTTPLogCRUDL

urlpatterns = [path("", include(HTTPLogCRUDL().as_urlpatterns()))]
