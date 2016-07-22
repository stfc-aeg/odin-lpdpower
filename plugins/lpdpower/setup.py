from setuptools import setup, find_packages
import os

# Import requirements from file
with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='lpdpower',
    version='0.1',
    description='EXCALIBUR detector plugin for ODIN framework',
    url='https://github.com/timcnicholls/odin',
    author='Tim Nicholls',
    author_email='tim.nicholls@stfc.ac.uk',
    packages = find_packages(),
    install_requires=required,
)
