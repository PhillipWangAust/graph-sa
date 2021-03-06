# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='simulated_annealing',
      version='1.4.0.rc1',
      description='Simulated Annealing solver for networkx graphs',
      keywords='simulated annealing, graph, distributed average consensus, convergence rate',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/vonNiklasson/graph-sa',
      author='Johan Niklasson, Oskar Hahr',
      author_email='jnikl@kth.se, ohahr@kth.se',
      license='MIT',
      packages=find_packages(exclude=['twine']),
      install_requires=[
            'cycler',
            'decorator',
            'extended-networkx-tools',
            'kiwisolver',
            'matplotlib',
            'networkx',
            'numpy',
            'scipy',
            'pyparsing',
            'python-dateutil',
      ],
      py_modules=['six'],
      python_requires='~=3.6',
      zip_safe=False,
      classifiers=[
            # How mature is this project? Common values are
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 3 - Alpha',

            # Indicate who your project is intended for
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',

            # Topics
            'Topic :: System :: Distributed Computing',
            'Topic :: Scientific/Engineering :: Mathematics',


            # Pick your license as you wish (should match "license" above)
            'License :: OSI Approved :: MIT License',

            # Specify the Python versions you support here. In particular, ensure
            # that you indicate whether you support Python 2, Python 3 or both.
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
      ],
)