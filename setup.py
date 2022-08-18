import setuptools

setuptools.setup(
    name="jarvis-pkg",
    packages=setuptools.find_packages(),
    scripts=['bin/jarvis-pkg'],
    version="0.0.1",
    author="Luke Logan",
    author_email="llogan@hawk.iit.edu",
    description="An installer for applications",
    url="https://github.com/lukemartinlogan/jarvis-pkg",
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 0 - Pre-Alpha",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: None",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Installer",
    ],
    long_description=""
)
