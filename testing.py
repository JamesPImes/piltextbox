import piltextbox
from piltextbox.textbox.formatting import FWord, FLine, PLine, UnwrittenLines
from piltextbox.textbox.formatting import format_parse, flat_parse, parse_into_line

tb = piltextbox.TextBox((400, 1600), paragraph_indent=4, new_line_indent=12)

# These are not included in the `piltextbox` github repo, but can be acquired at
# <https://github.com/liberationfonts/liberation-fonts/releases/tag/2.1.1>
test_fonts = {
    'test_regular': r'testing_fonts\LiberationSans-Regular.ttf',
    'test_bold': r'testing_fonts\LiberationSans-Bold.ttf',
    'test_ital': r'testing_fonts\LiberationSans-Italic.ttf',
    'test_boldital': r'testing_fonts\LiberationSans-BoldItalic.ttf'
}

tb.set_truetype_font(typeface=test_fonts['test_regular'])
tb.set_truetype_font(typeface=test_fonts['test_bold'], style='bold')
tb.set_truetype_font(typeface=test_fonts['test_ital'], style='ital')
tb.set_truetype_font(typeface=test_fonts['test_boldital'], style='boldital')
#tb.set_truetype_font(typeface=test_fonts['default'], formatting='intentional_error')


# Some sample text from Wikipedia.
txt = 'The <b>Public Land <i>Survey System (PLSS)</b> is</i> the'

long_txt = '''The Public Land <b>Survey System (PLSS) is <i>the surveying method developed
and used </b>in the United States to plat, or</i> divide, real property for sale and settling. Also known as the Rectangular Survey System, it was created by the Land Ordinance of 1785 to survey land ceded to the United States by the Treaty of Paris in 1783, following the end of the American Revolution. Beginning with the Seven Ranges, in present-day Ohio, the PLSS has been used as the primary survey method in the United States. Following the passage of the Northwest Ordinance, in 1787, the Surveyor General of the Northwest Territory platted lands in the Northwest Territory. The Surveyor General was later merged with the General Land Office, which later became a part of the U.S. Bureau of Land Management (BLM). Today, the BLM controls the survey, sale, and settling of the new lands.'''


# write word-by-word
tb.write(long_txt)
tb.write(long_txt, formatting=True)
tb.write(long_txt, formatting=True, discard_formatting=True)
#tb.render().show()

# write individual lines
tb.write_line(txt)
tb.write_line(txt, formatting=True)
tb.write_line(txt, formatting=True, discard_formatting=True)
tb.write_line(txt, justify=True)
tb.write_line(txt, formatting=True, justify=True)
#tb.render().show()

# write paragraphs
unwrit = tb.write_paragraph(long_txt)
unwrit = tb.write_paragraph(long_txt, formatting=True)
unwrit = tb.write_paragraph(long_txt, formatting=True, discard_formatting=True)
unwrit = tb.write_paragraph(long_txt, justify=True)
unwrit = tb.write_paragraph(long_txt, formatting=True, justify=True)
# testing over-writing
unwrit = tb.write_paragraph(long_txt, formatting=True, justify=True)
unwrit = tb.write_paragraph(
    long_txt, formatting=True, justify=True, reserve_last_line=True)
tb.write_line('Last line was reserved.')

print(tb.simplify_unwritten(unwrit))

uw = tb.write("Testing one, two, three")
print(tb.simplify_unwritten(uw, exclude_indent=True))

uw = tb.write_line("Testing four, five")
print(tb.simplify_unwritten(uw, exclude_indent=True))

uw = tb.write_line("Testing six, seven", formatting=True)
print(tb.simplify_unwritten(uw, exclude_indent=True))

tb.render().show()


# continue writing

tb2 = piltextbox.TextBox.new_same_as(tb)

tb2.continue_paragraph(unwrit, justify=True)
tb2.write_paragraph(long_txt, formatting=True)

tb2.render().show()

