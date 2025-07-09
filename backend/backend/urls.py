from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf import settings

base_api_url = 'api/'

urlpatterns = [
    path("admin/", admin.site.urls),
    path(base_api_url, include("core.api.urls")),
    path(base_api_url + 'account/', include("account.api.urls")),
    path(base_api_url + 'repo/', include("repo.api.urls")),
    path(base_api_url + 'course/', include("course.api.urls")),
    path(base_api_url + 'login/',include("login.api.urls")),
    # path(base_api_url + 'authentication/',include("authentication.api.urls")),
]

if bool(settings.DEBUG):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
 
