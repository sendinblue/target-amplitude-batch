#!/usr/bin/env python
from setuptools import setup

setup(
    name="target-amplitude-batch",
    version="0.1.0",
    description="Singer.io target for extracting data",
    author="Stitch",
    url="http://singer.io",
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    py_modules=["target_amplitude_batch"],
    install_requires=[
        "singer-python>=5.0.12",
    ],
    entry_points="""
    [console_scripts]
    target-amplitude-batch=target_amplitude_batch:main
    """,
    packages=["target_amplitude_batch"],
    package_data = {},
    include_package_data=True,
)
