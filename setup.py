import os
from setuptools import setup

def read(*rnames):
    filename = os.path.join(os_path.dirname(__file__), *rnames)
    with open(filename) as f:
        return f.read()

long_description = """{}

Download
********""".format(read('README.rst'))

setup(
    name='objectpath',
    version=read('VER').strip(),
    description='The agile query language for semi-structured data. #JSON',
    long_description=long_description,
    url='http://adriank.github.io/ObjectPath',
    author='Adrian Kalbarczyk',
    author_email='adrian.kalbarczyk@gmail.com',
    license='AGPLv3',
    packages=['objectpath','objectpath.utils','objectpath.core'],
    # package_dir={'': 'objectpath'},
    keywords="query, tree, JSON, nested structures",
    classifiers=[
        "Development Status :: 6 - Mature",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    zip_safe=True,
    entry_points = {
        'console_scripts': [
            'objectpath = objectpath.shell:main'
        ]
    },
    test_suite="tests",
)
