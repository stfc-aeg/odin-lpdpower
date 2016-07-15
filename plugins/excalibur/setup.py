from setuptools import setup, find_packages, Extension
import os

# Import requirements from file
with open('requirements.txt') as f:
    required = f.read().splitlines()

# Define the real and stub fem_api extension modules - note these are not true python extension 
# modules in the sense that they cannot be used directly but need to be wrapped with ctypes, but
# we use the setuptools Extension mechanism to manage them anyway

fem_api_stub_source_path='fem_api_stub'
fem_api_stub_sources = ['fem_api_wrapper.c', 'femApi.cpp', 'ExcaliburFemClient.cpp', 'FemApiError.cpp']
 
fem_api_stub = Extension('excalibur.fem_api_stub', 
    sources=[os.path.join(fem_api_stub_source_path, source) for source in fem_api_stub_sources],
    define_macros=[('COMPILE_AS_STUB', None)]
)

setup(
    name='excalibur',
    version='0.1',
    description='EXCALIBUR detector plugin for ODIN framework',
    url='https://github.com/timcnicholls/odin',
    author='Tim Nicholls',
    author_email='tim.nicholls@stfc.ac.uk',
    ext_modules=[fem_api_stub],
    packages = find_packages(),
    install_requires=required,
)
