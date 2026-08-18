import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from generate_menu import DISHES, RECIPE_URLS, build_daily_payload, generate_for_date, weekly_protein_plan


class DailyMenuTests(unittest.TestCase):
    def test_menu_is_one_protein_and_two_unique_sides(self):
        menu = generate_for_date("2026-08-19")
        self.assertEqual([dish["role"] for dish in menu["dishes"]], ["protein", "side", "side"])
        self.assertEqual(len({dish["id"] for dish in menu["dishes"]}), 3)

    def test_same_date_is_deterministic(self):
        first = generate_for_date("2026-09-12")
        second = generate_for_date("2026-09-12")
        self.assertEqual(first, second)

    def test_planned_protein_is_the_selected_protein(self):
        start = date(2026, 8, 18)
        for offset in range(90):
            current = start + timedelta(days=offset)
            menu = generate_for_date(current.isoformat())
            self.assertEqual(menu["proteinFamily"], menu["dishes"][0]["proteinFamily"])

    def test_daily_payload_warns_about_tomorrow(self):
        payload = build_daily_payload("2026-08-19")
        self.assertTrue(payload["advanceNoticeForTomorrow"]["anyNeedsAdvancePrep"])

    def test_weekly_budget_shape(self):
        plan = weekly_protein_plan(0)
        self.assertEqual(plan.count("chicken"), 3)
        self.assertEqual(plan.count("fish"), 1)
        self.assertEqual(plan.count("mutton"), 1)

    def test_every_active_dish_has_a_specific_recipe(self):
        active_ids = {
            dish["id"]
            for category in ("bengali", "chinese", "otherIndian")
            for kind in ("protein", "vegetable")
            for dish in DISHES[category][kind]
        }
        self.assertEqual(active_ids - RECIPE_URLS.keys(), set())


if __name__ == "__main__":
    unittest.main()
