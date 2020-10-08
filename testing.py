

import piltextbox
from piltextbox.textbox.formatting import FWord, FLine, PLine, UnwrittenLines
from piltextbox.textbox.formatting import format_parse, flat_parse, parse_into_line

tb = piltextbox.TextBox((400,600))

# These are not included in the `piltextbox` github repo, but can be acquired at
# <https://github.com/liberationfonts/liberation-fonts/releases/tag/2.1.1>
test_fonts = {
    'default': r'testing_fonts\LiberationSans-Regular.ttf',
    'bold': r'testing_fonts\LiberationSans-Bold.ttf',
    'ital': r'testing_fonts\LiberationSans-Italic.ttf',
    'boldital': r'testing_fonts\LiberationSans-BoldItalic.ttf'
}
tb.set_truetype_font(typeface=test_fonts['default'])
tb.set_truetype_font(typeface=test_fonts['bold'], formatting='bold')
tb.set_truetype_font(typeface=test_fonts['ital'], formatting='ital')
tb.set_truetype_font(typeface=test_fonts['boldital'], formatting='boldital')
#tb.set_truetype_font(typeface=test_fonts['default'], formatting='intentional_error')

# # tb.write_paragraph('Hello, testing one two, three.\nAnd testing four, five.')
#
# import piltextbox.textbox.formatting.formatparser as parser
# # f_text = "Testing <b>one,</b> <i>two,</i> <b><i>three,</b></i> four."
# # fwords = parser.format_parse(f_text)
# # for fw in fwords:
# #     print(fw.txt)
# #     print(fw.bold)
# #     print(fw.ital)
# #     print('\n\n')
# # tb.write_formatted_words(f_text, paragraph_indent=8)
#
# long_txt = '''The Public Land Survey System (PLSS) is the surveying method developed and used in the United States to plat, or divide, real property for sale and settling. Also known as the Rectangular Survey System, it was created by the Land Ordinance of 1785 to survey land ceded to the United States by the Treaty of Paris in 1783, following the end of the American Revolution. Beginning with the Seven Ranges, in present-day Ohio, the PLSS has been used as the primary survey method in the United States. Following the passage of the Northwest Ordinance, in 1787, the Surveyor General of the Northwest Territory platted lands in the Northwest Territory. The Surveyor General was later merged with the General Land Office, which later became a part of the U.S. Bureau of Land Management (BLM). Today, the BLM controls the survey, sale, and settling of the new lands. '''
# #long_txt = '''The Public Land <b>Survey System (PLSS) is <i>the surveying method developed and used </b>in the United States to plat, or</i> divide, real property for sale and settling. Also known as the Rectangular Survey System, it was created by the Land Ordinance of 1785 to survey land ceded to the United States by the Treaty of Paris in 1783, following the end of the American Revolution. Beginning with the Seven Ranges, in present-day Ohio, the PLSS has been used as the primary survey method in the United States. Following the passage of the Northwest Ordinance, in 1787, the Surveyor General of the Northwest Territory platted lands in the Northwest Territory. The Surveyor General was later merged with the General Land Office, which later became a part of the U.S. Bureau of Land Management (BLM). Today, the BLM controls the survey, sale, and settling of the new lands. '''
# tb.next_line_cursor()
# tb.write_justified_line(
#     'Lorem <i>ipsum <b>dolor sit</b> amet, consectetur. Morbi mauris.</i>',
#     indent=14, formatting=True)
# # tb.write_justified_line(
# #     'Lorem <i>ipsum <b>dolor sit</b> amet, consectetur. Morbi mauris.</i>',
# #     indent=14, formatting=False)
# #
# # words = 'Lorem ipsum dolor <b>sit amet, consectetur<i> adipiscing elit.</b> Sed feugiat ante</i> in auctor auctor'.split(' ')
# # for i in range(len(words)):
# #     tb.write_justified_line(' '.join(words[:i]), formatting=True)
#
# #tb.write_formatted_words(long_txt, paragraph_indent=0, new_line_indent=0)
# uw = tb.write_paragraph(long_txt)
# uw = tb.write_paragraph(long_txt, justify=True)
# uw = tb.write_paragraph(long_txt, justify=True)
# uw = tb.write_paragraph(long_txt, justify=True)
# uw = tb.write_paragraph(long_txt, justify=True)
# print(uw)
#
# tb.render().show()


long_txt = '''The Public Land <b>Survey System (PLSS) is <i>the surveying method developed and used </b>in the United States to plat, or</i> divide, real property for sale and settling. Also known as the Rectangular Survey System, it was created by the Land Ordinance of 1785 to survey land ceded to the United States by the Treaty of Paris in 1783, following the end of the American Revolution. Beginning with the Seven Ranges, in present-day Ohio, the PLSS has been used as the primary survey method in the United States. Following the passage of the Northwest Ordinance, in 1787, the Surveyor General of the Northwest Territory platted lands in the Northwest Territory. The Surveyor General was later merged with the General Land Office, which later became a part of the U.S. Bureau of Land Management (BLM). Today, the BLM controls the survey, sale, and settling of the new lands.'''

# testing = tb._wrap_text_TESTING(long_txt, 5, 10)
# print(str(type(testing)) + '_' + str(testing.formatting))
#
# testing.print()
#
# testing = tb._wrap_text_TESTING(long_txt, 5, 10, formatting=True)
# print(str(type(testing)) + '_' + str(testing.formatting))
#
# testing.print()

#uw = tb.write_paragraph(long_txt, justify=True, formatting=True)
#ln = parse_into_line('The Public Land <b>Survey System (PLSS) is <i>the surveying', formatting=True)

#tb._write_fline(ln, 'text_cursor', tb.font_RGBA, justify=True)

# uw = tb._wrap_text_TESTING(long_txt, 0, 0, False, True)
# uw.print()

txt = 'The Public Land <b>Survey System (PLSS) is <i>the surveying'

# uw = tb.write_line(txt, formatting=True, justify=False)
# uw = tb.write_line(txt, formatting=False, justify=False)
# uw = tb.write_line(txt, formatting=True, justify=True)
# uw = tb.write_line(txt, formatting=False, justify=True)
# uw = tb.write_paragraph(long_txt, formatting=True, justify=False)
# uw = tb.write_paragraph(long_txt, formatting=False, justify=False)
uw = tb.write_paragraph(long_txt, formatting=True, justify=True)
uw = tb.write_paragraph(long_txt, formatting=False, justify=True)

tb.render().show()
