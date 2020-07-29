import io

from setuptools import find_packages
from setuptools import setup

with io.open("README.rst", "rt", encoding="utf8") as f:
    readme = f.read()

setup(
    name="datastore",
    version="1.0.0",
    url="https://learningstuff.martinlanser.com/",
    license="BSD",
    maintainer="Martin Lanser",
    maintainer_email="martinlanser@gmail.com",
    description="A simple data store for IOT sensors and similar data loggers.",
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["flask", "flask-login","flask_wtf", "wtforms", "Flask-SQLAlchemy", "Flask-Mail", "Flask-Limiter"],
    extras_require={"test": ["pytest", "coverage", "flake8"]},
)