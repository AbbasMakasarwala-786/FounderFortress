from setuptools import setup,find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()


setup(
    name="mlops-5",
    version="0.1",
    author="Abbas Makasarwala",
    packages=find_packages(),
    install_requires =requirements,
)