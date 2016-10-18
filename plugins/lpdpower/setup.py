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
    install_requires=['odin==0.1'],
    dependency_links=['https://github.com/percival-detector/odin/zipball/v0.1#egg=odin-0.1'],
    extras_require={
        'test' : ['nose', 'coverage', 'mock']
    }
)
