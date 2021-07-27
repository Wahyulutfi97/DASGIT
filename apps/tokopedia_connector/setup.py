# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in tokopedia_connector/__init__.py
from tokopedia_connector import __version__ as version

setup(
	name='tokopedia_connector',
	version=version,
	description='Tokopedia Connector',
	author='DAS',
	author_email='digitalasiasolusindo@gmail.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
