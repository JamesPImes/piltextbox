# Copyright (c) 2020, James P. Imes. All rights reserved.

"""
piltextbox - An extension for the Pillow (PIL) library for streamlined
writing of text in an image, with automatic textwrapping and
indendation, optional text-block justification, configurable font
settings, and basic bold/italic formatting.
"""

import piltextbox._constants as _constants
__version__ = _constants.__version__
__version_date__ = _constants.__version_date__
__author__ = _constants.__author__
__email__ = _constants.__email__
__license__ = _constants.__license__
__website__ = _constants.__website__

from piltextbox.textbox import TextBox
