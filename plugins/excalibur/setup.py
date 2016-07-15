from setuptools import setup, find_packages, Extension
import os

# Import requirements from file
with open('requirements.txt') as f:
    required = f.read().splitlines()

# Define the real and stub fem_api extension modules 
fem_api_extension_path='fem_api_extension'
fem_api_wrapper_source = os.path.join(fem_api_extension_path, 'fem_api_wrapper.c')

fem_api_stub_source_path=os.path.join(fem_api_extension_path, 'stub')
fem_api_stub_sources = [fem_api_wrapper_source] + [
                            os.path.join(fem_api_stub_source_path, source) for source in [
                                'femApi.cpp', 'ExcaliburFemClient.cpp', 'FemApiError.cpp']
                             ]

fem_api_stub = Extension('excalibur.fem_api_stub', 
    sources=fem_api_stub_sources,
    include_dirs=[fem_api_stub_source_path],
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
