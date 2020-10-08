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
    def __init__(
            self, txt, bold=False, ital=False, xspace=True, is_indent=False):
        """
        :param txt: A string, being the word itself.
        :param bold: A bool, whether to bold this word.
        :param ital: A bool, whether to italicize this word.
        :param xspace: A bool, whether a space may follow this word.
        Defaults to True; set to False for indents and perhaps
        punctuation.
        :param is_indent: A bool, whether this FWord is an indent.
        """
        self.txt = txt
        self.bold = bold
        self.ital = ital
        self.xspace = xspace
        self.is_indent = is_indent

    @staticmethod
    def _examine_fwords(fwords: list, fonts: dict, existing_dict=None):
        """
        INTERNAL USE:
        Examine the list of FWord objects, using the provided `fonts`
        (a dict, whose values are ImageFont objects, and whose keys are
        'main', 'bold', 'ital', and 'boldital'), to return a dict of
        various information about those FWord obj's (see below).

        :param fwords: A list of FWord objects.
        :param fonts: A dict, whose values are ImageFont objects, and
        whose keys are 'main', 'bold', 'ital', and 'boldital'.
        (HINT: `TextBox.formatted_fonts` attribute is probably what you
        want to use for the `fonts` argument here.)
        :param existing_dict: To resume writing to a dict that was
        was previously returned by this method, pass that dict as
        `existing_dict` here.
        :returns: A dict of the following information:
        -- 'word_px_dict' -> A dict, whose keys are FWord objects and
            whose values are a 2-tuple of (width, height) for that FWord
        -- 'font_dict' -> A dict, whose keys are FWord objects and whose
            values are the ImageFont object for that FWord
        -- 'total_word_w' -> An integer, being the total width in px of
            the words.
        -- 'total_word_h' -> An integer, being the max height in px of
            any of the words.
        -- 'space_w' -> An integer, being the width in px of a single
            space character, using the 'main' font.
        """

        from PIL import Image, ImageDraw

        # Dummy ImageDraw object for checking size.
        dr = ImageDraw.Draw(Image.new('RGBA', (1, 1)), 'RGBA')

        if existing_dict is None:
            # Get the width of a single space character in px
            space_w, _ = dr.textsize(' ', font=fonts['main'])
            existing_dict =  {
                'word_px_dict': {},
                'font_dict': {},
                'total_word_w': 0,
                'total_word_h': 0,
                'space_w': space_w
            }

        for fword in fwords:
            # Get the styling for this word (e.g., 'boldital'), which also
            # serves as a key in the `.formatted_fonts` dict.
            styling = f"{'bold' * fword.bold}{'ital' * fword.ital}"
            if styling == '':
                styling = 'main'

            # Get the font for this styling, but fall back to main, if not set.
            font = fonts.get(styling, fonts['main'])

            word_w, word_h = dr.textsize(fword.txt, font=font)
            existing_dict['word_px_dict'][fword] = (word_w, word_h)
            existing_dict['font_dict'][fword] = font
            existing_dict['total_word_w'] += word_w
            if word_h > existing_dict['total_word_h']:
                existing_dict['total_word_h'] = word_h

        return existing_dict

    @staticmethod
    def recompile_fwords(fwords: list, exclude_indent=False):
        """
        Recompile a list of FWord objects (e.g., what gets returned from
        the `TextBox.write()` method) into a single string (plain text),
        discarding any formatting.
        """
        fl = FLine(fwords=fwords)
        return fl.simplify(exclude_indent=exclude_indent)


