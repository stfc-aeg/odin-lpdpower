from setuptools import setup, find_packages
import versioneer

setup(
    name='lpdpower',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='XFEL LPD PSCU plugin for ODIN framework',
    url='https://github.com/timcnicholls/odin',
    author='Tim Nicholls',
    author_email='tim.nicholls@stfc.ac.uk',
    packages=find_packages(),
    install_requires=['odin'],
    dependency_links=['https://github.com/odin-detector/odin-control/zipball/master#egg=odin'],
    extras_require={
        'test': ['nose', 'coverage', 'mock']
    },
)
