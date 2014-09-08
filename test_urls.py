from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns("",
        url(r'^admin/', include(admin.site.urls)))

