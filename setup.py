"""
Copyright Wenyi Tang 2023

:Author: Wenyi Tang
:Email: wenyitang@outlook.com

"""
from setuptools import find_packages, setup

setup(
    name="zgit",
    version="0.0.1",
    description="zgit",
    packages=find_packages(),
    install_requires=["dateparser", "numpy", "matplotlib"],
    license="MIT",
    author="Wenyi Tang",
    author_email="wenyitang@outlook.com",
    keywords="git statistic",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
