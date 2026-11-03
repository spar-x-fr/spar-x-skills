"""Behaviour of test_scope.py on throwaway git repositories."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import test_scope

# With core.fsmonitor=true in the user's global config, every throwaway repository
# would start a git fsmonitor daemon that never exits; dozens pile up and stall the
# suite. Turn it off for the git processes these tests start (git >= 2.31).
os.environ.update(
    {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.fsmonitor", "GIT_CONFIG_VALUE_0": "false"}
)

FILES = {
    "shop/pricing.py": "def total(items):\n    return sum(items)\n",
    "shop/users.py": "def name(u):\n    return u['name']\n",
    "shop/username_rules.py": "MAX = 20\n",
    "shop/orphan.py": "X = 1\n",
    "tests/helpers.py": "def make():\n    return 1\n",
    "tests/test_pricing.py": "from shop.pricing import total\n",
    "tests/test_accounts.py": "from shop import users\nfrom tests.helpers import make\n",
    "tests/test_rules.py": "from shop.username_rules import MAX\n",
    "pyproject.toml": "[project]\nname='x'\n",
    "README.md": "doc\n",
    "config/app.yaml": "debug: false\n",
}
GIT = ["git", "-c", "user.email=t@t", "-c", "user.name=t", "-c", "commit.gpgsign=false"]


def make_repo(parent: Path, files=FILES) -> Path:
    root = parent / "repo"
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    for args in (["init", "-q"], ["add", "."], ["commit", "-qm", "init"]):
        subprocess.run(GIT + args, cwd=root, check=True, capture_output=True)
    return root


class Base(unittest.TestCase):
    parent_name = ""

    def setUp(self):
        parent = Path(tempfile.mkdtemp())
        if self.parent_name:
            parent = parent / self.parent_name
            parent.mkdir()
        self.root = make_repo(parent)
        self.record_full(passed=True)

    def record_full(self, passed=True, days_ago=0):
        date = datetime.now(timezone.utc) - timedelta(days=days_ago)
        test_scope.save_ledger(
            self.root,
            {
                "last_full": {
                    "commit": test_scope.git(self.root, "rev-parse", "HEAD"),
                    "passed": passed,
                    "date": date.isoformat(timespec="seconds"),
                },
                "runs": [],
            },
        )

    def edit(self, rel, extra="\n# changed\n"):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        old = path.read_text(encoding="utf-8") if path.exists() else ""
        path.write_text(old + extra, encoding="utf-8")

    def plan(self, full=False):
        return test_scope.make_plan(self.root, full, None)


class Selection(Base):
    def test_nothing_changed_runs_nothing(self):
        self.assertEqual(self.plan().mode, "none")

    def test_docs_only_runs_nothing(self):
        self.edit("README.md")
        self.assertEqual(self.plan().mode, "none")

    def test_change_runs_only_matching_tests(self):
        self.edit("shop/pricing.py")
        plan = self.plan()
        self.assertEqual((plan.mode, plan.tests), ("scoped", ["tests/test_pricing.py"]))

    def test_import_match_is_word_bounded(self):
        self.edit("shop/users.py")
        self.assertEqual(self.plan().tests, ["tests/test_accounts.py"])

    def test_changed_test_file_is_run(self):
        self.edit("tests/test_rules.py")
        self.assertEqual(self.plan().tests, ["tests/test_rules.py"])

    def test_changed_helper_runs_the_tests_that_import_it(self):
        self.edit("tests/helpers.py")
        self.assertEqual(self.plan().tests, ["tests/test_accounts.py"])

    def test_shared_file_forces_full(self):
        self.edit("pyproject.toml")
        plan = self.plan()
        self.assertEqual(plan.mode, "full")
        self.assertIn("pyproject.toml", plan.reason)

    def test_unclassified_file_type_forces_full(self):
        self.edit("config/app.yaml")
        self.assertEqual(self.plan().mode, "full")

    def test_unmapped_source_without_folder_tests_forces_full(self):
        self.edit("shop/orphan.py")
        self.edit("shop/pricing.py")  # even when another change selected tests
        plan = self.plan()
        self.assertEqual(plan.mode, "full")
        self.assertEqual(plan.unmapped, ["shop/orphan.py"])

    def test_renamed_module_keeps_tests_of_the_old_name(self):
        subprocess.run(
            ["git", "mv", "shop/pricing.py", "shop/billing.py"],
            cwd=self.root,
            check=True,
            capture_output=True,
        )
        self.assertIn("shop/pricing.py", test_scope.changed_files(self.root, None))
        plan = self.plan()  # billing.py has no test yet, so a full run is the safe answer
        self.assertTrue(plan.mode == "full" or "tests/test_pricing.py" in plan.tests, plan)

    def test_deleted_module_runs_its_tests(self):
        (self.root / "shop/users.py").unlink()
        self.assertIn("tests/test_accounts.py", self.plan().tests)

    def test_non_ascii_path_is_seen(self):
        self.edit("shop/café.py", "X = 2\n")
        self.edit("tests/test_café.py", "from shop.café import X\n")
        self.assertIn("tests/test_café.py", self.plan().tests)

    def test_untracked_test_found_from_a_subfolder(self):
        self.edit("tests/test_new.py", "import shop\n")
        plan = test_scope.make_plan(self.root, False, None)
        self.assertIn("tests/test_new.py", plan.tests)
        self.assertEqual(test_scope.changed_files(self.root, None), ["tests/test_new.py"])

    def test_force_full(self):
        self.assertEqual(self.plan(full=True).mode, "full")

    def test_red_stale_or_broken_full_run_forces_full(self):
        self.record_full(passed=False)
        self.assertEqual(self.plan().mode, "full")
        self.record_full(passed=True, days_ago=10)
        self.assertIn("jours", self.plan().reason)
        test_scope.save_ledger(self.root, {"last_full": {"passed": True}, "runs": []})
        self.assertEqual(self.plan().mode, "full")


class InsideIgnoredFolderName(Base):
    parent_name = "build"  # a repo living under a folder called build must still work

    def test_tests_are_found(self):
        self.edit("shop/pricing.py")
        self.assertEqual(self.plan().tests, ["tests/test_pricing.py"])


class Running(Base):
    def test_scoped_run_never_replaces_last_full(self):
        self.edit("shop/pricing.py")
        plan = self.plan()
        code = test_scope.run_and_record(self.root, plan, [sys.executable, "-c", "print('ok')"], 1)
        ledger = json.loads((self.root / test_scope.LEDGER).read_text(encoding="utf-8"))
        self.assertEqual((code, ledger["runs"][-1]["mode"]), (0, "scoped"))
        self.assertTrue(ledger["last_full"]["passed"])

    def test_red_full_run_makes_next_run_full(self):
        plan = self.plan(full=True)
        test_scope.run_and_record(
            self.root, plan, [sys.executable, "-c", "import sys; sys.exit(1)"], 4
        )
        self.assertEqual(self.plan().mode, "full")

    def test_full_command_lists_every_test_module(self):
        command = test_scope.build_command(self.root, self.plan(full=True), None)
        self.assertEqual(
            command[-3:], ["tests.test_accounts", "tests.test_pricing", "tests.test_rules"]
        )

    def test_empty_full_suite_is_refused(self):
        empty = make_repo(Path(tempfile.mkdtemp()), {"app.py": "X = 1\n"})
        with self.assertRaises(RuntimeError):
            test_scope.build_command(empty, test_scope.Plan("full", "x"), None)

    def test_mixed_languages_need_an_explicit_command(self):
        with self.assertRaises(RuntimeError):
            test_scope.detect_command(self.root, ["tests/test_a.py", "web/a.test.ts"])

    def test_template_keeps_paths_with_spaces_whole(self):
        command = test_scope.expand_template("pytest -q {tests}", ["tests/my test.py", "b.py"])
        self.assertEqual(command, ["pytest", "-q", "tests/my test.py", "b.py"])


if __name__ == "__main__":
    unittest.main()
