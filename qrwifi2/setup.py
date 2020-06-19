from setuptools import setup, find_packages

setup(
      name='qrwifi2',
      version='0.1',
      author_email='martinlanser@gmail.com',
      packages=['qrwifi2'],
      package_data={},
      install_requires=['pyqrcode', 'numpy', 'click'],
      entry_points={
        'console_scripts': ['qrwifi2 = qrwifi2.cli:start']
      }
)