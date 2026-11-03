"""Regression tests for defects found in the independent code review."""

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import agent_audit  # noqa: E402
import token_audit  # noqa: E402


def run_hook(payload: dict) -> dict:
    done = subprocess.run(
        [sys.executable, str(ROOT / "hooks" / "inject.py")],
        input=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        capture_output=True,
        timeout=30,
    )
    return json.loads(done.stdout.decode("utf-8")) if done.stdout.strip() else {}


class Hook(unittest.TestCase):
    def test_accents_survive_the_round_trip(self):
        out = run_hook(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Agent",
                "tool_input": {"prompt": "entrée → résultat", "model": "haiku"},
            }
        )
        updated = out["hookSpecificOutput"]["updatedInput"]
        self.assertTrue(updated["prompt"].startswith("entrée → résultat"))
        self.assertEqual(updated["model"], "haiku")

    def test_rules_point_to_an_existing_test_scope_script(self):
        context = run_hook({"hook_event_name": "SessionStart"})["hookSpecificOutput"][
            "additionalContext"
        ]
        found = re.search(r'python "([^"]+test_scope\.py)"', context)
        self.assertIsNotNone(found, context)
        assert found is not None
        self.assertTrue(Path(found.group(1)).exists(), found.group(1))

    def test_rules_are_added_once(self):
        out = run_hook(
            {
                "hook_event_name": "PreToolUse",
                "tool_input": {"prompt": "x\nRIGHTSIZE rules already here"},
            }
        )
        self.assertEqual(out, {})

    def test_session_start_context(self):
        out = run_hook({"hook_event_name": "SessionStart"})
        self.assertIn("QUALITY BEFORE OPTIMISATION", out["hookSpecificOutput"]["additionalContext"])


class AgentAudit(unittest.TestCase):
    def setUp(self):
        self.folder = Path(tempfile.mkdtemp())
        self.file = self.folder / "code-explorer.md"
        self.original = b"---\r\nname: code-explorer\r\ndescription: Finds code.\r\n---\r\nBody\r\n"
        self.file.write_bytes(self.original)

    def test_double_folder_apply_is_idempotent_and_keeps_crlf_and_backup(self):
        folder = str(self.folder)
        agent_audit.main(["--dir", folder, "--dir", folder, "--apply"])
        agent_audit.main(["--dir", folder, "--apply"])
        text = self.file.read_bytes()
        self.assertEqual(text.count(b"effort:"), 1)
        self.assertEqual(text.count(b"model:"), 1)
        self.assertNotIn(b"\n", text.replace(b"\r\n", b""))  # every newline is still CRLF
        self.assertEqual((self.folder / "code-explorer.md.bak").read_bytes(), self.original)


class TokenAudit(unittest.TestCase):
    def write_session(self, root: Path, name: str, model: str):
        record = {
            "type": "assistant",
            "timestamp": "2026-10-20T10:00:00Z",
            "message": {
                "id": "msg_same",
                "model": model,
                "usage": {"input_tokens": 10, "output_tokens": 100},
                "content": [{"type": "text"}],
            },
        }
        path = root / "proj" / f"{name}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record), encoding="utf-8")

    def report(self, root: Path) -> dict:
        args = token_audit.parse_args(["--root", str(root), "--since", "2026-10-01"])
        turns = token_audit.dedupe(
            t
            for p in token_audit.transcript_files(root, None, None)
            for t in token_audit.read_turns(p, args.since, None)
        )
        return token_audit.build_report(turns, args)

    def test_copied_history_counts_once(self):
        root = Path(tempfile.mkdtemp())
        self.write_session(root, "original", "claude-opus-5-5")
        self.write_session(root, "resumed", "claude-opus-5-5")
        self.assertEqual(self.report(root)["responses"], 1)

    def test_unpriced_models_are_reported(self):
        root = Path(tempfile.mkdtemp())
        self.write_session(root, "old", "claude-3-5-haiku")
        report = self.report(root)
        self.assertEqual(report["unpriced"], {"responses": 1, "models": ["claude-3-5-haiku"]})


class BenchInfraErrors(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, str(ROOT / "bench"))
        import run_bench

        self.infra = run_bench.infra_error

    def test_credit_and_empty_runs_are_infrastructure(self):
        self.assertTrue(
            self.infra({"is_error": True, "result": "Credit balance is too low", "num_turns": 1})
        )
        self.assertTrue(self.infra({"is_error": True, "result": "?", "num_turns": 0}))

    def test_real_model_runs_are_kept(self):
        self.assertFalse(self.infra({"is_error": False, "result": "done", "num_turns": 1}))
        self.assertFalse(self.infra({"is_error": True, "result": "hit budget", "num_turns": 12}))


if __name__ == "__main__":
    unittest.main()
