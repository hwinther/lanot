import setuptools
from distutils.core import setup

setup(
    name='prometheus',
    version='0.1.8b',
    packages=['prometheus', 'prometheus.misc', 'prometheus.server', 'prometheus.server.socketserver'],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.txt').read(),
    author='Hans Christian Winther-Sorensen',
    author_email='hc@wsh.no',
    url='https://prometheus.wsh.no'
)
