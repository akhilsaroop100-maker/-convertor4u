from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from converters.sitemaps import CategorySitemap, PairSitemap, StaticSitemap

sitemaps = {"static": StaticSitemap, "categories": CategorySitemap, "conversions": PairSitemap}
urlpatterns = [
    path("admin/", admin.site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("", include("converters.urls")),
]

handler404 = "converters.views.page_not_found"
handler500 = "converters.views.server_error"
