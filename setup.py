from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = [r.strip() for r in f.read().splitlines()]

setup(
    name='investment-analytics',
    version='0.0.1',
    description='Provides Python interface to various stock data APIs and investment analytics utilities.',
    url='https://github.com/alenlukic/investment-analytics',
    author='Alen Lukic',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Office/Business :: Financial :: Investment',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3'
    ],
    keywords='invest investment investing stock market stocks iex api',
    install_requires=requirements,
    packages=find_packages(),
    python_requires='>=3, <4'
)
