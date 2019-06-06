#!/usr/bin/python
# -*- coding: utf-8 -*-
from setuptools import setup

__version__ = '0.1.7'


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='emplo-nameko-zipkin',
    version=__version__,
    author="Maxim Kiyan <maxim.k@fraglab.com>, Zbigniew Siciarz <zbigniew.siciarz@emplocity.pl>",
    url='https://github.com/Emplocity/nameko-zipkin',
    description='Zipkin tracing for nameko framework',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['nameko_zipkin'],
    install_requires=[
        'py_zipkin>=0.7.1',
        'nameko>=2.6.0',
    ],
)
