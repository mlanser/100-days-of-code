
from setuptools import setup, find_packages
from speedtest.core.version import get_version

VERSION = get_version()

f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name='speedtest',
    version=VERSION,
    description='SpeedTest checks and logs internet speed for current network connection',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Martin Lanser',
    author_email='martinlanser@gmail.com',
    url='https://github.com/johndoe/myapp/',
    license='unlicensed',
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    package_data={'speedtest': ['templates/*']},
    include_package_data=True,
    entry_points="""
        [console_scripts]
        speedtest = speedtest.main:main
    """,
)
