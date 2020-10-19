import setuptools
import denver

with open("README.md") as file:
    long_description = file.read()
with open("requirements.txt") as file:
    requirements = file.read()
    requirements = requirements.split("\n")

setuptools.setup(
    name='PiOS',
    version='0.1',
    packages=setuptools.find_packages()+setuptools.find_namespace_packages(),
    package_data=denver.pysetup.find_package_data("pios", "pios"),
    url='https://github.com/xcodz-dot/PiOS',
    license='MIT License',
    author='xcodz',
    author_email='',
    description='PiOS, A full featured python written OS',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
    install_requires=requirements
)
