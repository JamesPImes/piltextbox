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
    The text of a word, whether or not it should be bolded and/or
    italicized, and whether it should be followed by a space.
    """
    def __init__(self, txt, bold=False, ital=False, xspace=True):
        """
        :param txt: A string, being the word itself.
        :param bold: A bool, whether to bold this word.
        :param ital: A bool, whether to italicize this word.
        :param xspace: A bool, whether a space may follow this word.
        Defaults to True; set to False for indents and perhaps
        punctuation.
        """
        self.txt = txt
        self.bold = bold
        self.ital = ital
        self.xspace = xspace


class FLine:
    """
    A line of formatted text.
    """
    def __init__(self, fwords: list, justifiable=False):
        """

        :param fwords: A list of FWord objects that make up the line of
        text.
        :param justifiable: A bool, whether or not this line can be
        block-justified.
        """
        self.fwords = fwords
        self.justifiable = justifiable

    def simplify(self):
        """
        Return the text of this line in plain text (a string).
        """
        c_txt = ''
        for i in range(len(self.fwords)):
            sp = ''
            if i != len(self.fwords) - 1:
                # Don't add a final space for the last fword in the list
                sp = self.fwords[i].xspace * ' '
            c_txt = f"{c_txt}{self.fwords[i].txt}{sp}"

        return c_txt

    def to_pline(self):
        """
        Convert this FLine object (formatted text) into a PLine object
        (plain text), discarding any encoded formatting, but retaining
        whether it is justifiable.
        """
        return PLine(txt=self.simplify(), justifiable=self.justifiable)


class PLine:
    """
    A line of plain text.
    """
    def __init__(self, txt, justifiable=False):
        """
        :param txt: A line of text (i.e. a single string).
        :param justifiable: A bool, whether or not this line can be
        block-justified.
        """
        self.txt = txt
        self.justifiable = justifiable


class UnwrittenLines:
    """
    A container for unwritten lines, either formatted or plain (but not
    both types).
    """
    def __init__(self, lines=None, formatting=None):
        """
        :param lines: A list of PLine objects or a list of FLine objects
        (but not a mixture of the two) -- i.e. either unwritten plain
        lines, or unwritten formatted lines. If not specified, defaults
        to an empty list.
        :param formatting: A bool, whether or not the objects are FLine
        (i.e. `=True`; for formatted lines) or PLine (i.e. `=False`; for
        plain lines). If passed as None (the default), will check the
        type of the first element in the `lines` list (if any). (It may
        remain None.)
        """
        if lines is None:
            lines = []
        self.lines = lines

        if formatting is None:
            if not isinstance(lines, list):
                pass
            elif len(lines) == 0:
                pass
            elif isinstance(lines[0], PLine):
                formatting = False
            elif isinstance(lines[0], FLine):
                formatting = True
        self.formatting = formatting

    def simplify(self):
        """
        Convert this UnwrittenLines object into a list of lines of text
        (i.e. strings), without any encoded formatting information.
        """
        simplified_lines = []
        if self.formatting:
            for obj in self.lines:
                simplified_lines.append(obj.simplify())
        else:
            for obj in self.lines:
                simplified_lines.append(obj.txt)
        return simplified_lines

    def print(self):
        """
        Print the plain text of this UnwrittenLines to console.
        """
        sl = self.simplify()
        for l in sl:
            print(l)

def flat_parse(text) -> list:
    """
    Split text into a list of FWord objects (i.e. the text of each word
    with encoded formatting), but treat any format codes as words or
    part of words -- i.e. '<b>the' will remain '<b>the'. Each FWord in
    the returned list will have `False` for both its `.bold` and `.ital`
    attributes.
    """
    raw_words = text.split(' ')
    fwords = []
    for word in raw_words:
        fwords.append(FWord(word, bold=False, ital=False))

    return fwords


def format_parse(text, discard_formatting=False) -> list:
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
            if discard_formatting:
                fwords.append(FWord(txt, bold=False, ital=False))
            else:
                fwords.append(FWord(txt, bold=bold, ital=ital))

        # In case no bold or ital codes were added to the respective lists...
        all_bold.append(bold)
        all_ital.append(ital)

        # Set the first element in each list as the final value for bold/ital
        bold = all_bold[0]
        ital = all_ital[0]

    return fwords
