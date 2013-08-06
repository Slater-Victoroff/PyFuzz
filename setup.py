try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="PyFuzz",
    version="0.1.0",
    author="Slater Victoroff",
    author_email="Slater.R.Victoroff@gmail.com",
    packages=["pyfuzz"],
    url="http://pypi.python.org/pypi/PyFuzz/",
    license="LICENSE.txt",
    description="Simple fuzz testing for unit tests, i18n, and security",
    long_description=open("README.txt").read(),
    install_requires=[
        "lxml >= 2.3.2",
        "requests >= 1.2.3",
        "numpy >= 1.6.1"
    ],
)