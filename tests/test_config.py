# -*- coding: utf-8 -*-
"""Edge case tests for config parsing (no Anki dependency)"""

import unittest


# NOTE: The parsing logic below is replicated from config.py because that module
# imports aqt (Anki's Qt framework) at module level, making it unimportable
# without a running Anki instance. The real config.py also calls strip_html()
# on input before parsing. If the parsing logic in config.py changes, these
# tests must be updated to match.

def parseNoteSettings(field, dflt_set=None, dflt_opt=None):
    """
    Parse note settings from a plain text field.
    Extracted from config.py for testing without Anki.
    """
    if dflt_set is None:
        dflt_set = [1, 1, 0]
    if dflt_opt is None:
        dflt_opt = [False, False, False, False]

    if field is None:
        return (dflt_set, dflt_opt)

    options, settings, opts, sets = None, None, None, None

    lines = field.replace(" ", "").split("|")
    if not lines:
        return (dflt_set, dflt_opt)
    settings = lines[0].split(",")
    if len(lines) > 1:
        options = lines[1].split(",")

    if not options and not settings:
        return (dflt_set, dflt_opt)

    if not settings:
        sets = dflt_set
    else:
        sets = []
        for idx, item in enumerate(settings[:3]):
            try:
                sets.append(int(item))
            except ValueError:
                sets.append(None)
        length = len(sets)
        if length == 3 and isinstance(sets[1], int):
            pass
        elif length == 2 and isinstance(sets[0], int):
            sets = [sets[1], sets[0], sets[1]]
        elif length == 1 and isinstance(sets[0], int):
            sets = [dflt_set[0], sets[0], dflt_set[2]]
        else:
            sets = dflt_set

    if not options:
        opts = dflt_opt
    else:
        opts = []
        for i in range(4):
            try:
                if options[i] == "y":
                    opts.append(True)
                else:
                    opts.append(False)
            except IndexError:
                opts.append(dflt_opt[i])

    return (sets, opts)


def createNoteSettings(setopts):
    """Create plain text settings string (from config.py)"""
    set_str = ",".join(str(i) if i is not None else "all" for i in setopts[0])
    opt_str = ",".join("y" if i else "n" for i in setopts[1])
    return set_str + " | " + opt_str


class TestParseNoteSettings(unittest.TestCase):
    """Test parseNoteSettings edge cases"""

    def test_normal_settings(self):
        """Standard settings string: '1,1,0 | y,n,n,n'"""
        sets, opts = parseNoteSettings("1,1,0 | y,n,n,n")
        self.assertEqual(sets, [1, 1, 0])
        self.assertEqual(opts, [True, False, False, False])

    def test_empty_string(self):
        """Empty string should return defaults"""
        sets, opts = parseNoteSettings("")
        self.assertEqual(sets, [1, 1, 0])
        self.assertEqual(opts, [False, False, False, False])

    def test_none_input(self):
        """None input should return defaults (bug fix test)"""
        sets, opts = parseNoteSettings(None)
        self.assertEqual(sets, [1, 1, 0])
        self.assertEqual(opts, [False, False, False, False])

    def test_whitespace_only(self):
        """Whitespace-only string should return defaults"""
        sets, opts = parseNoteSettings("   ")
        self.assertEqual(sets, [1, 1, 0])
        self.assertEqual(opts, [False, False, False, False])

    def test_settings_only_no_options(self):
        """Settings without pipe/options should use default options"""
        sets, opts = parseNoteSettings("2,1,1")
        self.assertEqual(sets, [2, 1, 1])
        self.assertEqual(opts, [False, False, False, False])

    def test_single_setting_value(self):
        """Single value should be treated as prompt"""
        sets, opts = parseNoteSettings("3")
        # length=1, isinstance(sets[0], int)=True -> [dflt[0], 3, dflt[2]]
        self.assertEqual(sets, [1, 3, 0])

    def test_two_setting_values(self):
        """Two values: first=prompt, second=before+after (symmetric)"""
        sets, opts = parseNoteSettings("2,3")
        # length=2, isinstance(sets[0], int)=True -> [sets[1], sets[0], sets[1]]
        self.assertEqual(sets, [3, 2, 3])

    def test_all_keyword_in_settings(self):
        """'all' should parse as None (meaning all context)"""
        sets, opts = parseNoteSettings("all,1,all")
        self.assertEqual(sets, [None, 1, None])

    def test_partial_options(self):
        """Fewer than 4 option values should fill from defaults"""
        sets, opts = parseNoteSettings("1,1,0 | y,n")
        self.assertEqual(opts, [True, False, False, False])

    def test_extra_options_ignored(self):
        """More than 4 option values should be truncated"""
        sets, opts = parseNoteSettings("1,1,0 | y,y,y,y,y,y")
        self.assertEqual(len(opts), 4)
        self.assertEqual(opts, [True, True, True, True])

    def test_garbage_settings(self):
        """Completely invalid settings should return defaults"""
        sets, opts = parseNoteSettings("abc,def,ghi")
        # All ValueError -> sets = [None, None, None], length=3
        # isinstance(sets[1], int) is False -> falls through
        # length != 2, length != 1 -> sets = dflt_set
        self.assertEqual(sets, [1, 1, 0])

    def test_mixed_valid_invalid_settings(self):
        """Mix of valid and invalid: 'abc,2,xyz'"""
        sets, opts = parseNoteSettings("abc,2,xyz")
        # sets = [None, 2, None], length=3, isinstance(sets[1], int)=True -> pass
        self.assertEqual(sets, [None, 2, None])

    def test_extra_spaces(self):
        """Spaces should be stripped"""
        sets, opts = parseNoteSettings("  1 , 1 , 0  |  y , n , n , n  ")
        self.assertEqual(sets, [1, 1, 0])
        self.assertEqual(opts, [True, False, False, False])

    def test_negative_values(self):
        """Negative numbers are valid ints and get parsed (caller's problem)"""
        sets, opts = parseNoteSettings("-1,1,0")
        self.assertEqual(sets, [-1, 1, 0])

    def test_zero_prompt(self):
        """Zero prompt is a valid integer setting"""
        sets, opts = parseNoteSettings("1,0,1")
        self.assertEqual(sets, [1, 0, 1])

    def test_multiple_pipes(self):
        """Multiple pipes should only use first two segments"""
        sets, opts = parseNoteSettings("1,1,0 | y,n,n,n | extra,stuff")
        self.assertEqual(sets, [1, 1, 0])
        self.assertEqual(opts, [True, False, False, False])


