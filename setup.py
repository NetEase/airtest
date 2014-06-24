# coding: utf-8
#

from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

setup(
      name='airtest',
      version='0.1.0624',
      description='mobile test(black air) python lib',
      long_description=long_description,

      author='codeskyblue',
      author_email='codeskyblue@gmail.com',

      packages = find_packages(),
      install_requires=['androidviewclient', 'requests', 'docopt'],
      entry_points='''
      [console_scripts]
      air.test = airtest.cli:main
      ''')
