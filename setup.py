###############################################################################
#####   Setup.py - installs all the required packages and dependancies    #####
###############################################################################

import pathlib
from setuptools import setup, find_packages
import sys
import iso3166_updates

#ensure python version is greater than 3
if (sys.version_info[0] < 3):
    sys.exit('Python 3 is the minimum version requirement.')

#get path to README file
HERE = pathlib.Path(__file__).parent
README = (HERE / 'README.md').read_text()

setup(name='iso3166-updates',
      version=iso3166_updates.__version__,
      description='A Python package that pulls the latest updates & changes to all ISO3166 listed countries.',
      long_description = README,
      long_description_content_type = "text/markdown",
      author=iso3166_updates.__license__,
      author_email=iso3166_updates.__authorEmail__,
      maintainer=iso3166_updates.__maintainer__,
      license=iso3166_updates.__license__,
      url=iso3166_updates.__url__,
      keywords=["iso", "iso3166", "beautifulsoup", "python", "pypi", "countries", "country codes", "csv" \
            "iso3166-2", "iso3166-1"],
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'License :: Free For Educational Use',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',	
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
      install_requires=[
          'beautifulsoup4>=4.11.1',
          'pandas',
          'requests>=2.28.1',
          'iso3166'
      ],
     test_suite='tests',
     packages=find_packages(),
     include_package_data=True,
     zip_safe=False)
