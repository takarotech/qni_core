#!/usr/bin/python3

import platform
from setuptools import setup, find_packages


install_requires =['pygame', 'numpy']
if platform.system() == 'Linux':
    install_requires.append('evdev')

setup(
    name='qni_core',
    version='1.0.0',
    author='Arad Eizen',
    author_email='arad.rgb@gmail.com',
    description='Qni playground core modules',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=install_requires,
)
