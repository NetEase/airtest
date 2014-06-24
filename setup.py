# coding: utf-8
#

from setuptools import setup, find_packages

setup(
      name='airtest',
      version='0.1',
      description='mobile test(black air) python lib',
      packages = find_packages(),
      #py_modules=['airtest'],

      author='codeskyblue',
      author_email='codeskyblue@gmail.com',

      requires=['requests', 'androidviewclient'],
     )
