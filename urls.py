from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^login/', 'canvas.views.login'),
    url(r'^yay/', 'canvas.views.yay'),
    # Examples:
    # url(r'^$', 'facebook_teste.views.home', name='home'),
    # url(r'^facebook_teste/', include('facebook_teste.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
