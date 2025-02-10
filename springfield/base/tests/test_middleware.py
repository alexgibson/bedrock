# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from contextlib import suppress
from importlib import reload
from unittest import mock

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.test import Client, RequestFactory, TestCase as DjangoTestCase
from django.test.utils import override_settings
from django.urls import reverse

import csp.constants
import pytest
from freezegun import freeze_time
from jinja2.exceptions import UndefinedError
from markus.testing import MetricsMock
from pytest_django.asserts import assertTemplateUsed

from springfield.base.middleware import (
    CacheMiddleware,
    ClacksOverheadMiddleware,
    CSPMiddlewareByPathPrefix,
    HostnameMiddleware,
    SpringfieldLangCodeFixupMiddleware,
    SpringfieldLocaleMiddleware,
)
from springfield.base.tests import TestCase


@override_settings(
    MIDDLEWARE=["springfield.base.middleware.MetricsStatusMiddleware"],
    ROOT_URLCONF="springfield.base.tests.urls",
)
class TestMetricsStatusMiddleware(DjangoTestCase):
    def test_200(self):
        with MetricsMock() as mm:
            resp = Client().get(reverse("index"))
            assert resp.status_code == 200
            mm.assert_incr_once("response.status", tags=["status_code:200"])

    def test_302(self):
        with MetricsMock() as mm:
            resp = Client().get(reverse("redirect"))
            assert resp.status_code == 302
            mm.assert_incr_once("response.status", tags=["status_code:302"])

    def test_returns_400(self):
        with MetricsMock() as mm:
            with suppress(UndefinedError):
                resp = Client().get(reverse("returns_400"))
                assert resp.status_code == 400
            mm.assert_incr_once("response.status", tags=["status_code:400"])

    def test_raises_400_bad_request(self):
        with MetricsMock() as mm:
            with suppress(UndefinedError):
                resp = Client().get(reverse("raises_400_bad_request"))
                assert resp.status_code == 400
            mm.assert_incr_once("response.status", tags=["status_code:400"])

    def test_raises_400_multipart_parser_error(self):
        with MetricsMock() as mm:
            with suppress(UndefinedError):
                resp = Client().get(reverse("raises_400_multipart_parser_error"))
                assert resp.status_code == 400
            mm.assert_incr_once("response.status", tags=["status_code:400"])

    def test_raises_400_suspicious_operation(self):
        with MetricsMock() as mm:
            with suppress(UndefinedError):
                resp = Client().get(reverse("raises_400_suspicious_operation"))
                assert resp.status_code == 400
            mm.assert_incr_once("response.status", tags=["status_code:400"])

    def test_raises_403_permission_denied(self):
        with MetricsMock() as mm:
            with suppress(UndefinedError):
                resp = Client().get(reverse("raises_403_permission_denied"))
                assert resp.status_code == 403
            mm.assert_incr_once("response.status", tags=["status_code:403"])

    def test_raises_404(self):
        with MetricsMock() as mm:
            with suppress(UndefinedError):
                resp = Client().get(reverse("raises_404"))
                assert resp.status_code == 404
            mm.assert_incr_once("response.status", tags=["status_code:404"])

    def test_returns_404(self):
        with MetricsMock() as mm:
            resp = Client().get(reverse("returns_404"))
            assert resp.status_code == 404
            mm.assert_incr_once("response.status", tags=["status_code:404"])

    def test_raises_500(self):
        with MetricsMock() as mm:
            with suppress(UndefinedError):
                resp = Client().get(reverse("raises_500"))
                assert resp.status_code == 500
            mm.assert_incr_once("response.status", tags=["status_code:500"])

    def test_returns_500(self):
        with MetricsMock() as mm:
            resp = Client().get(reverse("returns_500"))
            assert resp.status_code == 500
            mm.assert_incr_once("response.status", tags=["status_code:500"])


