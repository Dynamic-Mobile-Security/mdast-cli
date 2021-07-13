from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="mdast_cli",
    version='2.3',
    author="",
    description="Dynamic-Mobile-Security",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Dynamic-Mobile-Security/mdast-cli",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
         'requests > 2.20'
    ],
    entry_points ={
            'console_scripts': [
                'mdast_cli=mdast_cli.mdast_scan:main'
            ]
        },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
    ],
)
