import os
from setuptools import setup
import pandoc

pandoc.core.PANDOC_PATH = '/usr/bin/pandoc'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

def md2re(s):
	doc = pandoc.Document()
	doc.markdown = s
	return doc.rst

long_description = (
    md2re(read('../README.md'))
    + '\n' +
    'Download\n'
    '********\n'
    )

print long_description

setup(name='objectpath',
			version='0.4',
			description='The agile query language for semi-structured data. #JSON',
			long_description=long_description,
			url='http://adriank.github.io/ObjectPath',
			author='Adrian Kalbarczyk',
			author_email='adrian.kalbarczyk@gmail.com',
			license='AGPLv3',
			packages=['objectpath','objectpath.utils','objectpath.core'],
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
			}
		)
