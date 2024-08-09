from setuptools import setup, find_packages


def scan_requirements(req='requirements.txt'):
    with open(req) as f:
        return f.read().splitlines()


setup(
    name="phreeqc_database_tools",
    version="1.0.0",
    author="Joshua Leiper",
    author_email="jjl122@ic.ac.uk",
    description="A short description of your package",
    packages=find_packages(),
    # install_requires=scan_requirements(),
)
