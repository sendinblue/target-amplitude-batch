#!/usr/bin/env python
from setuptools import setup

setup(
    name="target-amplitude",
    version="0.1.0",
    description="Singer.io target for loading data to Amplitude Batch / Identify APIs",
    author="HichemELB",
    url="http://singer.io",
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    py_modules=["target_amplitude"],
    install_requires=[
        "singer-python==5.8.0",
        "adjust-precision-for-schema==0.3.3",
        "jsonschema==2.6.0",
        "singer==0.1.1",
        "amplitude-analytics==0.3.0",
    ],
    entry_points="""
    [console_scripts]
    target-amplitude=target_amplitude:main
    """,
)
