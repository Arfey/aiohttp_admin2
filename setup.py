import sys
import os
import pathlib

from setuptools import setup, find_packages

PY_VER = sys.version_info

templates = pathlib.Path(__file__).parent / 'aiohttp_admin2' / 'templates'


def package_files(directory):
    paths = []
    for (path, _, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


if not PY_VER >= (3, 5):
    raise RuntimeError("aiohttp_admin doesn't support Python earlier than 3.5")

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = []

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    name='aiohttp_admin2',
    description="Admin interface for aiohttp application.",
    long_description=readme + '\n\n' + history,
    author="Mykhailo Havelia",
    author_email='misha.gavela@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Framework :: AsyncIO',
        'Operating System :: POSIX',
        'Environment :: Web Environment',
    ],
    keywords='aiohttp_admin2',
    license="Apache Software License 2.0",
    install_requires=requirements,
    packages=find_packages(),
    package_data={
        '': package_files(templates),
    },
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/Arfey/aiohttp_admin2',
    version='0.1.0',
    platforms=['POSIX'],
    zip_safe=False,
)
