from setuptools import setup
import piltextbox._constants as constants

descrip = 'Streamlined text writing on images, using the Pillow (PIL) library'

long_description = (
    "An extension for the Pillow (PIL) library for streamlined "
    "writing of text in an image, with automatic textwrapping and "
    "indendation, optional text-block justification, configurable font "
    "settings, and basic bold/italic formatting.\n\n"
    "Visit [the GitHub repository](https://github.com/JamesPImes/piltextbox) "
    "for a quickstart guide."
)

setup(
    name='piltextbox',
    version=constants.__version__,
    packages=[
        'piltextbox', 'piltextbox.textbox', 'piltextbox.textbox.formatting'
    ],
    url=constants.__website__,
    license='MIT',
    author=constants.__author__,
    author_email=constants.__email__,
    description=descrip,
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_data={'': ['LICENSE.txt', 'requirements.txt']},
    include_package_data=True
)
