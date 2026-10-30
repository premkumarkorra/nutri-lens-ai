import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class HealthProfileDietChoiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
        cls.js = (ROOT / "static" / "js" / "app.js").read_text(encoding="utf-8")

    def test_profile_offers_non_vegetarian_choice(self):
        self.assertRegex(
            self.html,
            r'<input\s+type="checkbox"\s+id="profile-non-vegetarian">'
            r'[\s\S]*?<strong>Non-Vegetarian</strong>',
        )

    def test_diet_choices_load_from_existing_vegetarian_status(self):
        self.assertRegex(
            self.js,
            r'if\s*\(vegEl\)\s*vegEl\.checked\s*=\s*!!isVeg;'
            r'\s*if\s*\(nonVegEl\)\s*nonVegEl\.checked\s*=\s*!isVeg;',
        )

    def test_diet_choices_are_mutually_exclusive(self):
        self.assertIn(
            "if (nonVegEl) nonVegEl.checked = false;", self.js
        )
        self.assertIn("if (vegEl) vegEl.checked = false;", self.js)

    def test_vegan_is_not_offered_or_submitted_by_health_profile(self):
        self.assertNotIn('id="profile-vegan"', self.html)
        self.assertNotIn('id="reg-vegan"', self.html)
        self.assertNotIn("profile-vegan", self.js)
        self.assertNotIn("reg-vegan", self.js)


if __name__ == "__main__":
    unittest.main()
