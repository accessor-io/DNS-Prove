from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dns-prove",
    version="1.2",
    author="Cory Thorbeck",
    author_email="acc@accessor.io",
    description="A tool to convince an Ethereum DNSSEC oracle of the contents of DNS records",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/accessor-io/DNS-Prove",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "web3>=5.31.3",
        "dnspython>=2.4.2",
        "cryptography>=41.0.0",
        "eth-utils>=2.2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "flake8>=6.1.0",
            "black>=23.7.0",
            "isort>=5.12.0",
            "pytest-cov>=4.1.0",
        ],
        "docs": [
            "sphinx>=7.1.2",
            "sphinx-rtd-theme>=1.3.0",
            "myst-parser>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "dns-prove=dns_prove.client:main",
        ],
    },
)
