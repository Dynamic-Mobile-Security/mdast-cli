from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="mdast_cli",

    version='2025.6.3',


    author="Dynamic-Mobile-Security",
    description="Dynamic-Mobile-Security",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Dynamic-Mobile-Security/mdast-cli",
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['device.properties']},
    install_requires=[
        'altgraph==0.17',
        'beautifulsoup4==4.10.0',
        'cachetools==4.1.1',
        'certifi>=2023.7.22',
        'cffi==1.15.0',
        'chardet>=3.0.4',
        'charset-normalizer==2.0.12',
        'cryptography>=37.0.2',
        'google==3.0.0',
        'google-api-core==1.22.4',
        'google-api-python-client==1.12.3',
        'google-auth==1.22.1',
        'google-auth-httplib2==0.0.4',
        'googleapis-common-protos==1.52.0',
        'httplib2==0.21.0',
        'idna==2.10',
        'protobuf>=4.21.6',
        'pyasn1==0.4.8',
        'pyasn1-modules==0.2.8',
        'pycparser==2.21',
        'pyparsing==3.0.7',
        'pytz>=2021.1',
        'requests>=2.23.0',
        'rsa==4.8',
        'six>=1.15.0',
        'soupsieve==2.3.1',
        'uritemplate==3.0.1',
        'urllib3>=1.26.13'
    ],
    entry_points={
        'console_scripts': [
            'mdast_cli=mdast_cli.mdast_scan:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
    ],
)
