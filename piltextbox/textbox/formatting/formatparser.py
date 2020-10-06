# Copyright (c) 2020, James P. Imes. All rights reserved.

"""
A naive parser, taking raw text with optional format codes '<b>',
'</b>', '<i>', and '</i>' and generating a list of FWord objects.

NOTE: Format codes can only exist at word boundaries (and must be
outside punctuation).
"""

class FWord:
    """
    The text of a word, and whether or not it should be bolded and/or
    italicized.
    """
    def __init__(self, txt, bold=False, ital=False):
        self.txt = txt
        self.bold = bold
        self.ital = ital


def format_parse(text) -> list:
    """
    Split text into a list of FWord objects with encoded formatting.
    """

    format_codes = ('<b>', '</b>', '<i>', '</i>')

    bold = False
    ital = False
    raw_words = text.split(' ')
    fwords = []
    for word in raw_words:
        txt = word

        while True:
            if not txt.startswith(format_codes):
                break
            # TODO: Set `bold` and `ital` appropriately, and cull code from `txt`
        
        while True:
            if not txt.endswith(format_codes):
                break
            # TODO: Set `bold` and `ital` appropriately, and cull code from `txt`

        if len(txt) > 0:
            fwords.append(FWord(txt, bold=bold, ital=ital))

    return fwords


wrds = format_parse('Testing one, two, three, four.')
for wrd in wrds:
    print(wrd)
    print(wrd.txt)
    print(wrd.bold)
    print(wrd.ital)