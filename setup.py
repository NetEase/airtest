# coding: utf-8
#

from setuptools import setup, find_packages

long_description = ''
try:
    with open('README.md') as f:
        long_description = f.read()
except:
    pass

setup(
      name='airtest',
      version='0.2.0717.04',
      description='mobile test(black air) python lib',
      long_description=long_description,

      author='codeskyblue',
      author_email='codeskyblue@gmail.com',

      packages = find_packages(),
      package_data={
          'airtest': ['htmltemplate/*.html', 'htmltemplate/*.js', 'htmltemplate/*.json'],
        },
      install_requires=[
          #'androidviewclient >= 7.1.1', 
          'requests >= 2.3.0', 
          'docopt >= 0.6.2',
          'pystache >= 0.5.4',
          'Appium-Python-Client == 0.9'
          ],
      entry_points='''
      [console_scripts]
      air.test = airtest.cli:main
      ''')
