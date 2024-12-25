from setuptools import setup, find_packages

setup(
    name='dns_prove',
    version='1.2',
    packages=find_packages(),
    install_requires=[
        'web3',
        'dnspython',
        'cryptography',
    ],
    entry_points={
        'console_scripts': [
            'dns_prove=dns_prove.client:main',
        ],
    },
    author='Cory Thorbeck',
    author_email='acc@accessor.io',
    description='A tool to convince an Ethereum DNSSEC oracle of the contents of DNS records',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/accessor-io/dns_prove',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