@override_settings(
    MIDDLEWARE=["springfield.base.middleware.MetricsViewTimingMiddleware"],
    ROOT_URLCONF="springfield.base.tests.urls",
    ENABLE_METRICS_VIEW_TIMING_MIDDLEWARE=True,
)
class TestMetricsViewTimingMiddleware(DjangoTestCase):
    @override_settings(ENABLE_METRICS_VIEW_TIMING_MIDDLEWARE=False)
    def test_200_disabled(self):
        with MetricsMock() as mm:
            resp = Client().get(reverse("index"))
            assert resp.status_code == 200
            mm.assert_not_timing("view.timings")

    def test_200(self):
        with MetricsMock() as mm:
            resp = Client().get(reverse("index"))
            assert resp.status_code == 200
            mm.assert_timing_once(
                "view.timings",
                tags=["view_path:springfield.base.tests.urls.index.GET", "module:springfield.base.tests.urls.GET", "method:GET", "status_code:200"],
            )

    def test_302(self):
        with MetricsMock() as mm:
            resp = Client().get(reverse("redirect"))
            assert resp.status_code == 302
            mm.assert_timing_once(
                "view.timings",
                tags=[
                    "view_path:springfield.base.tests.urls.redirect.GET",
                    "module:springfield.base.tests.urls.GET",
                    "method:GET",
                    "status_code:302",
                ],
            )

    def test_raises_404(self):
        with MetricsMock() as mm:
            with suppress(UndefinedError):
                resp = Client().get(reverse("raises_404"))
                assert resp.status_code == 404
            mm.assert_timing_once(
                "view.timings",
                tags=[
                    "view_path:springfield.base.tests.urls.raises_404.GET",
                    "module:springfield.base.tests.urls.GET",
                    "method:GET",
                    "status_code:404",
                ],
            )

    def test_returns_404(self):
        with MetricsMock() as mm:
            resp = Client().get(reverse("returns_404"))
            assert resp.status_code == 404
            mm.assert_timing_once(
                "view.timings",
                tags=[
                    "view_path:springfield.base.tests.urls.returns_404.GET",
                    "module:springfield.base.tests.urls.GET",
                    "method:GET",
                    "status_code:404",
                ],
            )

    def test_raises_500(self):
        with MetricsMock() as mm:
            with suppress(UndefinedError):
                resp = Client().get(reverse("raises_500"))
                assert resp.status_code == 500
            mm.assert_timing_once(
                "view.timings",
                tags=[
                    "view_path:springfield.base.tests.urls.raises_500.GET",
                    "module:springfield.base.tests.urls.GET",
                    "method:GET",
                    "status_code:500",
                ],
            )

    def test_returns_500(self):
        with MetricsMock() as mm:
            resp = Client().get(reverse("returns_500"))
            assert resp.status_code == 500
            mm.assert_timing_once(
                "view.timings",
                tags=[
                    "view_path:springfield.base.tests.urls.returns_500.GET",
                    "module:springfield.base.tests.urls.GET",
                    "method:GET",
                    "status_code:500",
                ],
            )


