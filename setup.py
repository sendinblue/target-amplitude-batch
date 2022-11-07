#!/usr/bin/env python
from setuptools import setup

setup(
    name="target-amplitude-batch",
    version="2.0.0",
    description="Singer.io target for loading data to Amplitude Batch / Identify APIs",
    author="HichemELB",
    url="git@github.com:DTSL/target-amplitude-batch.git",
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    py_modules=["target_amplitude_batch", "utils"],
    install_requires=[
        "singer-python==5.12.2",
        "adjust-precision-for-schema==0.3.3",
        "jsonschema==2.6.0",
        "amplitude-analytics==1.1.0",
        "pytz==2022.1",
    ],
    entry_points="""
    [console_scripts]
    target-amplitude-batch=target_amplitude_batch:main
    """,
)
