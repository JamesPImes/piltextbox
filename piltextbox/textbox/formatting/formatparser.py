# Copyright (c) 2020, James P. Imes. All rights reserved.

# TODO: Receive input text
# TODO: Split text into words by spaces.
# TODO: Find formatting codes (<b>, </b>, <i>, </i>).
#       <b> --> bold=True
#       </b> --> bold=False
#       <i> --> ital=True
#       </i> --> ital=False
# TODO: encode each word into an FWord object.

class FWord:
    """
    The text of a word, and whether or not it should be bolded and/or
    italicized.
    """
    def __init__(self, txt, bold=False, ital=False):
        self.txt = txt
        self.bold = bold
        self.ital = ital