@pytest.mark.parametrize(
    "request_path, expected_status_code, expected_dest, expected_request_locale",
    (
        (
            "/",
            302,
            "/de/",  # because accept-language header has de as default lang,
            None,
        ),
        ("/en-us/", 302, "/en-US/", None),
        ("/en-US/", 200, None, "en-US"),
        ("/de/", 200, None, "de"),
        ("/en-US/i/am/a/path/", 200, None, "en-US"),
        ("/de/i/am/a/path/", 200, None, "de"),
        ("/en-us/path/to/thing/", 302, "/en-US/path/to/thing/", None),
        ("/de-AT/path/to/thing/", 302, "/de/path/to/thing/", None),
        ("/es-mx/path/here?to=thing&test=true", 302, "/es-MX/path/here?to=thing&test=true", None),
        ("/en-us/path/to/an/éclair/", 302, "/en-US/path/to/an/%C3%A9clair/", None),
        ("/it/path/to/an/éclair/", 200, None, "it"),
        ("/sco/", 200, None, "sco"),
        ("/de/path/to/thing/?lang=fr", 302, "/fr/path/to/thing/", None),
        ("/de/path/to/thing/?lang=vv", 302, "/en-US/path/to/thing/", None),
        ("/de/path/to/thing/?lang", 302, "/en-US/path/to/thing/", None),
        ("/de/path/to/thing/?lang=fr&test=true&foo=bar", 302, "/fr/path/to/thing/?test=true&foo=bar", None),
    ),
    ids=[
        "Bare root path",
        "Lowercase lang code for root path",
        "No change needed for root path with good locale 1",
        "No change needed for root path with good locale 2",
        "No change needed for deep path with good locale 1",
        "No change needed for deep path with good locale 2",
        "Lowercase lang code for deeper path",
        "Unsuported lang goes to root supported lang code",
        "Querystrings are preserved during fixup",
        "Unicode escaped during fixup",
        "Unicode accepted during pass-through",
        "Three-letter locale acceptable",
        "?lang querystring for valid locale",
        "?lang querystring for invalid locale",
        "?lang querystring with no value",
        "?lang querystring for valid locale and further querystrings",
    ],
)
def test_SpringfieldLangCodeFixupMiddleware(
    request_path,
    expected_status_code,
    expected_dest,
    expected_request_locale,
    rf,
):
    request = rf.get(
        request_path,
        HTTP_ACCEPT_LANGUAGE="de-DE,en-GB;q=0.4,en-US;q=0.2",
    )

    middleware = SpringfieldLangCodeFixupMiddleware(get_response=HttpResponse)

    resp = middleware.process_request(request)

    if resp:
        assert resp.status_code == 302
        assert resp.headers["location"] == expected_dest
        assert resp.headers["vary"].lower() == "accept-language"
    else:
        # the request will have been annotated by the middleware
        assert request.locale == expected_request_locale


@pytest.mark.django_db
def test_SpringfieldLangCodeFixupMiddleware__no_lang_info_gets_locale_page__end_to_end(client):
    """Quick end-to-end test confirming the custom 404-locale template is rendered
    at the / path when there is no accept-language header"""

    resp = client.get("/", follow=False)
    assert "HTTP_ACCEPT_LANGUAGE" not in resp.request
    assert resp.status_code == 200
    # this template use actually happens in lib.l10n_utils.render
    assertTemplateUsed(resp, "404-locale.html")


@mock.patch("django.middleware.locale.LocaleMiddleware.process_request")
@mock.patch("django.middleware.locale.LocaleMiddleware.process_response")
def test_SpringfieldLocaleMiddleware_skips_super_call_if_path_is_for_root_and_has_no_lang_clues(
    mock_django_localemiddleware_process_response,
    mock_django_localemiddleware_process_request,
    rf,
):
    fake_request = rf.get("/")
    assert "HTTP_ACCEPT_LANGUAGE" not in fake_request
    middleware = SpringfieldLocaleMiddleware(fake_request)
    middleware.process_request(fake_request)
    assert not mock_django_localemiddleware_process_request.called

    fake_response = mock.Mock(name="fake response")
    middleware.process_response(fake_request, fake_response)
    assert not mock_django_localemiddleware_process_response.called


@pytest.fixture
def csp_middleware():
    return CSPMiddlewareByPathPrefix(lambda req: HttpResponse())


@override_settings(
    CONTENT_SECURITY_POLICY={"DIRECTIVES": {"default-src": ["default.com"]}},
    CONTENT_SECURITY_POLICY_REPORT_ONLY=None,
)
def test_no_csp_path_overrides(csp_middleware):
    rf = RequestFactory()
    request = rf.get("/u/thedude/")
    response = csp_middleware.process_response(request, HttpResponse())
    assert not hasattr(response, "_csp_config")
    assert not hasattr(response, "_csp_config_ro")
    assert csp.constants.HEADER in response.headers
    assert csp.constants.HEADER_REPORT_ONLY not in response.headers
    assert response.headers[csp.constants.HEADER] == "default-src default.com"


@override_settings(
    CONTENT_SECURITY_POLICY={"DIRECTIVES": {"default-src": ["default.com"]}},
    CONTENT_SECURITY_POLICY_REPORT_ONLY=None,
    CSP_PATH_OVERRIDES={"/u/thedude": {"DIRECTIVES": {"default-src": ["override.com"]}}},
)
def test_csp_path_overrides(csp_middleware):
    rf = RequestFactory()
    request = rf.get("/u/thedude/")
    response = csp_middleware.process_response(request, HttpResponse())
    assert response._csp_config == {"default-src": ["override.com"]}
    assert not hasattr(response, "_csp_config_ro")
    assert csp.constants.HEADER in response.headers
    assert csp.constants.HEADER_REPORT_ONLY not in response.headers
    assert response.headers[csp.constants.HEADER] == "default-src override.com"


