from setuptools import setup

descrip = 'Streamlined text writing on images, using the Pillow (PIL) library'

long_description = (
    "An extension for the Pillow (PIL) library for streamlined "
    "writing of text in an image, with automatic textwrapping and "
    "indendation, optional text-block justification, configurable font "
    "settings, and basic bold/italic formatting.\n\n"
    "Visit [the GitHub repository](https://github.com/JamesPImes/piltextbox) "
    "for a quickstart guide."
)

MODULE_DIR = 'piltextbox'


def get_constant(constant):
    setters = {
        "version": "__version__ = ",
        "author": "__author__ = ",
        "author_email": "__email__ = ",
        "url": "__website__ = "
    }
    var_setter = setters[constant]
    with open(rf".\{MODULE_DIR}\_constants.py", "r") as file:
        for line in file:
            if line.startswith(var_setter):
                version = line[len(var_setter):].strip('\'\n \"')
                return version
        raise RuntimeError(f"Could not get {constant} info.")


setup(
    name='piltextbox',
    version=get_constant('version'),
    packages=[
        'piltextbox',
        'piltextbox.textbox',
        'piltextbox.textbox.formatting'
    ],
    url=get_constant('url'),
    license='MIT',
    author=get_constant('author'),
    author_email=get_constant('author_email'),
    description=descrip,
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_data={'': ['LICENSE.txt', 'requirements.txt']},
    include_package_data=True
)
