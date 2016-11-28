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
    install_requires=['odin==0.1'],
    dependency_links=['https://github.com/percival-detector/odin/zipball/0.1#egg=odin-0.1'],
    extras_require={
        'test': ['nose', 'coverage', 'mock']
    },
)
