# -*- coding: utf-8 -*-

# Cloze Overlapper Add-on for Anki
#
# Copyright (C)  2016-2019 Aristotelis P. <https://glutanimate.com/>
# Updated for modern Anki (2.1.45+)

"""
Generates cloze texts for overlapping clozes.
Simple incremental reveal algorithm.
"""

MODE_NONE = 0
MODE_PREVIOUS = 1
MODE_ALL = 2


class ClozeGenerator(object):
    """Cloze generator — incremental reveal pattern"""

    cformat = "{{c%i::%s}}"

    def __init__(self, context_mode, maxfields):
        self.maxfields = maxfields
        self.context_mode = context_mode

    def generate(self, items, original=None, keys=None):
        """Generate overlapping cloze fields.

        context_mode controls what's visible besides the current cloze:
          MODE_NONE (0):     only the current item is clozed, everything else is "..."
          MODE_PREVIOUS (1): previous items shown, current clozed, future "..."
          MODE_ALL (2):      all items shown, only current is clozed

        Returns (fields, full, count).
        """
        length = len(items)
        if length < 1:
            return 0, None, None
        if length > self.maxfields:
            return None, None, length

        fields = []
        for card_idx in range(length):
            snippets = []
            for item_idx, item in enumerate(items):
                clean = self._strip_hint(item)
                if item_idx == card_idx:
                    # Current item — this is the cloze
                    snippets.append(self.cformat % (card_idx + 1, clean))
                elif item_idx < card_idx:
                    # Previous item
                    if self.context_mode in (MODE_PREVIOUS, MODE_ALL):
                        snippets.append(clean)
                    else:
                        snippets.append("...")
                else:
                    # Future item
                    if self.context_mode == MODE_ALL:
                        snippets.append(clean)
                    else:
                        snippets.append("...")
            field = self._format_snippets(snippets, original, keys)
            fields.append(field)

        count = len(fields)

        if self.maxfields > length:
            fields += [""] * (self.maxfields - length)

        return fields, "", count

    @staticmethod
    def _strip_hint(item):
        """Remove cloze hint (everything after ::) from an item"""
        if isinstance(item, (list, tuple)):
            return [i.split("::")[0] for i in item]
        return item.split("::")[0]

    @staticmethod
    def _format_snippets(snippets, original, keys):
        """Insert snippets back into original text, if available"""
        if not original:
            return snippets
        html = original
        for nr, phrase in zip(keys, snippets):
            if not isinstance(phrase, (list, tuple)):
                html = html.replace("{{" + nr + "}}", phrase, 1)
            else:
                for sub in phrase:
                    html = html.replace("{{" + nr + "}}", sub, 1)
        return html