@override_settings(
    CONTENT_SECURITY_POLICY={"DIRECTIVES": {"default-src": ["default.com"]}},
    CONTENT_SECURITY_POLICY_REPORT_ONLY=None,
    CSP_PATH_OVERRIDES={"/u/thedude": {"DIRECTIVES": {}}},
)
def test_csp_path_overrides_nullify(csp_middleware):
    rf = RequestFactory()
    request = rf.get("/u/thedude/")
    response = csp_middleware.process_response(request, HttpResponse())
    assert response._csp_config == {}
    assert not hasattr(response, "_csp_config_ro")
    assert csp.constants.HEADER not in response.headers
    assert csp.constants.HEADER_REPORT_ONLY not in response.headers


@override_settings(
    CONTENT_SECURITY_POLICY={"DIRECTIVES": {"default-src": ["default.com"]}},
    CONTENT_SECURITY_POLICY_REPORT_ONLY={"DIRECTIVES": {"default-src": ["default.com", "other.com"]}},
    CSP_PATH_OVERRIDES_REPORT_ONLY={"/u/thedude": {"DIRECTIVES": {"default-src": ["override.com"]}}},
)
def test_csp_path_overrides_report_only(csp_middleware):
    rf = RequestFactory()
    request = rf.get("/u/thedude/")
    response = csp_middleware.process_response(request, HttpResponse())
    assert response._csp_config_ro == {"default-src": ["override.com"]}
    assert not hasattr(response, "_csp_config")
    assert csp.constants.HEADER in response.headers
    assert csp.constants.HEADER_REPORT_ONLY in response.headers
    assert response.headers[csp.constants.HEADER] == "default-src default.com"
    assert response.headers[csp.constants.HEADER_REPORT_ONLY] == "default-src override.com"


@override_settings(
    CONTENT_SECURITY_POLICY={"REPORT_PERCENTAGE": 0, "DIRECTIVES": {"default-src": ["default.com"]}},
    CONTENT_SECURITY_POLICY_REPORT_ONLY={"REPORT_PERCENTAGE": 100, "DIRECTIVES": {"default-src": ["default.com"], "report-uri": ["report.com"]}},
)
def test_csp_report_percentage_zero(csp_middleware):
    rf = RequestFactory()
    request = rf.get("/u/thedude/")
    response = csp_middleware.process_response(request, HttpResponse())
    assert csp.constants.HEADER in response.headers
    assert csp.constants.HEADER_REPORT_ONLY in response.headers
    assert "report-uri" not in response.headers[csp.constants.HEADER]
    assert "report-uri" in response.headers[csp.constants.HEADER_REPORT_ONLY]


@mock.patch.dict("os.environ", {"CSP_REPORT_PERCENTAGE": "0.5"})
def test_csp_report_percentage_can_be_float():
    # Test report percentage is cast to a float.
    from springfield import settings

    # Force settings to reload pulling in the mocked environ
    reload(settings)

    assert settings.CONTENT_SECURITY_POLICY["REPORT_PERCENTAGE"] == 0.5
    assert settings.CONTENT_SECURITY_POLICY_REPORT_ONLY is None


@mock.patch.dict("os.environ", {"CSP_REPORT_URI": "/_the_csp_dude"}, clear=True)
def test_csp_report_uri():
    # Test if report-uri is set it is added to CSP config.
    from springfield import settings

    # Force settings to reload pulling in the mocked environ
    reload(settings)

    assert settings.csp_report_uri == "/_the_csp_dude"
    assert settings.CONTENT_SECURITY_POLICY["DIRECTIVES"]["report-uri"] == "/_the_csp_dude"
    assert settings.csp_ro_report_uri is None
    assert settings.CONTENT_SECURITY_POLICY_REPORT_ONLY is None


