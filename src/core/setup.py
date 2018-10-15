# coding=utf-8
import setuptools
from distutils.core import setup

setup(
    name='prometheus',
    version='0.2.0',
    packages=['prometheus', 'prometheus.misc', 'prometheus.server', 'prometheus.server.socketserver'],
    license='Apache License Version 2.0',
    long_description=open('README.txt').read(),
    author='Hans Christian Winther-Sorensen',
    author_email='hc@wsh.no',
    url='https://github.com/hwinther/lanot/'
)
