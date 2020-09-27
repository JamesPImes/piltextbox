from setuptools import setup

descrip = 'Streamlined text writing on images, using the Pillow (PIL) library'

long_description = (
    "An extension for the Pillow (PIL) library for streamlined "
    "writing of text in an image, with automatic textwrapping and "
    "indendation, optional text-block justification, and configurable font "
    "settings.\n\n"
    "Visit [the GitHub repository](https://github.com/JamesPImes/piltextbox) "
    "for a quickstart guide."
)

setup(
    name='piltextbox',
    version='0.1',
    packages=['piltextbox', 'piltextbox.textbox'],
    url='https://github.com/JamesPImes/piltextbox',
    license='MIT',
    author='James P. Imes',
    author_email='jamesimes@gmail.com',
    description=descrip,
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_data={'': ['LICENSE.txt', 'requirements.txt']},
    include_package_data=True
)
