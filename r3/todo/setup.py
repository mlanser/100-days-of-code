
from setuptools import setup, find_packages
from todo.core.version import get_version

VERSION = get_version()

f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name='todo',
    version=VERSION,
    description='A sample TODO app created with Cement',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Martin Lanser',
    author_email='martinlanser@gmail.com',
    url='https://github.com/mlanser/100-days-of-code/r3/todo',
    license='unlicensed',
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    package_data={'todo': ['templates/*']},
    include_package_data=True,
    entry_points="""
        [console_scripts]
        todo = todo.main:main
    """,
)
