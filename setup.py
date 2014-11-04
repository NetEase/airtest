# coding: utf-8
#

from setuptools import setup, find_packages

import airtest

long_description = ''
try:
    with open('README.md') as f:
        long_description = f.read()
except:
    pass

setup(
      name='airtest',
      version=airtest.__version__,
      description='mobile test(black air) python lib',
      long_description=long_description,

      author='codeskyblue',
      author_email='codeskyblue@gmail.com',

      packages = find_packages(),
      include_package_data=True,
      package_data={},
      install_requires=[
          #'androidviewclient >= 7.1.1', 
          'click>=3.3',
          'requests', 
          'docopt',
          'pystache',
          'Appium-Python-Client',
          'fuckit'
          ],
      entry_points='''
      [console_scripts]
      air.test = airtest.cli2:main
      ''')
