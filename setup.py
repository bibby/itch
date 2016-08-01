# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('README.rst') as readme:
    long_description = readme.read()

setup(
    name='itch',
    version='0.2.0',
    packages=find_packages(),
    description='Twitch APIs client',
    long_description=long_description,
    author='bibby',
    author_email='bibby@bbby.org',
    url='https://github.com/bibby/itch',
    include_package_data=False,
    install_requires=['requests', 'dateutils', 'argparse'],
    entry_points={'console_scripts': [
        'itch = cli:main',
        'itch-plot = plot:main'
    ]},
    keywords='twitch',
    classifiers=[]
)
