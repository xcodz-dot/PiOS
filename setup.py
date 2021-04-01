import setuptools
from denverapi import pysetup

with open("README.md") as file:
    long_description = file.read()

requirements = [
    "denver-api>=2.6.0b3",
    "setuptools~=51.1.0",
    "requests",
    "packaging",
    "rich",
    "Pyparsing",
    "html2text",
]

setuptools.setup(
    name="PiOS",
    version="0.11.0",
    packages=setuptools.find_packages()
    + setuptools.find_namespace_packages(include=["pios.*", "pios"]),
    package_data=pysetup.find_package_data("pios", "pios"),
    url="https://github.com/xcodz-dot/PiOS",
    license="MIT License",
    author="xcodz",
    author_email="",
    description="PiOS, A full featured python written OS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
    install_requires=requirements,
    keywords=["PiOS", "python", "os", "github", "pyos", "operating", "system"],
    extras_require={"SDK": ["PiOS-SDK"]},
)
