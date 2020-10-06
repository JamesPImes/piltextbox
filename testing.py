

import piltextbox

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

tb.write_paragraph('Hello, testing one two, three.\nAnd testing four, five.')
tb.im.show()