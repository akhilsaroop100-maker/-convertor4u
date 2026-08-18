from django.urls import path
from . import views
urlpatterns = [
    path("", views.home, name="home"), path("robots.txt", views.robots, name="robots"),
    path("unit-systems/", views.reference_page, {"page_slug": "unit-systems"}, name="unit_systems"),
    path("about/", views.reference_page, {"page_slug": "about"}, name="about"),
    path("terms/", views.reference_page, {"page_slug": "terms"}, name="terms"),
    path("privacy/", views.reference_page, {"page_slug": "privacy"}, name="privacy"),
    path("accuracy/", views.reference_page, {"page_slug": "accuracy"}, name="accuracy"),
    path("contact/", views.contact, name="contact"),
    path("site-map/", views.site_map, name="site_map"),
    path("api/convert/", views.convert_api, name="convert_api"),
    path("api/query/", views.query_api, name="query_api"),
    path("api/categories/<slug:category_slug>/units/", views.units_api, name="units_api"),
    path("healthz/", views.health, name="health"),
    path("maintenance/", views.maintenance, name="maintenance"),
    path("api/multi-convert/", views.multi_convert_api, name="multi_convert_api"),
    path("api/currency/history/", views.currency_history_api, name="currency_history_api"),
    path("<slug:category_slug>/", views.category, name="category"),
    path("<slug:category_slug>/<slug:pair_slug>/", views.conversion, name="conversion"),
]