class FLine:
    """
    A line of formatted text.
    """
    def __init__(
            self, fwords: list, justifiable=False, fword_info=None):
        """
        A line of formatted text.

        :param fwords: A list of FWord objects that make up the line of
        text.
        :param justifiable: A bool, whether or not this line can be
        block-justified.
        :param fword_info: A dict generated by `FWord._examine_fwords()`
        that provides info on word sizes, fonts, etc. (See docs on
        `FWord._examine_fwords()` for all data contained.)
        """
        self.fwords = fwords
        self.justifiable = justifiable
        self.staged = None
        self.fword_info = fword_info

    def _extract_fword_info(self, fword_info: dict, use_staged=True):
        """
        Extract from `fword_info` (a dict generated by the
        `FWord._examine_fwords()` static method) the relevant info for
        writing a particular this FLine object. If `use_staged=True` (on
        by default) will use the list in the `.staged` attribute of this
        FLine; and if False, then will use the `.fwords` attribute.

        :param fword_info: A dict generated by `FWord._examine_fwords()`
        :param use_staged: Extract the info for the `.staged` attribute,
        rather than `.fwords`. (Defaults to True)
        :returns: Returns a dict of this information:
        -- 'line_word_w' -> The width in px of all words, with no spaces
        -- 'line_word_h' -> The max height in px of any word
        -- 'line_w' -> The width of the entire line, including spaces
        -- 'space_w' -> The width in px of a single space character
        -- 'total_spaces' -> The total number of space characters in
            this line
        """
        target = self.staged
        if not use_staged or self.staged is None:
            target = self.fwords

        line_word_w = 0
        line_word_h = 0
        line_w = 0
        total_spaces = 0
        space_w = fword_info['space_w']

        i = len(target)
        for fw in target:
            line_word_w += fword_info['word_px_dict'][fw][0]
            line_w += fword_info['word_px_dict'][fw][0]
            if fword_info['word_px_dict'][fw][1] > line_word_h:
                line_word_h = fword_info['word_px_dict'][fw][1]

            # For all but the last FWord (or any FWords for whom `.xspace`
            # is not true), add a space
            if i != 1 and fw.xspace:
                line_w += space_w
                total_spaces += 1
            i -= 1
        return {
            'line_word_w': line_word_w,
            'line_word_h': line_word_h,
            'line_w': line_w,
            'space_w': space_w,
            'total_spaces': total_spaces
        }

    def simplify(self, exclude_indent=False):
        """
        Return the text of this line in plain text (a string).

        :param exclude_indent: Do not include the indent (if any).
        Defaults to False.
        """
        c_txt = ''
        if self.fwords is None:
            return None
        if len(self.fwords) == 0:
            return c_txt
        for i in range(len(self.fwords)):
            sp = ''
            if exclude_indent and self.fwords[i].is_indent:
                continue
            if i != len(self.fwords) - 1:
                # Don't add a final space for the last fword in the list
                sp = self.fwords[i].xspace * ' '
            c_txt = f"{c_txt}{self.fwords[i].txt}{sp}"
        return c_txt

    def to_pline(self, exclude_indent=False):
        """
        Convert this FLine object (formatted text) into a PLine object
        (plain text), discarding any encoded formatting, but retaining
        whether it is justifiable.

        :param exclude_indent: Do not include the indent (if any).
        Defaults to False.
        """
        txt = self.simplify(exclude_indent=exclude_indent)
        return PLine(txt=txt, justifiable=self.justifiable)

    def _stage(self, indent=None):
        """
        INTERNAL USE:
        Stage this line for writing, inserting an FWord at the beginning
        for the indent, if any.
        :param indent: A string for the indentation. (None is OK.)
        """
        self.staged = self.fwords.copy()
        if isinstance(indent, str):
            indent = FWord(txt=indent, bold=False, ital=False, xspace=False)
            self.staged.insert(0, indent)
        return self.staged

    def _unstage(self):
        """
        INTERNAL USE:
        The writing of this line was unsuccessful, so unstage it.
        """
        self.staged = None


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
        self.staged = None

    def simplify(self, exclude_indent=False):
        """
        Return the text of this line in plain text (a string).

        :param exclude_indent: Cull the indent (if any) from the
        returned text. Defaults to False.
        """
        if exclude_indent:
            return self.txt.lstrip(' ')
        return self.txt

    def to_fline(self, exclude_indent=False):
        """
        Convert this PLine object (plain text) into a FLine object
        (formatted text), retaining whether it is justifiable. No
        formatting will actually be encoded, and no format codes in the
        text of this PLine object will be converted.

        :param exclude_indent: Cull the indent (if any) from the
        text before converting to a FLine. Defaults to False.
        :returns: A FLine object containing the text of this PLine.
        """
        txt = self.simplify(exclude_indent=exclude_indent)
        return FLine(fwords=flat_parse(txt), justifiable=self.justifiable)

    def _stage(self, indent=None):
        """
        INTERNAL USE:
        Stage this line for writing, adding the leading indent, if any.
        :param indent: A string for the indentation. (May be None)
        :returns: The plain text of the staged line.
        """
        self.staged = self.txt
        if isinstance(indent, str):
            self.staged = indent + self.staged
        return self.staged

    def _unstage(self):
        """
        INTERNAL USE:
        The writing of this line was unsuccessful, so unstage it.
        """
        self.staged = None


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

        # For staging the next line to write, while writing is being attempted.
        self.staged = None

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

        # A dict containing size, font, etc. of each FWord in the `lines`
        # (gets calculated during text wrapping, and might as well store it
        # to avoid calculating twice or more).
        self.fword_info = {}

    def simplify(self, exclude_indent=False):
        """
        Convert this UnwrittenLines object into a list of lines of text
        (i.e. strings), without any encoded formatting information.
        :param exclude_indent: Do not include the indents (if any).
        Defaults to False.
        :returns: A list of strings, each being an unwritten line.
        """
        simplified_lines = []
        for obj in self.lines:
            # PLine and FLine both have a `.simplify()` method.
            simplified_lines.append(obj.simplify(exclude_indent=exclude_indent))
        return simplified_lines

    def print(self):
        """
        Print the plain text of this UnwrittenLines to console.
        """
        simple_lines = self.simplify()
        for line in simple_lines:
            print(line)

    @property
    def remaining(self):
        """
        How many lines remain unwritten.
        """
        if self.lines is None:
            return None
        return len(self.lines)

    def _stage_next_line(self):
        """
        INTERNAL USE:
        Stage the next line for writing, and return that line.
        (Use only while writing is being attempted.)
        """
        if self.remaining in [0, None]:
            return None
        self.staged = self.lines[0]
        return self.staged

    def _successful_write(self):
        """
        INTERNAL USE:
        The staged line was successfully written. Remove it, and reset
        the staged line to None.
        """
        self.staged = None
        self.lines.pop(0)

    def _unstage(self):
        """
        INTERNAL USE:
        The staged line was NOT successfully written. Put the line back
        in the list (i.e. just set `.staged` to None).
        """
        self.staged = None


