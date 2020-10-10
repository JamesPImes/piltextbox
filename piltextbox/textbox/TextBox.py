# Copyright (c) 2020, James P. Imes. All rights reserved.

"""
The main TextBox object, holding the PIL.Image and PIL.ImageDraw objects
and methods for configuring and writing text.
"""

from PIL import Image, ImageDraw, ImageFont
from .formatting import FWord, FLine, PLine, UnwrittenLines
from .formatting import format_parse_deep, all_parse, parse_into_line


class TextBox:
    """
    A container for a PIL.Image.Image object with functionality for
    streamlined text writing. (Currently in 'RGBA' mode only.)

    Access the Image object of the writable area in `.im` attribute
    (excludes margins, if any).
    Access a PIL.ImageDraw.ImageDraw object of the writable area in
    `.text_draw` attribute.
    IMPORTANT: To get a *copy* of the Image (that leaves the `.im`
    attribute separate and intact), use the `.render()` method, which
    will include the margins (if any).

    Use `.write_paragraph()` to write paragraphs (or paragraph-like
    text) with automatic linebreaks and indents, with optional block-
    justified.

    Use `.write_line()` to write individual lines, with optional indent,
    and optionally block-justified.

    Use `.write()` to write word-by-word, but with block-justification
    not allowed.

    IMPORTANT: If changing the font size or font typeface, use the
    `.set_truetype_font()` method. (Changing a font AFTER any particular
    text has been word-wrapped and/or formatted will NOT have an effect
    on that text. There is no 'undo', so any text that is written stays
    written. Moreover, any words or lines returned as unwritten (e.g.,
    if there was not enough space in the textbox to write it all) will
    NOT capture subsequent changes to fonts; and in fact doing so will
    probably have unintended consequences. Best practice is to first set
    all fonts, then write all text that use those fonts, and repeat as
    necessary.

    FOR FORMATTED TEXT (bold / ital):
    User MUST explicitly set 'bold', 'ital', and 'boldital' fonts with
    `.set_truetype_font()` method BEFORE attempting to write any
    formatted text. Otherwise, all formatted text will simply use the
    main font that was set at the time.
        Example (for a TextBox object stored as variable `tb`):
        ```
        # Set 'main' font (also sets `.font` instance variable).
        tb.set_truetype_font(
            size=14, `typeface='<filepath1>' style='main')

        # Do not need to specify size after it's been set for 'main'.
        tb.set_truetype_font(typeface='<filepath2>' style='bold')
        tb.set_truetype_font(typeface='<filepath3>' style='ital')
        tb.set_truetype_font0(typeface='<filepath4>' style='boldital')
        ```

    Include these format codes within the string passed to the writing
    method (AND specify `formatting=True` in the method) in order to
    toggle formatted text:
    -- Turn bold on and off with codes '<b>' and '</b>'.
    -- Turn italics on and off with codes '<i>' and '</i>'.

    Turning bold/ital on when writing one string (with any writing
    function) will NOT keep for the next written string.
        ex1: '<b>The quick brown fox'  ->  written in bold
        ex2: 'jumped over'  ->  not written in bold (or ital)
        ex3: '<b><i>the lazy</b> dog</i>'
            -> `the lazy` is bold+ital; `dog` is ital only.

    Format codes can ONLY be captured at the outside of words, and
    OUTSIDE all punctuation.
        ex4: '<b>The quick</b> brown fox'  ->  Both codes are OK.
        ex5: '<b><i>jumped ov</b>er the lazy fox</i>.'
            -> Neither the '</b>' nor the '</i>' will be captured.
    """

    def __init__(
            self, size: tuple, typeface=None, font_size=12,
            bg_RGBA=(255, 255, 255, 255), font_RGBA=(0, 0, 0, 255),
            paragraph_indent=0, new_line_indent=0, spacing=4,
            margins=None):
        """
        :param size: 2-tuple of (width, height).
        :param typeface: The filepath to a truetype font (.ttf file) to
        use for the primary font.
        :param font_size: The size of the font to create.
        :param bg_RGBA: 4-tuple of the background color. (Defaults to
        white, full opacity.)
        :param font_RGBA: 4-tuple of the font color. (Defaults to black,
        full opacity.)
        :param paragraph_indent: How many spaces (i.e. characters, not
        px) to write before the first line of a new paragraph.
        :param new_line_indent: How many spaces (i.e. characters, not
        px) to write before every subsequent line of a paragraph.
        :param spacing: How many px between each line.
        :param margins: Either `None` or a 4-tuple specifying how many
        px for each margin (left, upper, right, lower -- mirroring PIL's
        conventions.)  Defaults to `None`.
            IMPORTANT: If using margins, keep in mind that the `.im`
                attribute of a TextBox object refers to the writable
                area. To get an output Image that includes the margins,
                use the `.render()` method.
            NOTE ALSO: If margins are used, it will reduce the area that
                will be written in accordingly. `size` of the TextBox
                will not be increased to accommodate. If margins cannot
                fit, it will raise a ValueError at init.
        """

        self._bg_RGBA = bg_RGBA
        self._size = size
        self._margins = margins

        # The Image object of the writable area
        self.im = None
        # The ImageDraw object for the writable area
        self.text_draw = None
        # Create and set `self.im` and `self.text_draw` here:
        self._new_tb()

        # IMPORTANT: Set font with `.set_truetype_font()` method.
        self.font = ImageFont.load_default()
        # formatted fonts should have 'bold', 'ital', and 'boldital' if
        # formatting is going to be parsed.
        self.formatted_fonts = {
            'main': self.font
        }
        self.typeface = typeface
        self.font_size = font_size
        self.font_RGBA = font_RGBA
        if None not in [typeface, font_size]:
            self.set_truetype_font(font_size, typeface)

        # How many spaces (i.e. characters, not px) before the first
        # line of a new paragraph
        self.paragraph_indent = paragraph_indent
        # How many spaces (i.e. characters, not px) before each
        # subsequent line
        self.new_line_indent = new_line_indent

        # How many px between lines
        self.spacing = spacing

        # The main cursor (coord location where text can be written)
        self.text_cursor = (0, 0)

    @staticmethod
    def new_same_as(tb):
        """
        Generate and return a new (blank) TextBox object, using the same
        settings as another TextBox (passed as `tb`).
        :param tb: The TextBox whose attributes should be copied.
        """
        new_tb = TextBox(
            size=tb._size,
            typeface=tb.typeface,
            font_size=tb.font_size,
            bg_RGBA=tb._bg_RGBA,
            font_RGBA=tb.font_RGBA,
            paragraph_indent=tb.paragraph_indent,
            new_line_indent=tb.new_line_indent,
            spacing=tb.spacing,
            margins=tb._margins)
        # Will copy the dict, but not the ImageFont objects it has stored
        new_tb.formatted_fonts = tb.formatted_fonts.copy()
        return new_tb

    def _new_tb(self):
        """
        INTERNAL USE:

        Create a new image for the text area. If margins were specified
        at init, adjust the size of the writable area appropriately.
        Store the Image and the ImageDraw objects to `.im` and
        `.text_draw` attributes, respectively.
        """
        tb_wid, im_height = self._size
        margins = self._margins
        if margins is not None:
            left_right_marg = margins[0] + margins[2]
            upper_lower_marg = margins[1] + margins[3]
            tb_wid -= left_right_marg
            im_height -= upper_lower_marg
            if tb_wid <= 0 or im_height <= 0:
                raise ValueError(
                    'Specified margins are larger than the size of the TextBox')

        self.im = Image.new('RGBA', (tb_wid, im_height), color=self._bg_RGBA)
        self.text_draw = ImageDraw.Draw(self.im, 'RGBA')

    def render(self) -> Image:
        """
        Get a unique PIL.Image.Image object of the textbox. Margins will
        be included if they were set at init. (Leaves `self.im` in place
        by creating a copy, so the returned Image object can be
        manipulated without modifying the original.)

        :return: A copy of the PIL.Image.Image object containing the
        written text, and containing the margins (if any).
        """
        if self._margins is None:
            return self.im.copy()
        left, upper, _, _ = self._margins
        margin_im = Image.new('RGBA', self._size, color=self._bg_RGBA)
        margin_im.paste(self.im, (left, upper))
        return margin_im

    ################################
    # Properties (and property-like methods) / Configuring the TextBox
    ################################

    @property
    def text_line_height(self):
        """
        The height (in px) needed to write a line of text (not including
        space between lines), using the currently set main font.
        """
        return self.text_draw.textsize('XT', font=self.font)[1]

    def lines_left(self, cursor='text_cursor') -> int:
        """
        Calculate how many lines can still be written between the coord
        of the specified cursor and the bottom of the textbox, using the
        currently set main font and line spacing.

        :return: An integer of how many lines can still be written.
        """
        # Get coord, but fall back to the default `.text_cursor` if needed
        _, y_current = getattr(self, cursor, self.text_cursor)
        y_max = self.im.height
        y_remain = y_max - y_current

        # Store line_height so it doesn't have to be realculated.
        line_height = self.text_line_height

        # Subtract the height of our bottom line from the available px
        y_remain -= line_height
        if y_remain < 0:
            # No room even to fit even a single line_height
            return 0

        # All other lines require an additional line space.
        return 1 + (y_remain // (line_height + self.spacing))

    def on_last_line(self, cursor='text_cursor') -> bool:
        """
        Whether we're on the last line, at the specified cursor
        (defaults to 'text_cursor'), using the currently set font.
        """

        return self.lines_left(cursor) == 1

    def is_exhausted(self, cursor='text_cursor') -> bool:
        """
        Whether there's room to write at least one more line with the
        currently set font, at the specified cursor (defaults to
        'text_cursor').
        """
        return self.lines_left(cursor) == 0

    def at_new_line(self, cursor='text_cursor') -> bool:
        """
        Check whether the cursor is at the start of a new line.

        :param cursor: The name of the cursor to check. (Defaults to
        'text_cursor'.)
        :return: A bool.
        """
        x, y = getattr(self, cursor, self.text_cursor)
        return x == 0

    def set_truetype_font(
            self, size=None, typeface=None, RGBA=None, style='main'):
        """
        Modify the size, typeface, and/or RGBA of the font. (Any
        unspecified parameters will leave the current attributes alone.)

        :param size: An int specifying the size of the font.
        :param typeface: Filepath to the .ttf font file to use.
        NOTE: Must be a filepath to a truetype font! If a valid filepath
        to a truetype font has not been specified (either during this
        call, or previously), then neither `typeface` nor `size` will
        have any effect, and the PIL default font will be (re)loaded.
        However, if a truetype font was previously provided, then it
        need not be provided again.
        :param RGBA: A 4-tuple of the color for the font.
        :param style: Specify what style this typeface is for (must be
        'main', 'bold', 'ital', or 'boldital'). Defaults to 'main'.
        NOTE: Setting 'main' will ALSO set `self.font`, which is used
        for writing any non-formatted text.
        :return: None
        """

        # Check for errors in the specified `RGBA`, and then set it.
        if RGBA is not None:
            if not isinstance(RGBA, tuple):
                raise TypeError(
                    '`RGBA` must be tuple containing 4 ints from 0 to 255. '
                    f"(Argument of type \'{type(RGBA)}\' was passed)")
            elif len(RGBA) != 4:
                raise ValueError(
                    f"`RGBA` must be tuple containing 4 ints from 0 to 255. "
                    f"(Passed tuple contained {len(RGBA)} elements.")
            for val in RGBA:
                if not isinstance(val, int):
                    raise TypeError(
                        '`RGBA` must be tuple containing 4 ints from 0 to 255. '
                        f"(Passed tuple contained element of "
                        f"type \'{type(val)}\'")
                if val < 0 or val > 255:
                    raise ValueError(
                        '`RGBA` must contain ints from 0 to 255. '
                        f"(The passed tuple contained int {val})")
            # If it passes the checks, set it.
            self.font_RGBA = RGBA

        # If `typeface` and `size` are BOTH None, then the ImageFont
        # object won't change. So if we don't need to create a new
        # ImageFont obj, we can return now. (RGBA does not get encoded
        # in an ImageFont obj)
        if typeface is None and size is None:
            return

        if typeface is None:
            typeface = self.typeface
        if typeface is None:
            # If still None, load the default PIL font.
            self.font = ImageFont.load_default()
            return

        if size is None:
            size = self.font_size

        fs = ('main', 'bold', 'ital', 'boldital')
        if style not in fs:
            raise ValueError(
                "`formatting` must be 'main', 'bold', 'ital', or 'boldital'")

        self.formatted_fonts[style] = ImageFont.truetype(typeface, size)

        if style == 'main':
            self.font = ImageFont.truetype(typeface, size)

            # We only want to change the respective typeface attribute AFTER
            # creating an ImageFont object, so that that has now had the
            # chance to raise any appropriate errors.
            self.font_size = size
            self.typeface = typeface

    ################################
    # Writing Text
    ################################

    def write_paragraph(
            self, text, cursor='text_cursor', font_RGBA=None,
            reserve_last_line=False, override_legal_check=False,
            paragraph_indent=None, new_line_indent=None, justify=False,
            formatting=False, discard_formatting=False):
        """
        Write the text as though it is a paragraph, with linebreaks
        inserted where necessary. Any lines that could not be fit within
        this textbox will be returned as a list of lines. (Optionally
        use the `.continue_paragraph()` method to write the returned
        UnwrittenLines object (if any) into a new TextBox object,
        configured with identical font(s) and width.)

        :param text: Text to be written (a string), or an UnwrittenLines
        object (i.e. the object type that gets returned from this method
        if one or more lines could not be written).
        IMPORTANT: If an UnwrittenLines object is passed as `text`, the
        lines will NOT be re-wrapped, and it is assumed that this
        TextBox object is identical in configuration to the TextBox
        object that returned the lines as unwritten.
        :param cursor: Which cursor to begin writing at. (Defaults to
        'text_cursor')
        :param font_RGBA: A 4-tuple specifying the font color. (If not
        specified, will fall back to whatever is in this object's
        `.font_RGBA` attrib.)
        :param reserve_last_line: If it is reached, leave the last line
        in the textbox empty (and return an UnwrittenLines object
        containing any lines that were not written). (Defaults to
        `False`)
        :param override_legal_check: Disregard whether the written text
        would go beyond the bottom boundaries of this TextBox. (Defaults
        to `False`)
        :param paragraph_indent: An int for how many leading spaces
        (i.e. characters, not px) before the first line. (If not
        specified, defaults to `self.paragraph_indent`.)
        :param new_line_indent: An int for how many leading spaces (i.e.
        characters, not px) before each subsequent line. (If not
        specified, defaults to `self.new_line_indent`.)
        :param justify: A bool, whether the written text should be
        block-justified -- i.e. stretched between the left indent and
        the right edge of the textbox. If used, all lines in the
        paragraph will be justified, except the final line, and any line
        that originally ended with a linebreak or return character.
        (Defaults to `False`)
        :param formatting: A bool, whether to parse format codes (e.g.,
        '<b>' or '</b>' in the input text string.
        :param discard_formatting: A bool, whether to discard all
        formatting and only write plain text. (Will have no effect
        unless parameter `formatting=` is True AND `text` was passed as
        a string.)
        :return: Returns as follows:
        -- All lines successfully written -> returns None
        -- At least one line was not written -> returns an
            UnwrittenLines object containing the lines that could NOT be
            written.
        """

        # If any of these parameters were not spec'd, pull from attribs
        if font_RGBA is None:
            font_RGBA = self.font_RGBA

        if paragraph_indent is None:
            paragraph_indent = self.paragraph_indent

        if new_line_indent is None:
            new_line_indent = self.new_line_indent

        # Check if text has already been broken into lines (e.g., if this
        # was called from `.continue_paragraph()` method.)
        if not isinstance(text, UnwrittenLines):
            # Break text into lines (i.e. an UnwrittenLines object)
            text = self._wrap_text(
                text, paragraph_indent=paragraph_indent,
                new_line_indent=new_line_indent, formatting=formatting,
                discard_formatting=discard_formatting)

        # Renaming this variable for clearer purpose from this point on.
        unwritten = text

        # Write each line (until we can't anymore)
        while unwritten.remaining > 0:
            if reserve_last_line and self.on_last_line(cursor=cursor):
                return unwritten
            line = unwritten._stage_next_line()

            # Write the line. Store the returned value, to see if everything
            # got written.
            unwrit_line = self.write_line(
                line, cursor=cursor, font_RGBA=font_RGBA, indent=None,
                reserve_last_line=reserve_last_line,
                override_legal_check=override_legal_check, justify=justify)

            if unwrit_line is not None:
                # Something couldn't be written. Put the last line back
                # in and return what's left.
                unwritten._unstage()
                return unwritten

            # Successfully wrote that line, so remove it from unwritten.
            unwritten._successful_write()

        if unwritten.remaining == 0:
            return None

        return unwritten

    def continue_paragraph(
            self, continue_lines: UnwrittenLines, cursor='text_cursor',
            font_RGBA=None, reserve_last_line=False, override_legal_check=False,
            justify=False):
        """Continue writing the unwritten lines previously returned by
        `.write_paragraph()`.

        NOTE: Text will not be re-wrapped. This method assumes that the
        TextBox being written in is configured identically to the one
        from which the unwritten lines were returned.

        NOTE ALSO: The UnwrittenLines object gets modified in-situ --
        line objects in the `.lines` attribute get popped with `.pop()`.

        All other applicable parameters have the same effect as in
        `.write_paragraph()`.
        :param continue_lines: An UnwrittenLines object be written.
        :param cursor: Same as in `.write_paragraph().
        :param font_RGBA: Same as in `.write_paragraph().
        :param reserve_last_line: Same as in `.write_paragraph().
        :param override_legal_check: Same as in `.write_paragraph().
        :param justify: Same as in `.write_paragraph().
        :return: Returns as follows:
        -- All lines successfully written -> returns None
        -- At least one line was not written -> returns the same
            UnwrittenLines object, with its `.lines` attribute culled to
            only the remaining lines.
        """
        unwrit_lines = self.write_paragraph(
            text=continue_lines, cursor=cursor, font_RGBA=font_RGBA,
            reserve_last_line=reserve_last_line,
            override_legal_check=override_legal_check, justify=justify)
        return unwrit_lines

    def write_line(
            self, text, cursor='text_cursor', font_RGBA=None,
            reserve_last_line=False, override_legal_check=False,
            indent=None, justify=False, formatting=False,
            discard_formatting=False):
        """
        Write a line of text at the specified cursor, after first
        confirming that the line can fit within the textbox. (May
        optionally partially override the legality check.) Any line that
        could not be fit within this textbox will be returned as a list
        of containing that line (in the same format as it was passed in).

        `text` can be passed as a string, as a PLine object (i.e. a line
        of plain text, as generated by this module), or as a FLine
        object (a line of formatted text, also generated by this
        module).

        BLOCK-JUSTIFICATION:
        If a string is passed as `text`, then parameter `justify=True`
        will justify the line. However, if a PLine or FLine object is
        passed as `text`, then BOTH `justify=` parameter must be True,
        AND that obj's `.justifiable` attribute must be True -- or the
        line will NOT be justified.
            ex:
                # Will justify the line (passed a str-type):
                line_1 = 'Testing Ex 1'
                tb_obj.write_line(line_1, justify=True)

                # Will NOT justify the line (passed a str-type):
                line_2 = 'Testing Ex 2'
                tb_obj.write_line(line_2, justify=False)

                # Will justify the line (passed as a PLine object):
                line_3 = PLine(txt='Testing Ex 3', justifiable=True)
                tb_obj.write_line(line_3, justify=True)

                # Will NOT justify the line (passed as a PLine object):
                line_4 = PLine(txt='Testing Ex 4', justifiable=False)
                tb_obj.write_line(line_4, justify=True)

                # Will NOT justify the line (passed as a PLine object):
                line_5 = PLine(txt='Testing Ex 5', justifiable=True)
                tb_obj.write_line(line_5, justify=False)

                # (FLine objects have the same requirements for block-
                # justification as PLine objects.)

        :param text: The text to write (a string), or a PLine or FLine
        object.
        :param cursor: Which cursor to begin writing at. (Defaults to
        'text_cursor')
        :param font_RGBA: A 4-tuple specifying the font color. (If not
        specified, will fall back to whatever is in this object's
        `.font_RGBA` attrib.)
        :param reserve_last_line: If it is reached, leave the last line
        in the textbox empty (and return a FLine or PLine object,
        representing the unwritten line). (Defaults to `False`)
        :param override_legal_check: Disregard whether the written text
        would go beyond the boundaries of this TextBox. (Defaults to
        `False`)
        NOTE: `override_legal_check=True` will still NOT allow justified
        text that is too wide for the line (unjustified text is OK).
        :param indent: An int specifying how many leading spaces (i.e.
        characters, not px) to write before the `text`. (Defaults to
        None)
        :param justify: A bool, whether the written text should be
        block-justified -- i.e. stretched between the left indent and
        the right edge of the textbox.
        :param formatting: A bool, whether to parse format codes (e.g.,
        '<b>' or '</b>' in the input text.
        NOTE: Parameter `formatting` only applies when `text` is passed
        as a string (i.e. it is ignored for PLine or FLine object).
        :param discard_formatting: A bool, whether to discard all
        formatting and only write plain text. (Will have no effect
        unless parameter `formatting=` is True AND `text` was passed as
        a string.)

        :return: Returns as follows:
        -- Line successfully written -> returns None
        -- Line unsuccessfully written, and param `formatting` was False
            -> returns a PLine object, being the unwritten line, stored
            as a PLine object.
        -- Line unsuccessfully written, and param `formatting` was True
            -> returns a FLine object, being the unwritten line, stored
                as a FLine object (with encoded formatting).
        NOTE: If a line was not successfully written, and `text` was
        originally passed as a FLine or PLine object, then that original
        object will be returned -- i.e. it will not convert a FLine to
        PLine or vice versa.
        """

        bad_text_error = TypeError('`text` must be type: str, FLine, or PLine')

        # Check whether `text` is a plain string; convert to PLine or
        # FLine, as needed
        if isinstance(text, str):
            justifiable = True
            text = parse_into_line(
                text, formatting, justifiable, discard_formatting)
        elif isinstance(text, PLine):
            justifiable = text.justifiable
            formatting = False
        elif isinstance(text, FLine):
            justifiable = text.justifiable
            formatting = True
        else:
            raise bad_text_error

        if not self.at_new_line(cursor):
            self.next_line_cursor(cursor)

        if reserve_last_line and self.on_last_line(cursor=cursor):
            return text

        if font_RGBA is None:
            font_RGBA = self.font_RGBA

        if formatting:
            return self._write_fline(
                text, cursor, font_RGBA, override_legal_check, indent,
                justify=(justify and justifiable))
        elif justify and justifiable and not formatting:
            # We need to justify, but `text` is currently a PLine.
            # Block-justified text is accomplished by the FLine-writer,
            # so pull the plain text indent out, and convert to FLine.

            copy_pline = PLine(txt=text.txt, justifiable=text.justifiable)

            # Check how many leading spaces
            orig_len = len(copy_pline.txt)
            copy_pline.txt = copy_pline.txt.lstrip(' ')
            deduced_indent = orig_len - len(copy_pline.txt)
            conv_line = copy_pline.to_fline()

            # Also add the `indent=` parameter, if any.
            if indent is not None:
                deduced_indent += indent

            success_check = self._write_fline(
                conv_line, cursor, font_RGBA, override_legal_check,
                indent=deduced_indent, justify=justify)

            if success_check is not None:
                # If it could not be written, we want to return the
                # PLine (not the converted FLine)
                return text
        else:
            return self._write_pline(
                text, cursor, self.font, font_RGBA, override_legal_check,
                indent)

    def _write_pline(
            self, pline_obj: PLine, cursor, font, font_RGBA,
            override_legal_check=False, indent=None):
        """
        INTERNAL USE:
        Write the contents of a PLine object (a line of plain text).
        May not justify the text.

        :param pline_obj: A PLine object for the text to be written.
        :param cursor: The cursor at which to begin writing.
        :param font: Which font to use.
        :param font_RGBA: The 4-tuple color code for this text.
        :param override_legal_check: Disregard whether the written text
        would go beyond the boundaries of this TextBox. (Defaults to
        `False`)
        :param indent: An integer, being the number of space characters
        to use for the indentation of this line.
        :return: If the line was successfully written, returns None.
        If the line was NOT written, returns the original PLine object.
        """

        # Convert `integer` from number of spaces (int) into a string of spaces
        if indent is not None:
            indent = ' ' * indent
        staged_line = pline_obj._stage(indent=indent)

        # Try to get the specified cursor, but fall back to
        # `.text_cursor`, if it doesn't exist
        coord = getattr(self, cursor, self.text_cursor)
        legal = self._check_legal_textwrite(staged_line, font, cursor)
        if legal or override_legal_check:
            # Write the text and get the width and height of the text written.
            xy_delta = self._write_text(coord, staged_line, font, font_RGBA)
        else:
            pline_obj._unstage()
            return pline_obj

        self.next_line_cursor(cursor=cursor, commit=True)

        return None

    def _write_fline(
            self, fline_obj: FLine, cursor, font_RGBA,
            override_legal_check=False, indent=None, justify=False,
            fword_info=None):
        """
        INTERNAL USE:
        Write the contents of a FLine object (a line of formatted text).
        May justify the text.

        :param fline_obj: A FLine object for the text to be written.
        :param cursor: The cursor at which to begin writing.
        :param font_RGBA: The 4-tuple color code for this text.
        :param override_legal_check: Disregard whether the written text
        would go beyond the boundaries of this TextBox. (Defaults to
        `False`)
        NOTE: `override_legal_check=True` will still NOT allow justified
        text that is too wide for the line (unjustified text is OK).
        :param indent: An integer, being the number of space characters
        to use for the indentation of this line.
        :param justify: Whether this line should be block-justified.
        :param fword_info: A dict generated by `FWord._examine_fwords()`
        specifying size, etc. from a list of FWord objects. (Probably
        only for internal use, when calling this method after text has
        been wrapped, wherein this information has already been
        calculated -- e.g., when this method is called from
        `.write_paragraph()`.)
        :return: If the line was successfully written, returns None.
        If the line was NOT written, returns the original FLine object.
        """

        def update_coord(coord, xy_delta, new_xy_delta) -> tuple:
            """
            Update the coord and xy_delta, per new_xy_delta.
            """

            x0, y0 = coord
            x_delta, y_delta = xy_delta
            new_x_delta, new_y_delta = new_xy_delta

            coord = (x0 + new_x_delta, y0)

            x_delta += new_x_delta
            if new_y_delta > y_delta:
                y_delta = new_y_delta

            xy_delta = (x_delta, y_delta)

            return coord, xy_delta

        # Convert `integer` from number of spaces (int) into a string of spaces
        if indent is not None:
            indent = ' ' * indent

        fwords = fline_obj._stage(indent=indent)

        if fword_info is None:
            fword_info = FWord._examine_fwords(
                fwords, fonts=self.formatted_fonts)
        line_info = fline_obj._extract_fword_info(fword_info, use_staged=True)

        # Deduce px available for all spaces in this line.
        px_all_spaces = self.im.width - line_info['line_word_w']

        # Space (in px) per word boundary
        spwd = line_info['space_w']
        bonus_sp_px = 0
        if line_info['total_spaces'] > 0:
            spwd = px_all_spaces // line_info['total_spaces']
            bonus_sp_px = px_all_spaces % line_info['total_spaces']

        # De-facto width legal check (cannot be overridden for justified line)
        illegal_width = False
        if (px_all_spaces < 0 or spwd < line_info['space_w']):
            # Not enough room to write this text on this line; or the
            # calculated space per word is narrower than a typed space char
            illegal_width = True
        if illegal_width and (justify or not override_legal_check):
            fline_obj._unstage()
            return fline_obj

        # Handle legality check for height.
        is_legal = True
        if not override_legal_check:
            is_legal = self._check_legal_cursor(
                (0, line_info['line_word_h']), cursor=cursor)
        if not is_legal:
            fline_obj._unstage()
            return fline_obj

        # Write the indent (i.e. just move the cursor to the right).
        coord = getattr(self, cursor, self.text_cursor)
        xy_delta = (0, 0)

        fwords_left = len(fwords)
        for fword in fwords:
            # Write the word
            self.text_draw.text(
                coord, fword.txt, font=fword_info['font_dict'][fword],
                fill=font_RGBA)

            # We already calculated each word's width, height, so pull
            # that, and update the cursor
            new_xy_delta = fword_info['word_px_dict'][fword]
            coord, xy_delta = update_coord(coord, xy_delta, new_xy_delta)

            # Unless it's the last word (or no space should be written after
            # this fword -- e.g., an indent), then write a space (i.e. move
            # the cursor right the appropriate px).
            if fwords_left > 1 and fword.xspace:
                # Default space distance to justified text...
                space = spwd
                if bonus_sp_px > 0:
                    # Spend each extra space px, one at a time.
                    space += 1
                    bonus_sp_px -= 1
                # ... but reset to a single space character, if not justifying.
                if not justify:
                    space = fword_info['space_w']
                coord, xy_delta = update_coord(coord, xy_delta, (space, 0))

            fwords_left -= 1

        self.next_line_cursor(cursor=cursor, commit=True)
        return None

    def write(
            self, text, cursor='text_cursor', font_RGBA=None,
            reserve_last_line=False, formatting=False,
            discard_formatting=False, paragraph_indent=None,
            new_line_indent=None):
        """
        Write the `text` word-by-word, for as many words as can fit. Can
        NOT use this method for justified text (for that, use
        `.write_line()` or `.write_paragraph()` methods).

        NOTE: Will break to new lines as necessary, but will NOT update
        the cursor to a new line after writing. To do that, call
        `.next_line_cursor()` afterwards. If it runs out of space, then
        the unwritten words will be returned as a list of FWord objects.

        :param text: A string of text to write, or a list of FWord
        objects (such as what gets returned by this method if not all
        could fit in the TextBox).
        :param cursor: Which cursor to begin writing at. (Defaults to
        'text_cursor')
        :param font_RGBA: A 4-tuple specifying the font color. (If not
        specified, will fall back on whatever is in this object's
        `.font_RGBA` attrib.)
        :param reserve_last_line: If it is reached, leave the last line
        in the textbox empty (and return a list of any unwritten FWord
        objects). (Defaults to `False`)
        :param paragraph_indent: An int for how many leading spaces
        (i.e. characters, not px) before the first line. (If not
        specified, defaults to `self.paragraph_indent`.)
        :param new_line_indent: An int for how many leading spaces (i.e.
        characters, not px) before each subsequent line. (If not
        specified, defaults to `self.new_line_indent`.)
        NOTE: If the cursor is not currently at the start of a new line
        OR if `text` is passed as a list of FWord objects, then this
        method will assume that all resulting lines should be indented
        pursuant to `new_line_indent`, and not `paragraph_indent`.
        :param formatting: A bool, whether to parse format codes (e.g.,
        '<b>' or '</b>' in the input text.
        :param discard_formatting: A bool, whether to discard all
        formatting and only write plain text. (Will have no effect
        unless parameter `formatting=` is True AND `text` was passed as
        a string.)
        :return: Returns a list of FWord objects, i.e. the words that
        could NOT be written. (Such a list can then be passed as `text`
        in another call of `.write()` on another TextBox object, or
        recompiled into a plain string with the static method
        `TextBox.simplify_unwritten()`.)
        """

        if paragraph_indent is None:
            paragraph_indent = self.paragraph_indent

        if new_line_indent is None:
            new_line_indent = self.new_line_indent

        def insert_new_indent(fwords_list, indent_chars):
            if indent_chars in [None, 0]:
                return
            ind_fw = FWord(
                ' ' * indent_chars, bold=False, ital=False, xspace=False,
                is_indent=True)
            fwords_list.insert(0, ind_fw)
            return

        next_indent = paragraph_indent
        if isinstance(text, str):
            fwords = all_parse(text, formatting, discard_formatting)
        elif isinstance(text, list):
            fwords = text
            next_indent = new_line_indent
        else:
            raise TypeError(
                '`text` must be passed as a string, or as a list of FWord '
                'objects')

        if reserve_last_line and self.on_last_line(cursor=cursor):
            return fwords

        if font_RGBA is None:
            font_RGBA = self.font_RGBA

        coord = getattr(self, cursor, 'text_cursor')

        if self.at_new_line(cursor=cursor):
            # Insert the initial indent (if any) at the start of the list.
            insert_new_indent(fwords, next_indent)

        next_indent = new_line_indent

        last_inserted_indent = False
        consecutive_unsuccessful = 0
        while len(fwords) > 0:
            fword = fwords.pop(0)
            style = f"{'bold' * fword.bold}{'ital' * fword.ital}"
            if style == '':
                style = 'main'
            font = self.formatted_fonts.get(style, self.font)

            legal = self._check_legal_textwrite(fword.txt, font, cursor)
            if legal:
                xy_delta = self._write_text(
                    coord, fword.txt, font=font, font_RGBA=font_RGBA)
                coord = self.same_line_cursor(
                    xy_delta, cursor=cursor, add_space=fword.xspace,
                    space_font=font)
                consecutive_unsuccessful = 0
                last_inserted_indent = False
            else:
                coord = self.next_line_cursor(cursor=cursor)
                fwords.insert(0, fword)
                consecutive_unsuccessful += 1

            if consecutive_unsuccessful > 1 \
                    or (reserve_last_line and self.on_last_line(cursor=cursor)):
                # If we've gone two consecutive passes without a legal
                # writing; or if we're on the last line and want to reserve it
                # we return the remaining list of FWord objs.
                if last_inserted_indent:
                    # If we've most recently added an indent, get rid of it.
                    fwords.pop(0)
                return fwords

            if self.at_new_line(cursor=cursor) and not last_inserted_indent:
                insert_new_indent(fwords, next_indent)
                last_inserted_indent = True

        # Unnecessary to state, but to be clear: If we successfully write every
        # word in the text, we return None.
        return None

    @staticmethod
    def simplify_unwritten(unwritten, exclude_indent=False):
        """
        For any text that was returned unwritten by any of the TextBox
        writing methods, this will 'unpack' it into a block of plain
        text. (It will destroy any data regarding formatting, block-
        justification, or if they originally ended in a linebreak or
        return character.)

        :param unwritten: Any object returned by any of the TextBox
        writing methods -- i.e. FLine, PLine, UnwrittenLines objects, or
        a list of FWord objects.
        :param exclude_indent: Whether to discard indents, if any.
        Defaults to `False`.
        :return: A single string.
        """
        if isinstance(unwritten, UnwrittenLines):
            lst = unwritten.simplify(exclude_indent=exclude_indent)
            return '\n'.join(lst)
        elif isinstance(unwritten, (PLine, FLine)):
            return unwritten.simplify(exclude_indent=exclude_indent)
        elif not isinstance(unwritten, list):
            raise TypeError(
                "`unwritten` must be of type FLine, PLine, UnwrittenLines; or "
                " a list of FWord objects"
            )

        return FWord.recompile_fwords(unwritten, exclude_indent=exclude_indent)

    def _write_text(self, coord: tuple, text: str, font, font_RGBA) -> tuple:
        """
        INTERNAL USE:
        Write `text` at the specified `coord`. Returns a 2-tuple of the
        width and height of the written text. Does NOT update a cursor.
        NOTE: This method does not care whether it goes outside the
            textbox, so be sure to handle `._check_legal_textwrite()`
            before calling this method.

        (End users should use `.write_line()` and `.write_paragraph()`,
        which have built-in legality checks that will prevent writing
        beyond textbox boundaries.)

        :param coord: Where to write the text.
        :param text: What text to write.
        :param font: PIL.ImageFont object that should be used.
        :param font_RGBA: A 4-tuple specifying the font color. (If not
        specified, will fall back on whatever is in this object's
        `.font_RGBA` attrib.)
        :return: Returns a 2-tuple of the (width, height) of the text
        written.
        """

        w, h = self.text_draw.textsize(text, font=font)
        self.text_draw.text(coord, text, font=font, fill=font_RGBA)
        return (w, h)

    ################################
    # Manipulating / Checking Text Before Writing
    ################################

    def _check_legal_textwrite(self, text, font, cursor='text_cursor') -> bool:
        """
        INTERNAL USE:
        Check if there is enough room to write the specified text at the
        specified cursor (defaulting to 'text_cursor'), using the
        specified font.

        :param text: The text to check.
        :param font: The font that will be used to write the text.
        :type font: PIL.ImageFont
        :param cursor: The name of the cursor at which the text will be
        written. (Defaults to 'text_cursor')
        :return: A bool, whether or not the text can be written within
        the bounds of the textbox.
        """

        w, h = self.text_draw.textsize(text, font=font)
        # Only `legal` matters for this method.
        legal = self._check_legal_cursor((w, h), cursor=cursor)
        return legal

    def _wrap_text(
            self, text, paragraph_indent: int, new_line_indent: int,
            formatting=False, discard_formatting=False):
        """
        INTERNAL USE:
        Break down the `text` into a list of lines that will fit within
        the width of the TextBox, using the current settings.
        Additionally, parse any format codes with parameter
        `formatting=True` (defaults to False) and optionally discard
        those format codes with parameter `discard_formatting=True`
        (also defaults to False).

        This method also encodes whether each line is 'justifiable',
        meaning whether it can be stretched from the left indent to the
        right edge of the textbox. (All lines will be justifiable,
        except the final line in the text, and except lines that
        originally ended in a linebreak or return character.)

        :param paragraph_indent: How many leading spaces (i.e.
        characters, not px) before the first line. (If not specified,
        defaults to `self.paragraph_indent`.)
        :param new_line_indent: How many leading spaces (i.e.
        characters, not px) before each subsequent line. (If not
        specified, defaults to `self.new_line_indent`.)
        :param formatting: A bool, whether or not to parse format codes
        in the input text. Defaults to False.
        :param discard_formatting: A bool, whether or not to flatten all
        formatting (if any) into the default styling. (Has no effect if
        `formatting==False`.) Defaults to False.
        :return: An UnwrittenLines object containing a list of PLine or
        FLine objects (depending on whether parameter `formatting=` was
        passed as False or True).
        """
        # TODO: Handle extra-long words (i.e. a single word can't fit
        #   on a single line by itself -- just break the word at
        #   whatever char that is, onto the next line).

        final_lines = UnwrittenLines(lines=None, formatting=formatting)
        max_w = self.im.width

        # In order to maintain linebreaks/returns, but also have desired
        # indents (and whether a line is justifiable), we need to
        # manually break our text by linebreak first, and only then run
        # the algorithm.

        # First split our text by returns and linebreaks.
        text = text.strip('\r\n')
        text = text.replace('\r', '\n')
        rough_lines = text.split('\n')

        first_indent = FWord(
            ' ' * paragraph_indent, bold=False, ital=False, xspace=False,
            is_indent=True)
        later_indent = FWord(
            ' ' * new_line_indent, bold=False, ital=False, xspace=False,
            is_indent=True)

        # Get an initial fword_info dict that we'll fill throughout (gets
        # filled with px-sizes of words, fonts, space width, etc.)
        fwi = FWord._examine_fwords(
            fwords=[first_indent, later_indent], fonts=self.formatted_fonts)
        space_w = fwi['space_w']

        # Construct lines word-by-word, until they are longer than can
        # be written within the width of the image. At that point,
        # approve the last safe line, and start a new line with the word
        # that put it over the edge.
        # For each line, also encode whether it is 'justifiable', i.e.
        # whether it can be stretched from the left indent to the right
        # edge of the textbox. (All lines will be justifiable, except
        # the final line in the text, and except lines that originally
        # ended in a linebreak or return character.)

        rl_count = 0
        last_bold = False
        last_ital = False
        for rough_line in rough_lines:

            justifiable = True
            indent = later_indent
            if rl_count == 0:
                indent = first_indent

            # Strip any pre-existing whitespace
            rough_line = rough_line.strip()

            if formatting:
                # We need to use the 'deep' parser in order to maintain
                # bold/ital data across rough-line boundaries.
                fwords, last_bold, last_ital = format_parse_deep(
                    rough_line, discard_formatting=discard_formatting,
                    start_bold=last_bold, start_ital=last_ital)
            else:
                fwords = all_parse(rough_line, formatting, discard_formatting)

            if len(fwords) == 0:
                # No words in this rough_line. Move on.
                continue

            # Examine the new FWord objects, and add their info to the dict.
            fwi = FWord._examine_fwords(fwords, self.formatted_fonts, fwi)

            # width in px of current line
            cur_w = 0

            current_line_to_add = []
            candidate_line_list = []
            last_word_is_candidate = False
            at_new_line = True
            while len(fwords) > 0:
                # width in px of candidate line
                cand_w = cur_w

                new_fword = indent
                if not at_new_line:
                    new_fword = fwords.pop(0)
                at_new_line = False
                candidate_line_list = current_line_to_add.copy()
                candidate_line_list.append(new_fword)

                w, h = fwi['word_px_dict'][new_fword]
                cand_w += w
                if cand_w > max_w:
                    # Create a new FLine.
                    nl = FLine(
                        fwords=current_line_to_add, justifiable=justifiable,
                        fword_info=fwi)
                    # If we don't want formatting, convert the FLine to PLine.
                    if not formatting:
                        nl = nl.to_pline()

                    # Append our new line, and start a new one
                    final_lines.lines.append(nl)
                    indent = later_indent
                    if not new_fword.is_indent:
                        # Do not reinsert indents into fwords list
                        fwords.insert(0, new_fword)
                    current_line_to_add = []
                    last_word_is_candidate = True
                    at_new_line = True

                    # Reset cur_w to 0, plus width of indent and first word
                    cur_w = 0
                    for fword in current_line_to_add:
                        cur_w += fwi['word_px_dict'][fword][0]
                else:
                    last_word_is_candidate = False
                    current_line_to_add = candidate_line_list
                    # We also add `space_w` (equivalent to an additional space
                    # char), but wait until after the legal check so that a
                    # space at the end of a line does not push it over max_w
                    # (i.e. )incorrectly render it illegal).
                    cur_w = cand_w
                    if new_fword.xspace:
                        cur_w += space_w

            if current_line_to_add == candidate_line_list \
                    or last_word_is_candidate:
                justifiable = False

                # Create a new FLine.
                nl = FLine(
                    fwords=current_line_to_add, justifiable=justifiable,
                    fword_info=fwi)
                # If we don't want formatting, convert the FLine to PLine.
                if not formatting:
                    nl = nl.to_pline()
                # Append our new line
                final_lines.lines.append(nl)

            rl_count += 1

        # Store our fword_info dict to `final_lines`
        final_lines.fword_info = fwi

        # Return our UnwrittenLines object.
        return final_lines

    ################################
    # Cursor Methods
    ################################
    # Note regarding cursors: The coords stored as cursors are in
    # reference to the writable area, and do not account for margins.
    # That is, (0, 0) would point to the upper-left corner of the
    # writable area (`self.im`), even if that would not be (0, 0) of the
    # Image object that is eventually output by `.render()`.

    def reset_cursor(self, cursor='text_cursor') -> tuple:
        """
        Set the specified cursor (defaults to 'text_cursor') to (0, 0).

        :param cursor: The name of the cursor to be set to (0, 0).
        The named cursor will be stored as an attribute in `self`.
        Specifically, if a string is NOT passed as `cursor=`, the
        stored coord will be set to the default `.text_cursor`. However,
        if the particular cursor IS specified, it will save the
        resulting coord to that attribute name.
        Be careful not to overwrite other required attributes.
        :return: (0, 0)
        :Example:

        ex: 'tb_obj.reset_cursor()  # The default
            -> tb_obj.text_cursor == (0, 0)
            -> and returns (0, 0)
        ex: 'tb_obj.reset_cursor(cursor='highlight')
            -> tb_obj.highlight == (0, 0)
            -> and returns (0, 0)
        """
        self.set_cursor((0, 0), cursor)
        return (0, 0)

    def set_cursor(self, coord, cursor='text_cursor'):
        """
        Set the cursor to the specified x and y coord. If a string
        is NOT passed as `cursor=`, the committed coord will be set to
        the default `.text_cursor`. However, if the particular cursor
        IS specified, it will save the resulting coord to that attribute
        name.
            ex: 'tb_obj.set_cursor((200, 1200))
                -> tb_obj.text_cursor == (200, 1200)
            ex: 'tb_obj.set_cursor((200, 1200), cursor='highlight')
                -> tb_obj.highlight == (200, 1200)
        Be careful not to overwrite other required attributes.
        """
        setattr(self, cursor, coord)

    def same_line_cursor(
            self, xy_delta, cursor='text_cursor', commit=True,
            add_space=True, space_font=None,
            prevent_linebreak=False) -> tuple:
        """
        Move the specified `cursor` right on the same line, after having
        written some text at that cursor (the size of which is passed as
        `xy_delta`). If the cursor has moved up to or past the right
        edge of the textbox, will instead move the cursor to the next
        line (unless parameter `prevent_linebreak=True`, which is off by
        default).

        IMPORTANT: Does not check legality of resulting cursor position!

        :param xy_delta: 2-tuple of how many px have been written --
        although the y-value gets ignored.
        :param cursor: The name of the cursor being moved. (Defaults to
        'text_cursor'.)

        If the cursor is specified but does not yet exist, this will
        read from `.text_cursor` (to calculate the updated coord) but
        save to the specified cursor (if parameter `commit` is True).
        :param commit: Whether to save the coord to the cursor attrib.
        (Defaults to `True`)
        :param add_space: Whether to add another space at the end of
        the cursor, using the font specified in `space_font`.
        :param space_font: If writing an additional space (i.e.
        `add_space=True`), use the specified font. (Defaults to whatever
        is set at `self.font`.)
        :param prevent_linebreak: A bool, specifying whether to prevent
        a linebreak if we've found the end of the line. (Defaults to
        `False`)
        :return: The resulting coord.
        """
        x0, y0 = getattr(self, cursor, self.text_cursor)
        x_delta, _ = xy_delta
        space_px = 0
        if add_space:
            if space_font is None:
                space_font = self.font
            space_px, _ = self.text_draw.textsize(' ', space_font)
        x1 = x0 + x_delta + space_px
        if not prevent_linebreak and x1 >= self.im.width:
            return self.next_line_cursor(cursor=cursor, commit=commit)
        coord = (x1, y0)
        if commit:
            self.set_cursor(coord, cursor=cursor)
        return coord

    def next_line_cursor(self, cursor='text_cursor', commit=True) -> tuple:
        """
        Move the specified `cursor` to the so-called 'next line'.

        IMPORTANT: Does not check legality of resulting cursor position!

        :param cursor:
        If a string is NOT passed as `cursor=`, the returned (and
        optionally committed) coord will be set to the default
        `.text_cursor`. However, if the particular cursor IS specified,
        it will save the resulting coord to that attribute name (so long
        as `commit=True`).
        NOTE: If the cursor is specified but does not yet exist, this
        will read from `.text_cursor` (to calculate the updated coord)
        but save to the specified cursor.
        Be careful not to overwrite other required attributes!
        :param commit: A bool, whether to store the calculated coord to
        the specified cursor.
        :return: Returns the resulting coord.
        """

        # Set x to the left edge of the textbox
        x = 0

        # Discard the x0 from the cursor, but get y0.  (Fall back to
        # self.text_cursor, if `cursor=` was specified as a string that
        # wasn't already set)
        _, y0 = getattr(self, cursor, self.text_cursor)

        # We will add to our y-value the `.spacing` and the newly
        # calculated line height (using the currently set font).
        coord = (x, y0 + self.text_line_height + self.spacing)

        if commit:
            self.set_cursor(coord, cursor=cursor)

        return coord

    def update_cursor(
            self, xy_delta, cursor='text_cursor', commit=True) -> tuple:
        """
        Update the coord of the cursor, by adding the `x_delta` and
        `y_delta` to the current coord of the specified `cursor`.

        :param xy_delta: A tuple of (x, y) values, being how far (in px)
        the cursor has traveled from its currently set coord.
        :param cursor: The name of the cursor being updated. (Defaults
        to 'text_cursor'.)
        If a string is NOT passed as `cursor=`, the committed coord will
        be set to the default `.text_cursor`. However, if the particular
        cursor IS specified, it will save the resulting coord to that
        attribute name (so long as `commit=True`).

        Further, if the cursor is specified but does not yet exist, this
        will read from `.text_cursor` (to calculate the updated coord)
        but save to the specified cursor.
        Be careful not to overwrite other required attributes.
        :param commit: Whether to store the new coord to the cursor
        attribute in `self`.
        :return: Returns the updated coord, and optionally stores it to the
        cursor attribute with `commit=True` (on by default).
        """

        # Pull the specified cursor. If it does not already exist as an
        # attribute in this object, it will fall back to `.text_cursor`,
        # which exists for every TextBox object, per init.
        x_delta, y_delta = xy_delta
        x0, y0 = getattr(self, cursor, self.text_cursor)
        coord = (x0 + x_delta, y0 + y_delta)

        # Only if `commit=True` do we set this.
        if commit:
            setattr(self, cursor, coord)

        return coord

    ###############
    # Checking Cursor Movements
    ###############

    def _check_cursor_overshoot(
            self, xy_delta: tuple, cursor='text_cursor') -> tuple:
        """
        Check how many px the cursor has gone beyond right and bottom
        edges of the textbox. (Assumes that it is starting from a legal
        coord.)

        :param xy_delta: A tuple of (x, y) values, being how far (in px)
        the cursor has traveled from its currently set coord.
        :param cursor: The name of the cursor being checked. (Defaults
        to 'text_cursor'.)
        :return: Returns an (x, y) tuple of how many px past the margins
        the cursor has gone. (Negative numbers mean that it is within
        the right/bottom margins, but is agnostic as to the top/left
        margins.)
        """

        # Confirm `cursor` points to an existing tuple in self's
        # attributes. If not, we'll use the `.text_cursor` attribute.
        cursor_check = getattr(self, cursor, None)
        if not isinstance(cursor_check, tuple):
            cursor = 'text_cursor'

        # Get the hypothetical resulting cursor location if xy_delta is
        # applied. (`commit=False` means it won't be stored yet.)
        x, y = self.update_cursor(xy_delta, cursor, commit=False)

        x_overshot = x - self.im.width
        y_overshot = y - self.im.height

        return (x_overshot, y_overshot)

    def _check_legal_cursor(
            self, xy_delta: tuple, cursor='text_cursor') -> bool:
        """
        Check if there is enough room to move the cursor from its
        current position by `xy_delta` (a tuple of x,y value) before
        going outside the dimensions of the textbox.
        (Assumes that it is starting from a legal coord.)

        :param xy_delta: A tuple of (x, y) values, being how far (in px)
        the cursor has traveled from its currently set coord.
        :param cursor: The name of the cursor at which the text will be
        written. (Defaults to 'text_cursor')
        :return: A bool, whether or not the resulting coord will fall
        within the bounds of the textbox.
        """

        x_overshot, y_overshot = self._check_cursor_overshoot(xy_delta, cursor)
        if x_overshot > 0 or y_overshot > 0:
            return False
        return True
