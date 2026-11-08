import sqlite3
import tempfile
import unittest
from pathlib import Path

import database


class DatabaseTests(unittest.TestCase):
    def test_database_initialization_and_default_categories(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            original_instance = database.INSTANCE_DIR
            original_path = database.DATABASE_PATH

            try:
                database.INSTANCE_DIR = Path(temp_dir)
                database.DATABASE_PATH = Path(temp_dir) / "test_expense.db"
                database.init_db()

                with database.get_db() as conn:
                    tables = {
                        row["name"]
                        for row in conn.execute(
                            "SELECT name FROM sqlite_master WHERE type='table'"
                        )
                    }
                    self.assertIn("categories", tables)
                    self.assertIn("records", tables)

                    categories = conn.execute(
                        "SELECT COUNT(*) AS count FROM categories"
                    ).fetchone()["count"]
                    self.assertGreaterEqual(categories, 10)

                    foreign_keys = conn.execute(
                        "PRAGMA foreign_keys"
                    ).fetchone()[0]
                    self.assertEqual(foreign_keys, 1)
            finally:
                database.INSTANCE_DIR = original_instance
                database.DATABASE_PATH = original_path


if __name__ == "__main__":
    unittest.main()
