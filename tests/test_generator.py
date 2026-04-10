# -*- coding: utf-8 -*-
"""Edge case tests for ClozeGenerator"""

import sys
import os
import unittest

# Import the generator module directly, bypassing __init__.py (which requires aqt)
import importlib.util

_gen_path = os.path.join(os.path.dirname(__file__), '..', 'src',
                         'cloze_overlapper', 'generator.py')
_spec = importlib.util.spec_from_file_location("generator", _gen_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
ClozeGenerator = _mod.ClozeGenerator


class TestClozeGeneratorEdgeCases(unittest.TestCase):
    """Test edge cases in the cloze generation algorithm"""

    def _make_gen(self, before=1, prompt=1, after=0, options=None, maxfields=20):
        if options is None:
            options = [False, False, False, False]
        setopts = ([before, prompt, after], options)
        return ClozeGenerator(setopts, maxfields)

    # --- Single item ---

    def test_single_item(self):
        """Single item with prompt=1 should produce exactly 1 card"""
        gen = self._make_gen(before=1, prompt=1, after=0)
        fields, full, total = gen.generate(["alpha"])
        self.assertEqual(total, 1)
        self.assertIsNotNone(fields)
        self.assertEqual(len([f for f in fields if f != ""]), 1)

    def test_single_item_prompt_too_large(self):
        """prompt > number of items should return 0 (no cards possible)"""
        gen = self._make_gen(before=0, prompt=3, after=0)
        fields, full, total = gen.generate(["alpha"])
        self.assertEqual(fields, 0)

    # --- Two items ---

    def test_two_items_prompt_1(self):
        gen = self._make_gen(before=0, prompt=1, after=0)
        fields, full, total = gen.generate(["a", "b"])
        self.assertEqual(total, 2)
        self.assertIsNotNone(fields)

    def test_two_items_prompt_2(self):
        """2 items, prompt=2: only 1 card (both items clozed together)"""
        gen = self._make_gen(before=0, prompt=2, after=0)
        fields, full, total = gen.generate(["a", "b"])
        self.assertEqual(total, 1)
        self.assertIsNotNone(fields)

    def test_two_items_prompt_3(self):
        """prompt > items should signal no cards"""
        gen = self._make_gen(before=0, prompt=3, after=0)
        fields, full, total = gen.generate(["a", "b"])
        self.assertEqual(fields, 0)

    # --- Exceeds maxfields ---

    def test_exceeds_maxfields(self):
        """More items than maxfields should return None for fields"""
        gen = self._make_gen(before=0, prompt=1, after=0, maxfields=3)
        items = ["item%d" % i for i in range(5)]
        fields, full, total = gen.generate(items)
        self.assertIsNone(fields)
        self.assertEqual(total, 5)

    def test_exactly_maxfields(self):
        """Exactly maxfields items should succeed"""
        gen = self._make_gen(before=0, prompt=1, after=0, maxfields=5)
        items = ["item%d" % i for i in range(5)]
        fields, full, total = gen.generate(items)
        self.assertIsNotNone(fields)
        self.assertEqual(total, 5)

    # --- Increment option (options[2]) ---

    def test_increment_option(self):
        """With increment=True, total should be length + prompt - 1"""
        gen = self._make_gen(before=0, prompt=2, after=0,
                             options=[False, False, True, False])
        items = ["a", "b", "c"]
        fields, full, total = gen.generate(items)
        # total = 3 + 2 - 1 = 4
        self.assertEqual(total, 4)

    def test_increment_exceeds_maxfields(self):
        """Increment can push total beyond maxfields"""
        gen = self._make_gen(before=0, prompt=2, after=0,
                             options=[False, False, True, False], maxfields=3)
        items = ["a", "b", "c"]
        fields, full, total = gen.generate(items)
        # total = 3 + 2 - 1 = 4 > maxfields=3
        self.assertIsNone(fields)
        self.assertEqual(total, 4)

    # --- Before / After context ---

    def test_before_context(self):
        """Before context should include unhidden items before the cloze"""
        gen = self._make_gen(before=1, prompt=1, after=0)
        items = ["a", "b", "c"]
        fields, full, total = gen.generate(items)
        self.assertEqual(total, 3)
        # First card: no before context (nothing before), cloze on "a"
        # Second card: "a" as context, cloze on "b"
        # Third card: "b" as context, cloze on "c"
        self.assertIn("{{c1::a}}", fields[0])
        self.assertIn("a", fields[1])  # context
        self.assertIn("{{c2::b}}", fields[1])

    def test_after_context(self):
        """After context should include unhidden items after the cloze"""
        gen = self._make_gen(before=0, prompt=1, after=1)
        items = ["a", "b", "c"]
        fields, full, total = gen.generate(items)
        self.assertEqual(total, 3)
        # First card: cloze on "a", "b" as after context
        self.assertIn("{{c1::a}}", fields[0])
        self.assertIn("b", fields[0])

    def test_before_none_means_all(self):
        """before=None means show all preceding context"""
        gen = self._make_gen(before=None, prompt=1, after=0, maxfields=4)
        items = ["a", "b", "c", "d"]
        fields, full, total = gen.generate(items)
        # Last card (fields[3]): a,b,c should be visible as context before "d"
        last = fields[3]
        self.assertIsInstance(last, list)
        self.assertIn("a", last)
        self.assertIn("b", last)
        self.assertIn("c", last)

    def test_after_none_means_all(self):
        """after=None means show all following context"""
        gen = self._make_gen(before=0, prompt=1, after=None)
        items = ["a", "b", "c", "d"]
        fields, full, total = gen.generate(items)
        # First card: b,c,d should all be visible after context
        first = fields[0]
        self.assertIn("b", first)
        self.assertIn("c", first)
        self.assertIn("d", first)

    # --- No-first-context / No-last-context options ---

    def test_no_first_context(self):
        """options[0]=True: no after-context on the first card"""
        gen = self._make_gen(before=0, prompt=1, after=2,
                             options=[True, False, False, False])
        items = ["a", "b", "c"]
        fields, full, total = gen.generate(items)
        first = fields[0]
        # Should NOT have after context on first card - all non-cloze items should be "..."
        self.assertIsInstance(first, list)
        self.assertEqual(first[1], "...")
        self.assertEqual(first[2], "...")

    def test_no_last_context(self):
        """options[1]=True: no before-context on the last card"""
        gen = self._make_gen(before=2, prompt=1, after=0,
                             options=[False, True, False, False])
        items = ["a", "b", "c"]
        fields, full, total = gen.generate(items)
        last = fields[-1]
        # Should NOT have before context on last card
        self.assertNotIn("b", last.replace("{{c3::b}}", "").replace("{{c3::c}}", ""))

    # --- Custom cloze (with keys and formstr) ---

    def test_custom_cloze_format(self):
        """When original/keys are provided, snippets get inserted back"""
        gen = self._make_gen(before=0, prompt=1, after=0)
        items = ["alpha", "beta"]
        keys = ["1", "2"]
        original = "Before {{1}} middle {{2}} after"
        fields, full, total = gen.generate(items, original, keys)
        self.assertEqual(total, 2)
        self.assertIn("Before", fields[0])
        self.assertIn("after", fields[0])

    def test_custom_cloze_with_tuple_items(self):
        """Multiple phrases with the same key should be handled"""
        gen = self._make_gen(before=0, prompt=1, after=0)
        items = [("first", "second"), "third"]
        keys = ["1", "2"]
        original = "A {{1}} B {{1}} C {{2}}"
        fields, full, total = gen.generate(items, original, keys)
        self.assertEqual(total, 2)

    # --- Full field ---

    def test_full_field_generated(self):
        """Full field should contain all items clozed"""
        gen = self._make_gen(before=0, prompt=1, after=0)
        items = ["a", "b", "c"]
        fields, full, total = gen.generate(items)
        self.assertIsNotNone(full)
        # Full should have all items as clozes
        for item in items:
            self.assertIn(item, str(full))

    def test_unused_fields_cleared(self):
        """Fields beyond the generated count should be empty strings"""
        gen = self._make_gen(before=0, prompt=1, after=0, maxfields=10)
        items = ["a", "b", "c"]
        fields, full, total = gen.generate(items)
        self.assertEqual(total, 3)
        # Should have 10 fields total, last 7 empty
        self.assertEqual(len(fields), 10)
        for f in fields[3:]:
            self.assertEqual(f, "")

    # --- Ellipsis placeholders ---

    def test_ellipsis_for_hidden(self):
        """Items outside context/cloze range should be '...'"""
        gen = self._make_gen(before=0, prompt=1, after=0)
        items = ["a", "b", "c", "d", "e"]
        fields, full, total = gen.generate(items)
        # First card: only "a" clozed, rest should be "..."
        first = fields[0]
        self.assertIsInstance(first, list)
        self.assertEqual(first[1], "...")
        self.assertEqual(first[4], "...")

    # --- Prompt larger than 1 ---

    def test_prompt_2_clozes_two_items(self):
        """prompt=2 with 4 items: total=4, start=2, so 3 cards (idx 2,3,4)"""
        gen = self._make_gen(before=0, prompt=2, after=0)
        items = ["a", "b", "c", "d"]
        fields, full, total = gen.generate(items)
        # total=4, start=prompt=2, loop 2..4 -> 3 cards
        self.assertEqual(total, 3)
        # First generated card (idx=2): clozes items[0:2] = a,b
        first = fields[0]
        self.assertIn("{{c1::a}}", str(first))
        self.assertIn("{{c1::b}}", str(first))


    # --- Empty items ---

    def test_empty_items(self):
        """Empty items list with prompt=1 should return 0 (prompt > length)"""
        gen = self._make_gen(before=0, prompt=1, after=0)
        fields, full, total = gen.generate([])
        self.assertEqual(fields, 0)

    # --- Combined before + after + prompt ---

    def test_combined_before_after_prompt(self):
        """Real-world scenario: before=1, prompt=1, after=1 on 5 items"""
        gen = self._make_gen(before=1, prompt=1, after=1, maxfields=5)
        items = ["a", "b", "c", "d", "e"]
        fields, full, total = gen.generate(items)
        self.assertEqual(total, 5)
        # Middle card (idx=3, fields[2]): "b" before, "c" clozed, "d" after
        mid = fields[2]
        self.assertIsInstance(mid, list)
        self.assertEqual(mid[0], "...")  # a hidden
        self.assertEqual(mid[1], "b")   # before context
        self.assertIn("{{c3::c}}", mid[2])  # clozed
        self.assertEqual(mid[3], "d")   # after context
        self.assertEqual(mid[4], "...")  # e hidden

    # --- Negative / zero prompt ---

    def test_zero_prompt(self):
        """prompt=0 means 0 > length is false, total=len, start=0"""
        gen = self._make_gen(before=0, prompt=0, after=0)
        items = ["a", "b", "c"]
        fields, full, total = gen.generate(items)
        # prompt=0: total=3, start=0, loop range(0,4) = 4 iterations
        # This actually generates cards - each with 0 items clozed (empty cloze window)
        self.assertIsNotNone(fields)


class TestClozeGeneratorHelpers(unittest.TestCase):
    """Test helper methods of ClozeGenerator"""

    def _make_gen(self, before=1, prompt=1, after=0, options=None, maxfields=20):
        if options is None:
            options = [False, False, False, False]
        setopts = ([before, prompt, after], options)
        gen = ClozeGenerator(setopts, maxfields)
        gen.total = 5
        gen.start = 1
        return gen

    def test_format_cloze_strings(self):
        gen = self._make_gen()
        result = gen.formatCloze(["hello", "world"], 3)
        self.assertEqual(result, ["{{c3::hello}}", "{{c3::world}}"])

    def test_format_cloze_tuples(self):
        gen = self._make_gen()
        result = gen.formatCloze([("a", "b"), "c"], 2)
        self.assertEqual(result[0], ["{{c2::a}}", "{{c2::b}}"])
        self.assertEqual(result[1], "{{c2::c}}")

    def test_remove_hints_simple(self):
        gen = self._make_gen()
        result = gen.removeHints(["text::hint", "plain"])
        self.assertEqual(result, ["text", "plain"])

    def test_remove_hints_tuples(self):
        gen = self._make_gen()
        result = gen.removeHints([("a::h1", "b::h2")])
        self.assertEqual(result, [["a", "b"]])

    def test_get_cloze_start_normal(self):
        gen = self._make_gen(prompt=2)
        gen.total = 5
        gen.start = 2
        # idx=3, prompt=2 -> 3-2 = 1
        self.assertEqual(gen.getClozeStart(3), 1)

    def test_get_cloze_start_below_prompt(self):
        gen = self._make_gen(prompt=3)
        gen.total = 5
        gen.start = 3
        # idx=2 < prompt=3 -> return 0
        self.assertEqual(gen.getClozeStart(2), 0)

    def test_get_before_start_zero_before(self):
        """before=0 means no before context"""
        gen = self._make_gen(before=0)
        self.assertIsNone(gen.getBeforeStart(3, 2))

    def test_get_before_start_at_start(self):
        """start_c < 1 means nothing before"""
        gen = self._make_gen(before=2)
        self.assertIsNone(gen.getBeforeStart(1, 0))

    def test_get_after_end_zero_after(self):
        """after=0 means no after context"""
        gen = self._make_gen(after=0)
        self.assertIsNone(gen.getAfterEnd(3))

    def test_get_after_end_at_total(self):
        """At the last card, left=0 so no after"""
        gen = self._make_gen(after=2)
        gen.total = 5
        self.assertIsNone(gen.getAfterEnd(5))


if __name__ == '__main__':
    unittest.main()
