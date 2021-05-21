from django.conf import settings
from django.conf.urls import handler404, handler500
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

handler404 = 'service_pages.views.page_not_found'  # noqa
handler500 = 'service_pages.views.server_error'  # noqa
handler400 = 'service_pages.views.bad_request'  # noqa

urlpatterns = [
    path('master-chef/', admin.site.urls),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('service/', include('service_pages.urls')),
    path('api/', include('api.urls')),
    path('', include('recipes.urls')),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
