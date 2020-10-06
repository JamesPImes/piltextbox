# Copyright (c) 2020, James P. Imes. All rights reserved.

"""
Parse raw text (with optional format codes '<b>', '</b>', '<i>', and
'</i>') into a list of FWord objects, which encode bold and ital for
each word.

NOTE: Format codes can only exist at word boundaries (and must be
outside of any punctuation).
    ex: '<b>The quick brown fox</b> jumped <i>over and over.</i>'  # OK
        'The qui<b>ck</b> brown fox.'  # The '<b>' will NOT be found
        '<b>The quick brown fox</b>.'  # The '</b>' will NOT be found
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
    Split text into a list of FWord objects (i.e. the text of each word
    with encoded formatting).
    """

    format_codes = ('<b>', '</b>', '<i>', '</i>')

    bold = False
    ital = False
    raw_words = text.split(' ')
    fwords = []
    for word in raw_words:
        txt = word

        # Cull each format code from start of `txt`, and set the
        # appropriate bool variable to the equivalent value
        while True:
            if not txt.startswith(format_codes):
                break
            if txt.startswith('<b>'):
                bold = True
                txt = txt[len('<b>'):]
            if txt.startswith('</b>'):
                bold = False
                txt = txt[len('</b>'):]
            if txt.startswith('<i>'):
                ital = True
                txt = txt[len('<i>'):]
            if txt.startswith('</i>'):
                ital = False
                txt = txt[len('</i>'):]

        # After we set the `txt`, we want the last-specified bold code
        # and ital code (each); but since we'll check for them right-to-
        # left, we'll only want the first element in these lists.
        all_bold = []
        all_ital = []

        # Cull each format code from end of `txt`, and store its
        # equivalent value to the appropriate list.
        while True:
            if not txt.endswith(format_codes):
                break
            if txt.endswith('<b>'):
                all_bold.append(True)
                txt = txt[:-len('<b>')]
            if txt.endswith('</b>'):
                all_bold.append(False)
                txt = txt[:-len('</b>')]
            if txt.endswith('<i>'):
                all_ital.append(True)
                txt = txt[:-len('<i>')]
            if txt.endswith('</i>'):
                all_ital.append(False)
                txt = txt[:-len('</i>')]

        # Create an FWord object for this word
        if len(txt) > 0:
            fwords.append(FWord(txt, bold=bold, ital=ital))

        # In case no bold or ital codes were added to the respective lists...
        all_bold.append(bold)
        all_ital.append(ital)

        # Set the first element in each list as the final value for bold/ital
        bold = all_bold[0]
        ital = all_ital[0]

    return fwords
