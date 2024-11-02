import time
from urllib.parse import quote, quote_plus
from django.http import HttpResponseRedirect
from django.test import LiveServerTestCase, TestCase
from django.test.client import Client
import django_otp
import requests
import django_otp.plugins.otp_totp.models as otp_totp

from main.models import Code, Service, User, UserServiceConnection
from main.views import check_user_has_permission, resolve_to_service

# Create your tests here.

protected_path = "/protected"
sameorigin = "http://localhost:8001"
crossorigin = "http://127.0.0.1:8001"
unauthenticated_path = "/auth/go/unauthenticated"

TEST_USERNAME = "testuser"
TEST_USER_EMAIL = "test@poisson.tld"
TEST_USER_PASSWORD = "securepassword!!!111elf"

class IsolationTestCase(LiveServerTestCase):
    port = 8000
    def setUp(self):
        self.s1 = Service(name="Test Service", icon="d20", sub_url="/protected")
        self.s1.save()
        self.s2 = Service(name="Test Service CrossOrigin", icon="admin", sub_url="/protected", origin=crossorigin.split("://")[1])
        self.s2.save()

    def tearDown(self):
        self.s1.delete()
        self.s2.delete()

    def test_cant_access_protected_without_auth(self):
        path = f"{sameorigin}{protected_path}"
        resp = requests.get(path, allow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.headers["Location"] in [f"{sameorigin}{unauthenticated_path}?url={path}", f"{sameorigin}{unauthenticated_path}?url={quote_plus(path)}"])
        self.assertTrue(True)

    def test_cant_access_protected_without_auth_crossorigin(self):
        path = f"{crossorigin}{protected_path}"
        resp = requests.get(path, allow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.headers["Location"] in [f"{sameorigin}{unauthenticated_path}?url={path}", f"{sameorigin}{unauthenticated_path}?url={quote_plus(path)}"])


class RedirectionTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("testuser", "test@poisson.tld", "")
        self.user.save()

        self.user2fa = User.objects.create_user("testuser2fa", "test2fa@poisson.tld", "")
        self.user2fa.save()
        self.user2faDevice = otp_totp.TOTPDevice(key = "dummykey")
        self.user2faDevice.user = self.user2fa
        self.user2faDevice.name = 'Unnamed Device'
        self.user2faDevice.confirmed = True
        self.user2faDevice.save()

        self.service2FA = Service(name="test5", icon="d20", sub_url="/2fa", origin=crossorigin.split("://")[1], require_2fa_if_configured=True)
        self.service2FA.save()

        self.serviceValid = Service(name="test3", icon="d20", sub_url="/url1", origin=crossorigin.split("://")[1])
        self.serviceValid.save()

        UserServiceConnection(user=self.user, service=self.serviceValid).save()
        UserServiceConnection(user=self.user2fa, service=self.service2FA).save()
        UserServiceConnection(user=self.user, service=self.service2FA).save()

        self.serviceCode = Service(name="code", icon="d20", sub_url="/needs_code", origin=crossorigin.split("://")[1])
        self.serviceCode.save()

        self.code = Code(service=self.serviceCode, code="testcode")
        self.code.save()

        self.serviceInvalid = Service(name="test4", icon="d20", sub_url="/url2", origin=crossorigin.split("://")[1])
        self.serviceInvalid.save()

        self.allServices = [self.serviceValid, self.serviceInvalid, self.serviceCode, self.service2FA]
        self.nonCodeServices = [self.serviceValid, self.serviceInvalid, self.service2FA]

    def tearDown(self):
        self.user.delete()
        self.serviceValid.delete()
        self.serviceInvalid.delete()
        self.code.delete()
        self.serviceCode.delete()
        self.service2FA.delete()

    def consume_code(self):
        self.client.post("/auth/api/consume_code", {"code": self.code.code})

    def login_totp(self):
        req = self.client.request()
        req.user = self.user2fa
        req.session = self.client.session
        django_otp.login(req, self.user2faDevice)
        req.session.save()

    def test_unauth_goes_to_login(self):
        for svc in self.nonCodeServices:
            target_url = f'{crossorigin}{svc.sub_url}'
            resp = self.client.get(f"/auth/go/unauthenticated?url={target_url}")
            self.assertIsInstance(resp, HttpResponseRedirect)
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.url, f"/auth?next={quote(target_url)}")

    def test_unauth_code_goes_to_code_login(self):
        target_url = f'{crossorigin}{self.serviceCode.sub_url}'
        resp = self.client.get(f"/auth/go/unauthenticated?url={target_url}")
        self.assertIsInstance(resp, HttpResponseRedirect)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, f"/auth/go/code?next={quote(target_url)}")

    def test_auth_invalid_fails(self):
        self.client.force_login(self.user)
        target_url = f'{crossorigin}{self.serviceInvalid.sub_url}'
        resp = self.client.get(f"/auth/go/unauthenticated?url={target_url}")
        self.assertIsInstance(resp, HttpResponseRedirect)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, f"/auth/go/fail")

    def test_auth_code_goes_to_code_login(self):
        self.client.force_login(self.user)
        target_url = f'{crossorigin}{self.serviceCode.sub_url}'
        resp = self.client.get(f"/auth/go/unauthenticated?url={target_url}")
        self.assertIsInstance(resp, HttpResponseRedirect)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, f"/auth/go/code?next={quote(target_url)}")

    def test_auth_with_valid_code_goes_to_target(self):
        self.client.force_login(self.user)
        self.consume_code()
        target_url = f'{crossorigin}{self.serviceCode.sub_url}'
        resp = self.client.get(f"/auth/go/unauthenticated?url={target_url}")
        self.assertIsInstance(resp, HttpResponseRedirect)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith(f"{crossorigin}/_sso?token="))

    def test_unauth_with_valid_code_goes_to_target(self):
        self.consume_code()
        target_url = f'{crossorigin}{self.serviceCode.sub_url}'
        resp = self.client.get(f"/auth/go/unauthenticated?url={target_url}")
        self.assertIsInstance(resp, HttpResponseRedirect)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith(f"{crossorigin}/_sso?token="))

    def test_auth_allowed_succeeds(self):
        self.client.force_login(self.user)
        target_url = f'{crossorigin}{self.serviceValid.sub_url}'
        resp = self.client.get(f"/auth/go/unauthenticated?url={target_url}")
        self.assertIsInstance(resp, HttpResponseRedirect)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith(f"{crossorigin}/_sso?token="))

    def test_auth_validated_succeeds(self):
        self.client.force_login(self.user2fa)
        self.login_totp()
        target_url = f'{crossorigin}{self.service2FA.sub_url}'
        resp = self.client.get(f"/auth/go/unauthenticated?url={target_url}")
        self.assertIsInstance(resp, HttpResponseRedirect)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith(f"{crossorigin}/_sso?token="))

    def test_auth_unvalidated_no_device_succeeds(self):
        self.client.force_login(self.user)
        target_url = f'{crossorigin}{self.service2FA.sub_url}'
        resp = self.client.get(f"/auth/go/unauthenticated?url={target_url}")
        self.assertIsInstance(resp, HttpResponseRedirect)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith(f"{crossorigin}/_sso?token="))

    def test_auth_unvalidated_goes_to_2fa_prompt(self):
        self.client.force_login(self.user2fa)
        target_url = f'{crossorigin}{self.service2FA.sub_url}'
        resp = self.client.get(f"/auth/go/unauthenticated?url={target_url}")
        self.assertIsInstance(resp, HttpResponseRedirect)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, f"/auth/go/login_state_mod/otp?next={quote(target_url)}")


class PermissionsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", "test@poisson.tld", "")
        self.serviceValid = Service(name="test3", icon="d20", sub_url="/url1", origin=crossorigin.split("://")[1])
        self.serviceValid.save()
        self.serviceCode = Service(name="code", icon="d20", sub_url="/needs_code", origin=crossorigin.split("://")[1])
        self.serviceCode.save()
        self.serviceInvalid = Service(name="test4", icon="d20", sub_url="/url2", origin=crossorigin.split("://")[1])
        self.serviceInvalid.save()
        self.serviceRegex= Service(name="test5", icon="d20", sub_url=r"^/(url3|url4)$", origin=crossorigin.split("://")[1], regex=True)
        self.serviceRegex.save()
        self.code = Code(service=self.serviceInvalid)
        UserServiceConnection(user=self.user, service=self.serviceValid).save()

    def tearDown(self):
        self.user.delete()
        self.serviceValid.delete()
        self.serviceInvalid.delete()
        self.serviceRegex.delete()
        self.serviceCode.delete()

    def test_user_can_access_valid_service(self):
        self.assertTrue(check_user_has_permission(self.serviceValid, self.user, {}))

    def test_user_cant_access_invalid_service(self):
        self.assertFalse(check_user_has_permission(self.serviceInvalid, self.user, {}))

    def test_user_can_access_valid_service_from_url(self):
        self.assertTrue(check_user_has_permission(f"http://{self.serviceValid.origin}{self.serviceValid.sub_url}", self.user, {}))

    def test_user_cant_access_invalid_service_from_url(self):
        self.assertFalse(check_user_has_permission(f"http://{self.serviceInvalid.origin}{self.serviceInvalid.sub_url}", self.user, {}))

    def test_regex_url_resolve(self):
        self.assertEqual(resolve_to_service(f"http://{self.serviceRegex.origin}/url4"), self.serviceRegex)

    def test_regex_url_resolve_fail(self):
        self.assertIsNone(resolve_to_service(f"http://{self.serviceRegex.origin}/url5"))


