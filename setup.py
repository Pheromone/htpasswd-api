#!/usr/bin/env python

from distutils.core import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(name='htpasswd_api',
      version='0.5.2',
      description='API to configure HTPassword files',
      author='Pierre Paul Lefebvre',
      author_email='info@pierre-paul.com',
      install_requires=required,
      url='https://jeto.io',
      packages=['htpasswd_api'],
)
