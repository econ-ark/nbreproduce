#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.md') as history_file:
    history = history_file.read()

requirements = ['nbformat', 'docker']

setup_requirements = ['pytest-runner',]

test_requirements = ['pytest>=3', ]

setup(
    author="Mridul Seth",
    author_email='seth.mridul@gmail.com',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Reproduce Jupyter Notebooks inside Docker Containers.",
    entry_points={
        'console_scripts': [
            'nbreproduce=nbreproduce.cli:main',
        ],
    },
    install_requires=requirements,
    license="BSD license",
    long_description=readme + '\n\n' + history,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords='nbreproduce',
    name='nbreproduce',
    packages=find_packages(include=['nbreproduce', 'nbreproduce.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/MridulS/nbreproduce',
    version='0.4.0',
    zip_safe=False,
)
