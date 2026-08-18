from django.conf import settings


class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        allowed = ("/maintenance/", "/healthz/", "/admin/", settings.STATIC_URL)
        if settings.MAINTENANCE_MODE and not request.path.startswith(allowed):
            from .views import maintenance
            return maintenance(request)
        return self.get_response(request)