@mock.patch.dict("os.environ", {"CSP_REPORT_URI": "/_the_csp_dude", "CSP_RO_REPORT_URI": "/_csp_ro"}, clear=True)
def test_csp_ro_report_uri():
    # Test if report-only report-uri is set it is added to CSP config.
    from springfield import settings

    # Force settings to reload pulling in the mocked environ
    reload(settings)

    assert settings.csp_report_uri == "/_the_csp_dude"
    assert settings.CONTENT_SECURITY_POLICY["DIRECTIVES"]["report-uri"] == "/_the_csp_dude"
    assert settings.csp_ro_report_uri == "/_csp_ro"
    assert settings.CONTENT_SECURITY_POLICY_REPORT_ONLY["DIRECTIVES"]["report-uri"] == "/_csp_ro"


class TestCacheMiddleware(TestCase):
    def setUp(self):
        self.middleware = CacheMiddleware(get_response=HttpResponse)
        self.request = HttpRequest()
        self.response = HttpResponse()

    @freeze_time("2023-01-01 00:00:00.123456")
    def test_good_response_has_headers(self):
        for method in ("GET", "HEAD"):
            for status in (200, 301, 302, 403, 404, 500):
                self.request.method = method
                self.response.status_code = status
                self.middleware.process_response(self.request, self.response)
                self.assertEqual(self.response["Cache-Control"], "max-age=600")
                self.assertEqual(self.response["Expires"], "Sun, 01 Jan 2023 00:10:00 GMT")

    def test_no_caching_methods(self):
        for method in ("POST", "PUT", "DELETE", "OPTIONS"):
            self.request.method = method
            self.response.status_code = 200
            self.middleware.process_response(self.request, self.response)
            self.assertNotIn("Cache-Control", self.response)
            self.assertNotIn("Expires", self.response)

    def test_no_caching_headers(self):
        self.request.method = "GET"
        self.response.status_code = 200
        self.response["Cache-Control"] = "no-cache"
        self.middleware.process_response(self.request, self.response)
        self.assertEqual(self.response["Cache-Control"], "no-cache")
        self.assertNotIn("Expires", self.response)

    def test_no_cache_streaming_response(self):
        self.request.method = "GET"
        self.response.status_code = 200
        self.response.streaming = True
        self.middleware.process_response(self.request, self.response)
        self.assertNotIn("Cache-Control", self.response)
        self.assertNotIn("Expires", self.response)


class TestClacksOverheadMiddleware(TestCase):
    def setUp(self):
        self.middleware = ClacksOverheadMiddleware(get_response=HttpResponse)
        self.request = HttpRequest()
        self.response = HttpResponse()

    def test_good_response_has_header(self):
        self.response.status_code = 200
        self.middleware.process_response(self.request, self.response)
        self.assertEqual(self.response["X-Clacks-Overhead"], "GNU Terry Pratchett")

    def test_other_response_has_no_header(self):
        self.response.status_code = 301
        self.middleware.process_response(self.request, self.response)
        self.assertNotIn("X-Clacks-Overhead", self.response)

        self.response.status_code = 404
        self.middleware.process_response(self.request, self.response)
        self.assertNotIn("X-Clacks-Overhead", self.response)


@override_settings(ENABLE_HOSTNAME_MIDDLEWARE=True)
class TestHostnameMiddleware(TestCase):
    @override_settings(HOSTNAME="foobar", CLUSTER_NAME="oregon-b")
    def test_base(self):
        self.middleware = HostnameMiddleware(get_response=HttpResponse)
        self.request = HttpRequest()
        self.response = HttpResponse()

        self.middleware.process_response(self.request, self.response)
        self.assertEqual(self.response["X-Backend-Server"], "foobar.oregon-b")

    @override_settings(
        MIDDLEWARE=(list(settings.MIDDLEWARE) + ["springfield.base.middleware.HostnameMiddleware"]),
        HOSTNAME="foobar",
        CLUSTER_NAME="el-dudarino",
    )
    def test_request(self):
        response = self.client.get("/en-US/")
        self.assertEqual(response["X-Backend-Server"], "foobar.el-dudarino")