class TestCreateNoteSettings(unittest.TestCase):
    """Test createNoteSettings edge cases"""

    def test_normal_roundtrip(self):
        """Settings should survive a create -> parse roundtrip"""
        original = ([1, 1, 0], [True, False, False, False])
        text = createNoteSettings(original)
        parsed = parseNoteSettings(text)
        self.assertEqual(parsed, original)

    def test_none_values_roundtrip(self):
        """None values (all context) should survive roundtrip"""
        original = ([None, 1, None], [False, False, False, False])
        text = createNoteSettings(original)
        self.assertIn("all", text)
        parsed = parseNoteSettings(text)
        self.assertEqual(parsed, original)

    def test_all_options_true(self):
        text = createNoteSettings(([1, 1, 0], [True, True, True, True]))
        self.assertIn("y,y,y,y", text)

    def test_create_format(self):
        """Output should be 'set1,set2,set3 | opt1,opt2,opt3,opt4'"""
        text = createNoteSettings(([2, 3, 1], [True, False, True, False]))
        self.assertEqual(text, "2,3,1 | y,n,y,n")


class TestOverlapperEdgeCases(unittest.TestCase):
    """Test overlapper edge cases that don't require Anki"""

    # Matches the regex in overlapper.py ClozeOverlapper.creg
    creg = r"(?s)\[\[oc(\d+)::((.*?)(::(.*?))?)?\]\]"

    def test_cloze_regex_basic(self):
        """Test the cloze regex pattern matches correctly"""
        import re
        creg = self.creg

        # Basic match
        m = re.findall(creg, "[[oc1::hello]]")
        self.assertEqual(len(m), 1)
        self.assertEqual(m[0][0], "1")  # number
        self.assertEqual(m[0][1], "hello")  # content

    def test_cloze_regex_with_hint(self):
        import re
        creg = self.creg

        m = re.findall(creg, "[[oc1::answer::hint]]")
        self.assertEqual(m[0][0], "1")
        self.assertEqual(m[0][2], "answer")
        self.assertEqual(m[0][4], "hint")

    def test_cloze_regex_empty_content(self):
        """Empty cloze should still match"""
        import re
        creg = self.creg

        m = re.findall(creg, "[[oc1::]]")
        self.assertEqual(len(m), 1)
        self.assertEqual(m[0][0], "1")
        self.assertEqual(m[0][1], "")

    def test_cloze_regex_no_content(self):
        """Cloze with no :: should still match the number"""
        import re
        creg = self.creg

        # This won't match because :: is required
        m = re.findall(creg, "[[oc1]]")
        self.assertEqual(len(m), 0)

    def test_cloze_regex_multiline(self):
        """Regex should match across lines due to (?s) flag"""
        import re
        creg = self.creg

        m = re.findall(creg, "[[oc1::line1\nline2]]")
        self.assertEqual(len(m), 1)

    def test_cloze_regex_multiple(self):
        """Multiple clozes in one string"""
        import re
        creg = self.creg

        text = "[[oc1::first]] and [[oc2::second]]"
        m = re.findall(creg, text)
        self.assertEqual(len(m), 2)

    def test_cloze_regex_high_numbers(self):
        """Cloze numbers > 20 should still be matched by regex"""
        import re
        creg = self.creg

        m = re.findall(creg, "[[oc999::content]]")
        self.assertEqual(m[0][0], "999")


if __name__ == '__main__':
    unittest.main()
