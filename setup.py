from setuptools import find_packages, setup

setup(
    name='sccontroller',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'flask-api',
        'flask-jwt',
        'py-solc-x',
        'web3'
    ],
)