def parse_into_line(
        text: str, formatting: bool, justifiable=True, discard_formatting=False):
    """
    Parse text into either an FLine (i.e. `formatting=True` is passed)
    or a PLine (i.e. `formatting=False` is passed). Also encode whether
    this line is justifiable (defaults to True).

    NOTE: This function is agnostic as to line length. It will form a
    single line out of the entire text, and it may not fit within a
    given textbox.
    :param text: A string, of the text to parse.
    :param formatting: A bool, whether to parse format codes (e.g.,
    '<b>' or '</b>' in the input text. (Also controls whether to return
    whether a FLine or PLine object: True -> FLine; False -> Pline.)
    :param discard_formatting: A bool, whether to discard all formatting
    and only write plain text. (Will have no effect unless parameter
    `formatting=` is True.) Defaults to False.
    :param justifiable: A bool, whether the text in this line is able to
    be block-justified. Defaults to True.
    :returns: Either a FLine object (if `formatting=True` is passed) or
    a PLine object (if `formatting=False` is passed).
    """
    fwords = all_parse(text, formatting, discard_formatting)
    return compile_line(fwords, formatting, justifiable)


def compile_line(fwords: list, formatting: bool, justifiable=True):
    """
    Compile a list of FWord objects (`fwords` arg) and whether or not
    `formatting` is encoded, into an FLine (i.e. `formatting=True` is
    passed) or a PLine (i.e. `formatting=False` is passed). Also encode
    whether this line is justifiable (defaults to True).

    NOTE: This function is agnostic as to line length. It will form a
    single line out of all of the passed fwords.
    :param fwords: A list of FWord objects.
    :param formatting: A bool, whether formatting is encoded in the
    FWord objects (i.e. whether to return a FLine or PLine).
    :param justifiable: A bool, whether the text in this line is able to
    be block-justified.
    :returns: Either a FLine object (if `formatting=True` is passed) or
    a PLine object (if `formatting=False` is passed).
    """
    fline_version = FLine(fwords, justifiable)
    if formatting:
        return fline_version
    else:
        return fline_version.to_pline()


def all_parse(text: str, formatting: bool, discard_formatting=False):
    """
    Split text into a list of FWord objects (i.e. the text of each word
    with encoded formatting), but rely on parameter `formatting=` to
    determine whether format codes get parsed or left in the text.

    :param text: A string, of the text to parse.
    :param formatting: A bool, whether to parse format codes (e.g.,
    '<b>' or '</b>' in the input text.
    :param discard_formatting: A bool, whether to discard all formatting
    and only write plain text. (Will have no effect unless parameter
    `formatting=` is True.) Defaults to False.
    """
    if formatting:
        return format_parse(text, discard_formatting=discard_formatting)
    else:
        return flat_parse(text)


def flat_parse(text) -> list:
    """
    Split text into a list of FWord objects (i.e. the text of each word
    with encoded formatting), but treat any format codes as words or
    part of words -- i.e. '<b>the' will remain '<b>the'. Each FWord in
    the returned list will have `False` for both its `.bold` and `.ital`
    attributes.
    """
    text = text.strip('\r\n')
    text = text.replace('\r', '\n')
    text = text.replace('\n', ' ')

    raw_words = text.split(' ')
    fwords = []
    for word in raw_words:
        fwords.append(FWord(word, bold=False, ital=False))

    return fwords


def format_parse_deep(
        text, discard_formatting=False, start_bold=False,
        start_ital=False):
    """
    Split text into a list of FWord objects (i.e. the text of each word
    with encoded formatting); return a 3-tuple of the list of FWord
    objects, the final bold (bool), and the final ital setting (bool).

    :param text: A string, of the text to parse.
    :param discard_formatting: A bool, whether to discard all formatting
    and only write plain text. Defaults to False.
    :param discard_formatting:
    :param start_bold: The bold-setting to assume as of the first
    character.
    :param start_ital: The italic-setting to assume as of the first
    character.
    :returns: a 3-tuple of the list of FWord objects; the final bold
    (a bool), and the final ital setting (a bool).
    """

    format_codes = ('<b>', '</b>', '<i>', '</i>')

    bold = start_bold
    ital = start_ital

    text = text.strip('\r\n')
    text = text.replace('\r', '\n')
    text = text.replace('\n', ' ')

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

    return fwords, bold, ital


def format_parse(
        text, discard_formatting=False) -> list:
    """
    Split text into a list of FWord objects (i.e. the text of each word
    with encoded formatting).

    (Equivalent to `format_parse_deep()`, except that it does not return
    the final bold or ital values.)
    """
    fwords, _, __ = format_parse_deep(text, discard_formatting)

    return fwords