from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

# Grab the version number without importing penguins.
exec(open('esrpoise/_version.py').read())

setup(
    name="esrpoise",
    version=__version__,
    author="Mohammadali Foroozandeh, Jean-Baptiste Verstraete, Jonathan Yong",
    author_email="mohammadali.foroozandeh@chem.ox.ac.uk",
    description=("POISE for ESR"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/foroozandehgroup/esrpoise",
    packages=find_packages(exclude=["tests"]),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        "numpy>=1.17.0",
        "XeprAPI",
        "Py-BOBYQA",
    ]

)
