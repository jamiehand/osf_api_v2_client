#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    'six',
    'vcrpy',
    'requests',
    # TODO: put package requirements here
]

test_requirements = [
    'nose',
    # TODO: put package test requirements here
]

setup(
    name='osf_api_v2_client',
    version='0.1.0',
    description="A client for accessing the OSF v2 API",
    long_description=readme + '\n\n' + history,
    author="Jamie Hand",
    url='https://github.com/jamiehand/osf_api_v2_client',
    packages=[
        'osf_api_v2_client',
    ],
    package_dir={'osf_api_v2_client':
                 'osf_api_v2_client'},
    include_package_data=True,
    install_requires=requirements,
    license="Apache",
    zip_safe=False,
    keywords='osf_api_v2_client',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
