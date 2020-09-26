# piltextbox

An extension for the Pillow (PIL) library for streamlined writing of text in an image, with automatic textwrapping and optional text-block justification.

### Quickstart

The quickstart code below will write these sample lines:
```
line_sample_1 = 'Lorem ipsum dolor sit amet, consectetur adipiscing'

line_sample_2 = 'elit, sed do eiusmod tempor incididunt ut'

paragraph_sample_1 = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'

paragraph_sample_2_long = """Quisque justo quam, auctor ac quam et, porta euismod urna. Ut faucibus lorem non scelerisque imperdiet. In hac habitasse platea dictumst. Mauris non elit orci. Nulla venenatis sit amet metus vitae fermentum. Aliquam erat volutpat. Maecenas sed libero blandit, tincidunt tellus quis, euismod diam. In iaculis est semper odio egestas, a porta augue fringilla. Nulla ut augue non arcu blandit mattis id vel nibh.
Proin neque leo, semper a tempor pharetra, posuere sed neque. Cras egestas non nunc ac pellentesque. Sed fermentum ligula ante, ac finibus ante pulvinar vitae. Donec nec libero sit amet leo convallis dapibus. Nulla a sapien ut arcu posuere tristique nec vitae mauris. Etiam varius odio ac lorem blandit, eu ultricies arcu interdum. Maecenas accumsan tempor dui, a posuere ligula convallis efficitur. Curabitur blandit, augue ac varius pretium, erat risus ultrices libero, ac dictum odio diam quis urna.
Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Curabitur eleifend dapibus lacus, non feugiat neque luctus ut. Suspendisse vulputate, metus ut varius lacinia, massa arcu mollis turpis, ut blandit dui augue sed justo. Praesent vel ante dolor. Proin lacus metus, lacinia et ultricies eu, interdum nec nibh. Duis ultricies et ipsum in mollis. Nulla augue massa, faucibus ut sem suscipit, congue sagittis dolor. Proin a pellentesque leo. Quisque leo justo, tempus ut nulla nec, tincidunt tincidunt neque. Aliquam sit amet scelerisque odio.
Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Duis varius in magna vel scelerisque. Nunc sollicitudin vitae augue et dapibus. Suspendisse dictum et velit quis molestie. Duis sem felis, euismod nec est id, lobortis ultricies sapien. Donec tincidunt est ac lorem dapibus tincidunt. Vestibulum rhoncus ac risus sit amet luctus. Nam euismod malesuada elit. Mauris tempor auctor nunc vel malesuada. Cras sit amet erat eu quam sollicitudin porttitor ut a enim. Quisque maximus placerat lacinia. In vitae sapien eget ipsum elementum vestibulum eget vitae neque. Nam vel libero nisl. Maecenas dapibus dolor a erat interdum vulputate."""
```

*Note: The examples below use one of the [Liberation](https://github.com/liberationfonts) fonts, which are not included in this package.*
```
import piltextbox

# Filepath to the .ttf font we want to use. (If no font is set, it will use
# PIL's default font.)
font_fp = r'samplefonts\LiberationSans-Regular.ttf'

# a new TextBox object, 400x600 px, using the .ttf font at the filepath,
# size 14 font, with 0 spaces indenting for paragraphs, and 8 spaces for
# every subsequent line. 4 px for vertical line spacing, and margins
# (left-top-right-bottom, specified in px).
tb1 = piltextbox.TextBox(
    (400, 600), typeface=font_fp, font_size=14, paragraph_indent=0,
    new_line_indent=8, spacing=4, margins=(10,20,10,10))

# Write a single line, unjustified. If it can't be fit on a single line,
# gets returned as a list of unwritten text.
unwritten = tb1.write_line(line_sample_1)

# Write a single line, justified.
unwritten = tb1.write_line(line_sample_2, justify=True)

# Write the paragraph of text, unjustified. Any lines that can't be
# written are returned as a list of dicts -- which can be passed to
# `.continue_paragraph()` method on another equally configured textbox
unwritten_lines = tb1.write_paragraph(paragraph_sample_1)

# Write the paragraph of text, justified. (Linebreaks are respected by
# the text wrap, and lines ending in linebreaks are not justified.)
unwritten_lines = tb1.write_paragraph(paragraph_sample_2_long, justify=True)

# Because the last text could not be fit within what remained of the
# textbox, we create a new TextBox object (configured identically) and
# continue writing.

tb2 = piltextbox.TextBox(
    (400, 600), typeface=font_fp, font_size=14, paragraph_indent=0,
    new_line_indent=8, spacing=4, margins=(10,20,10,10))

# Continue writing, to our new TextBox object, again returning any lines
# that can't fit. We have to re-specify whether we want to justify.
unwritten_lines = tb2.continue_paragraph(unwritten_lines, justify=True)

# Use the `.render()` method to output a flattened PIL.Image object with
# the margins. (Accessing `tb1.im` would give you the PIL.Image object
# of the writable area only.)
image1 = tb1.render()
image2 = tb2.render()

# -------------------------------------------------------
# Misc. methods for checking how much space is left:

# How many lines can still be written in the TextBox, using the current font:
tb1.lines_left()

# Whether we're on the last line of the TextBox, using the current font:
tb1.on_last_line()

# Whether the current TextBox is exhausted (i.e. out of room to write,
# using the current font):
tb1.is_exhausted()
```

**`image1` from the above example:**
![tb1](documentation/image1.png)

**`image2` from the above example:**
![tb2](documentation/image2.png)