from urllib.parse import parse_qs, urlparse
import sys

from django.test import TestCase, override_settings
from django.urls import reverse
from unittest import skipIf


@override_settings(
    SOCIALACCOUNT_PROVIDERS={
        "google": {
            "APP": {
                "client_id": "test-client-id",
                "secret": "test-client-secret",
                "key": "",
            }
        }
    }
)
@skipIf(
    sys.version_info >= (3, 14),
    "Django 4.2 test client context-copy is incompatible with Python 3.14 in this environment.",
)
class GoogleLoginUrlTests(TestCase):
    def test_google_login_url_includes_client_id(self):
        response = self.client.get(reverse("google_login"), HTTP_HOST="localhost:8000")
        self.assertEqual(response.status_code, 302)
        query = parse_qs(urlparse(response["Location"]).query)
        self.assertEqual(query.get("client_id"), ["test-client-id"])

    def test_google_login_url_uses_request_host_for_redirect(self):
        response = self.client.get(reverse("google_login"), HTTP_HOST="localhost:8000")
        self.assertEqual(response.status_code, 302)
        query = parse_qs(urlparse(response["Location"]).query)
        self.assertEqual(
            query.get("redirect_uri"),
            ["http://localhost:8000/accounts/google/login/callback/"],
        )
