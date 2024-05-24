from setuptools import setup, find_packages

setup(
    name='dnssec_proof',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'web3', 
        'dnspython',  
    ],
    entry_points={
        'console_scripts': [
            'dnssec_proof=dnssec_proof.dnsprover:main', 
        ],
    },
    author='Cory Thorbcek',
    author_email='acc@accessor.io',
    description='A tool to convince an Ethereum DNSSEC oracle of the contents of DNS records',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/accessor-io/dnssec_proof',  
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
