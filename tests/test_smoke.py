"""Smoke tests: the Flask app imports against the current dependencies and
the index page renders through Jinja2. Also covers the new person/IBAN fields
and the (env-gated) Basic-Auth from Issue #1."""

import base64
import os
import unittest


class AppSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import fd_rechenwesen

        fd_rechenwesen.app.config["TESTING"] = True
        # These "open page" tests assume auth is off; make that deterministic
        # regardless of whatever AUTH_PASSWORD the surrounding env provides.
        fd_rechenwesen.app.config["AUTH_PASSWORD"] = None
        cls.app = fd_rechenwesen.app
        cls.client = fd_rechenwesen.app.test_client()

    def test_index_get_renders(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.data.decode()
        self.assertIn("The flipdot Rechenwesen", html)
        self.assertIn('<form', html)
        self.assertNotIn("alert-danger", html)

    def test_template_renders_message_blocks(self):
        with self.app.app_context():
            from flask import render_template

            success = render_template("index.html", message="Danke", error=False)
            self.assertIn("alert-success", success)
            self.assertIn("Danke", success)

            danger = render_template("index.html", message="Fehler", error=True)
            self.assertIn("alert-danger", danger)
            self.assertIn("Fehler", danger)

    def test_upload_field_present(self):
        html = self.client.get("/").data.decode()
        self.assertIn('name="pdf"', html)
        self.assertIn('name="shop-name"', html)
        self.assertIn('name="price"', html)

    def test_person_and_iban_fields_present(self):
        html = self.client.get("/").data.decode()
        self.assertIn('name="person"', html)
        self.assertIn('name="iban"', html)

    def test_frontpage_has_new_placeholders(self):
        import fd_rechenwesen

        frontpage_path = os.path.join(
            os.path.dirname(fd_rechenwesen.__file__), "frontpage.html"
        )
        with open(frontpage_path, encoding="utf-8") as fh:
            content = fh.read()
        self.assertIn("{{PERSON}}", content)
        self.assertIn("{{IBAN}}", content)


class AuthEnabledTest(unittest.TestCase):
    """The app must lock down when AUTH_PASSWORD is set (Issue #1)."""

    @classmethod
    def setUpClass(cls):
        import fd_rechenwesen

        cls.app = fd_rechenwesen.app
        cls.client = cls.app.test_client()

    def setUp(self):
        self._orig_user = self.app.config.get("AUTH_USER")
        self._orig_pass = self.app.config.get("AUTH_PASSWORD")
        self.app.config["AUTH_USER"] = "vorstand"
        self.app.config["AUTH_PASSWORD"] = "geheim"

    def tearDown(self):
        self.app.config["AUTH_USER"] = self._orig_user
        self.app.config["AUTH_PASSWORD"] = self._orig_pass

    def _basic(self, user, pw):
        token = base64.b64encode(f"{user}:{pw}".encode()).decode()
        return {"Authorization": f"Basic {token}"}

    def test_index_requires_auth_when_enabled(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 401)
        self.assertIn("Basic", response.headers.get("WWW-Authenticate", ""))

    def test_index_allows_correct_auth(self):
        response = self.client.get("/", headers=self._basic("vorstand", "geheim"))
        self.assertEqual(response.status_code, 200)

    def test_index_rejects_wrong_password(self):
        response = self.client.get("/", headers=self._basic("vorstand", "falsch"))
        self.assertEqual(response.status_code, 401)

    def test_post_requires_auth_when_enabled(self):
        response = self.client.post("/")
        self.assertEqual(response.status_code, 401)


class AuthDisabledTest(unittest.TestCase):
    """With AUTH_PASSWORD unset the page stays publicly reachable."""

    @classmethod
    def setUpClass(cls):
        import fd_rechenwesen

        cls.app = fd_rechenwesen.app
        cls.client = cls.app.test_client()

    def test_index_open_when_auth_password_unset(self):
        orig = self.app.config.get("AUTH_PASSWORD")
        self.app.config["AUTH_PASSWORD"] = None
        try:
            self.assertEqual(self.client.get("/").status_code, 200)
        finally:
            self.app.config["AUTH_PASSWORD"] = orig


if __name__ == "__main__":
    unittest.main()
