from setuptools import setup, find_packages

setup(
      name='booklist',
      version='0.1',
      author_email='martinlanser@gmail.com',
      packages=['booklist'],
      package_data={},
      install_requires=['Flask', 'SQLAlchemy'],
      entry_points={}
)