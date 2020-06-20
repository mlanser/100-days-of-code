from setuptools import setup, find_packages

setup(
      name='wifi2',
      version='0.1',
      author_email='martinlanser@gmail.com',
      packages=['wifi2'],
      package_data={},
      install_requires=['pyqrcode', 'numpy', 'click', 'configparser', 'requests'],
      entry_points={
        'console_scripts': ['wifi2 = wifi2.cli:start']
      }
)