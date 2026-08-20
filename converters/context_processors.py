from django.conf import settings


def public_site_settings(request):
    return {
        "public_operator_name": settings.PUBLIC_OPERATOR_NAME,
        "public_editor_name": settings.PUBLIC_EDITOR_NAME,
        "public_contact_email": settings.PUBLIC_CONTACT_EMAIL,
        "google_site_verification": settings.GOOGLE_SITE_VERIFICATION,
        "adsense_publisher_id": settings.ADSENSE_PUBLISHER_ID,
        "adsense_enabled": settings.ADSENSE_ENABLED,
    }
