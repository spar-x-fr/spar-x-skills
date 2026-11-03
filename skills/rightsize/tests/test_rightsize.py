"""Run from the repository root: python -m unittest discover -s tests"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import token_audit
from prices import request_cost, resolve
from route import Route, Task, escalate, route


class RouteTable(unittest.TestCase):
    def check(self, task, model, effort, mode=None):
        result = route(task)
        self.assertEqual((result.model, result.effort), (model, effort), result)
        if mode:
            self.assertEqual(result.mode, mode, result)

    def test_deterministic_tool_needs_no_model(self):
        self.check(Task(tool_can_do_it=True, scope=3), "none", "none", "inline")

    def test_read_only_search_goes_to_haiku_low(self):
        self.check(Task(read_only=True, scope=2, depth=1), "haiku", "low", "subagent")

    def test_risky_read_is_not_downgraded(self):
        self.check(Task(read_only=True, risk=2, depth=2), "opus", "medium")

    def test_simple_edit(self):
        self.check(Task(scope=1, risk=1, depth=1), "haiku", "low")

    def test_standard_feature(self):
        self.check(Task(scope=2, risk=1, ambiguity=1, depth=2), "sonnet", "medium")

    def test_prod_risk_lifts_one_level(self):
        self.check(Task(scope=1, risk=2, depth=1), "sonnet", "medium")

    def test_wide_ambiguous_work_plans_on_opus(self):
        result = route(Task(scope=3, ambiguity=3, depth=2, risk=1))
        self.assertEqual(
            (result.model, result.plan_model, result.mode),
            ("sonnet", "opus", "plan-then-subagents"),
        )

    def test_hard_bug(self):
        self.check(Task(depth=3, risk=1, scope=1), "opus", "high")

    def test_hard_and_risky_goes_xhigh(self):
        self.check(Task(depth=3, risk=2), "opus", "xhigh")

    def test_security_change_plans_first(self):
        self.check(Task(risk=3, scope=1, depth=2), "opus", "high", "plan-then-subagents")

    def test_conversation_context_keeps_it_inline(self):
        self.check(Task(scope=2, depth=2, needs_history=True), "sonnet", "medium", "inline")

    def test_tiny_tasks_stay_inline(self):
        self.check(Task(read_only=True, tool_calls=1), "haiku", "low", "inline")

    def test_verified_task_starts_one_level_lower(self):
        self.check(Task(depth=3, risk=1, has_check=True), "opus", "medium")
        self.check(Task(scope=2, depth=2, has_check=True), "sonnet", "low")

    def test_verification_never_lowers_max_risk(self):
        self.check(Task(risk=3, depth=2, has_check=True), "opus", "high")

    def test_verified_failure_climbs_back(self):
        result = route(Task(depth=3, risk=1, has_check=True, failed_attempts=1))
        self.assertEqual((result.model, result.effort), ("opus", "high"))

    def test_rejects_out_of_range(self):
        with self.assertRaises(ValueError):
            route(Task(scope=4))


class Escalation(unittest.TestCase):
    def test_effort_rises_before_model(self):
        start = Route("haiku", "low", "subagent")
        self.assertEqual((escalate(start, 1).model, escalate(start, 1).effort), ("haiku", "medium"))
        self.assertEqual((escalate(start, 3).model, escalate(start, 3).effort), ("sonnet", "low"))

    def test_fable_and_max_only_after_opus_xhigh(self):
        start = Route("opus", "high", "subagent")
        self.assertEqual(escalate(start, 1).effort, "xhigh")
        self.assertEqual(escalate(start, 2).model, "fable")
        self.assertEqual((escalate(start, 9).model, escalate(start, 9).effort), ("fable", "max"))

    def test_failures_counted_in_route(self):
        result = route(Task(scope=2, depth=2, failed_attempts=1))
        self.assertEqual((result.model, result.effort), ("sonnet", "high"))


class Prices(unittest.TestCase):
    def test_aliases_and_suffixes(self):
        self.assertEqual(resolve("opus"), "claude-opus-5-5")
        self.assertEqual(resolve("claude-opus-5-5[1m]"), "claude-opus-5-5")
        self.assertEqual(resolve("claude-opus-5"), "claude-opus-5")
        self.assertIsNone(resolve("gpt-5"))

    def test_cost_components(self):
        usage = {
            "input_tokens": 1_000_000,
            "output_tokens": 1_000_000,
            "cache_read_input_tokens": 1_000_000,
            "cache_creation_input_tokens": 1_000_000,
            "cache_creation": {"ephemeral_1h_input_tokens": 1_000_000},
        }
        # 4 input + 20 output + 0.20 read + 4 * 2 one-hour write
        self.assertAlmostEqual(request_cost("claude-opus-5-5", usage), 32.20)

    def test_haiku_long_prompt_rate(self):
        short = request_cost("claude-haiku-5-5", {"input_tokens": 50_000})
        long = request_cost("claude-haiku-5-5", {"input_tokens": 200_000})
        self.assertAlmostEqual(short, 0.005)
        self.assertAlmostEqual(long, 0.10)


class Audit(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        project = self.root / "proj"
        (project / "s1" / "subagents").mkdir(parents=True)
        usage = {"input_tokens": 10, "output_tokens": 1000, "cache_read_input_tokens": 0}

        def line(msg_id, model, block, agent=None, stamp="2026-10-20T10:00:00Z"):
            record = {
                "type": "assistant",
                "timestamp": stamp,
                "effort": "high",
                "message": {"id": msg_id, "model": model, "usage": usage, "content": [block]},
            }
            if agent:
                record["agentId"] = agent
            return json.dumps(record)

        main = [
            line("m1", "claude-opus-5-5", {"type": "text"}),
            line("m1", "claude-opus-5-5", {"type": "tool_use", "name": "Agent"}),
            line("m2", "<synthetic>", {"type": "text"}),
            line("m3", "claude-opus-5-5", {"type": "text"}, stamp="2026-09-01T00:00:00Z"),
        ]
        (project / "s1.jsonl").write_text("\n".join(main) + "\nnot json\n", encoding="utf-8")
        sub = [
            line("a1", "claude-opus-5-5", {"type": "tool_use", "name": "Grep"}, agent="x"),
            line("a2", "claude-opus-5-5", {"type": "tool_use", "name": "Read"}, agent="x"),
        ]
        sub_path = project / "s1" / "subagents" / "agent-x.jsonl"
        sub_path.write_text("\n".join(sub), encoding="utf-8")
        sub_path.with_suffix(".meta.json").write_text('{"agentType": "Explore"}', encoding="utf-8")

    def report(self):
        args = token_audit.parse_args(["--root", str(self.root), "--since", "2026-10-01"])
        turns = [
            t
            for p in token_audit.transcript_files(self.root, None, None)
            for t in token_audit.read_turns(p, args.since, None)
        ]
        return turns, token_audit.build_report(turns, args)

    def test_dedupes_blocks_skips_synthetic_and_old_lines(self):
        turns, report = self.report()
        self.assertEqual(report["responses"], 3)
        main = [t for t in turns if not t.agent_id]
        self.assertEqual(main[0].tools, ("Agent",))

    def test_flags_read_only_subagent_on_opus(self):
        _, report = self.report()
        found = report["opportunities"]["readonly_subagents_not_on_haiku"]
        self.assertEqual(found["count"], 1)
        self.assertEqual(found["examples"][0]["type"], "Explore")
        self.assertGreater(found["estimated_saving"], 0)
        self.assertEqual(report["opportunities"]["main_thread_model_switches"]["switches"], 0)


if __name__ == "__main__":
    unittest.main()
