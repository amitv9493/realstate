from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include
from django.urls import path
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.views import SpectacularSwaggerView

from realstate_new.api.notification.views import hello
from realstate_new.master.views import MetaDataView

# from realstate_new.master.views import protected_media_view  # noqa: ERA001

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("silk/", include("silk.urls", namespace="silk")),
    # path("media/<path:file_path>", protected_media_view, name="protected_media"),  # noqa: ERA001
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]
if settings.DEBUG:
    # Static file serving when using Gunicorn + Uvicorn for local web socket development
    urlpatterns += staticfiles_urlpatterns()
# API URLS
urlpatterns += [
    # API base url
    path("api/", include("config.api_router")),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),
    path(
        "metadata",
        MetaDataView.as_view(),
    ),
    path("hello", hello),
]
