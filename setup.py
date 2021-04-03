import setuptools
from denverapi import setup_utils as pysetup

with open("README.md") as file:
    long_description = file.read()

requirements = [
    "denver-api>=3.0.0b0",
    "setuptools>=51",
    "requests",
    "packaging",
    "rich",
    "toml",
    "wget",
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
