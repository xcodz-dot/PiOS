import setuptools
from denver import pysetup

with open("README.md") as file:
    long_description = file.read()

requirements = ["pydenver",
                "setuptools~=50.3.0",
                "requests",
                "packaging"]

setuptools.setup(
    name='PiOS',
    version='0.1',
    packages=setuptools.find_packages() + setuptools.find_namespace_packages(include=["pios.*"]),
    package_data=pysetup.find_package_data("pios", "pios"),
    url='https://github.com/xcodz-dot/PiOS',
    license='MIT License',
    author='xcodz',
    author_email='',
    description='PiOS, A full featured python written OS',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
    install_requires=requirements,
    keywords=["PiOS", "python", "os", "github", "pyos", "operating", "system"]
)
