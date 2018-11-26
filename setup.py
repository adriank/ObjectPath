import os
from setuptools import setup

def read(*rnames):
  return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (read('README.rst') + '\n' + 'Download\n' '********\n')

setup(
  name='objectpath',
  version=read('VER').strip(),
  description='The agile query language for semi-structured data. #JSON',
  long_description=long_description,
  url='http://adriank.github.io/ObjectPath',
  author='Adrian Kalbarczyk',
  author_email='adrian.kalbarczyk@gmail.com',
  license='MIT License',
  packages=['objectpath', 'objectpath.utils', 'objectpath.core'],
  # package_dir={'': 'objectpath'},
  keywords="query, tree, JSON, nested structures",
  classifiers=[
    "Development Status :: 6 - Mature", "Intended Audience :: Developers",
    "Intended Audience :: Science/Research", "License :: OSI Approved :: MIT License",
    "Programming Language :: Python",
    "Topic :: Software Development :: Libraries :: Python Modules"
  ],
  zip_safe=True,
  entry_points={'console_scripts': ['objectpath = objectpath.shell:main']},
  test_suite="tests"
)
