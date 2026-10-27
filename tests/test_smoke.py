"""Smoke tests: the Flask app imports against the current dependencies and
the index page renders through Jinja2."""

import unittest


class AppSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import fd_rechenwesen

        fd_rechenwesen.app.config["TESTING"] = True
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


if __name__ == "__main__":
    unittest.main()
