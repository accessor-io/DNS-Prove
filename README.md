user avatar

# DNSSEC Proof

DNSSEC Proof is a tool designed to convince an Ethereum DNSSEC oracle of the contents of DNS records. It interacts with DNS records, constructs proofs, and submits them to a DNSSEC oracle on the Ethereum blockchain.

## Features

- Lookup DNS information and retrieve DNS records.
- Construct DNSSEC proofs.
- Submit proofs to an Ethereum DNSSEC oracle.
- Verify signed text records containing Ethereum addresses.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [DNS Record Types](#DNS-Record-Types)
- [Project Structure](#project-structure)
- [Running Tests](#running-tests)
- [License](#license)

## Installation

### Prerequisites

- Python 3.6 or higher
- pip (Python package installer)

### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/dnssec_proof.git
   cd dnssec_proof

    Install the package and dependencies:

    pip install -r requirements.txt

dnsec

## Usage

After installing the package, you can use the dnssec_proof command-line tool.
Command-Line Interface

Fetch DNS information and submit proofs to a DNSSEC oracle:

dnssec_proof <record_type> <domain> --oracle <oracle_address> [--provider <provider_url>]
    <record_type>: Type of DNS record to fetch (e.g., A, AAAA, TXT)
    <domain>: Domain name to fetch DNS information for
    --oracle: Address of the DNSSEC Oracle contract (required)
    --provider: Web3 provider URL (optional)

## DNS Record Types

The dnssec_proof tool can look up various types of TXT records from DNS. TXT records are used to store text information in DNS and are often used for different purposes, such as verification, authentication, and providing general information. Here are some common types of TXT records that can be looked up:

    SPF (Sender Policy Framework):
        Purpose: Used to specify which mail servers are permitted to send email on behalf of a domain.
        Example: v=spf1 include:_spf.example.com ~all

    DKIM (DomainKeys Identified Mail):
        Purpose: Used for email authentication, allowing the receiver to check if the email was sent by the domain's owner.
        Example: v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC3x...

    DMARC (Domain-based Message Authentication, Reporting & Conformance):
        Purpose: Used to define the policy for handling incoming emails that fail SPF or DKIM checks.
        Example: v=DMARC1; p=none; rua=mailto:dmarc-reports@example.com

    TXT Records for Verification:
        Purpose: Used by various services for domain ownership verification (e.g., Google Search Console, Microsoft Office 365).
        Example: google-site-verification=abc123

    General Text Information:
        Purpose: To provide general information related to the domain.
        Example: This domain is managed by Example Company.

    Custom TXT Records:
        Purpose: Any custom text data that the domain owner wants to associate with the domain.
        Example: key1=value1

Example Command

To look up a TXT record for a domain, you can use the dnssec_proof command like this:

dnssec_proof TXT example.com --oracle 0x1234567890abcdef1234567890abcdef12345678 --provider https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID

Sample TXT Record Lookups

    SPF Record:

    dnssec_proof TXT example.com --oracle 0x1234567890abcdef1234567890abcdef12345678 --provider https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID

Output:

example.com. 600 IN TXT "v=spf1 include:_spf.example.com ~all"

DKIM Record:

dnssec_proof TXT dkim._domainkey.example.com --oracle 0x1234567890abcdef1234567890abcdef12345678 --provider https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID

Output:

dkim._domainkey.example.com. 600 IN TXT "v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC3x..."

DMARC Record:

dnssec_proof TXT _dmarc.example.com --oracle 0x1234567890abcdef1234567890abcdef12345678 --provider https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID

Output:

_dmarc.example.com. 600 IN TXT "v=DMARC1; p=none; rua=mailto:dmarc-reports@example.com"

Verification Record:

dnssec_proof TXT example.com --oracle 0x1234567890abcdef1234567890abcdef12345678 --provider https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID

Output:

example.com. 600 IN TXT "google-site-verification=abc123"

Example

dnssec_proof TXT _ens.example.com --oracle 0x1234567890abcdef1234567890abcdef12345678 --provider {{PROVIDER}}

## Project Structure
```
dnssec_proof/
├── dnssec_proof/
│   ├── client.py
│   ├── dnsprover.py
│   ├── initEth.py
│   ├── __init__.py
│   ├── oracle.py
│   └── utils.py
├── LICENSE
├── README.md
├── requirements.txt
├── setup.py
└── tests/
    ├── __init__.py
    └── test_dnsprover.py
```
Explanation

    dnssec_proof/: Main package directory containing all the necessary modules.
        client.py: CLI entry point to interact with the DNSSEC oracle.
        dnsprover.py: Contains the main functionality to look up DNS records and submit proofs.
        initEth.py: Code for constructing and verifying DNSSEC proofs.
        oracle.py: Defines an Oracle class to interact with a DNSSEC Oracle smart contract.
        utils.py: Utility functions for building proofs and hashing data.
        __init__.py: Marks the directory as a package.
    tests/: Contains unit tests for the project.
        test_dnsprover.py: Sample test file for the dnsprover module.
        __init__.py: Marks the directory as a package.
    LICENSE: License for the project.
    README.md: Project documentation.
    requirements.txt: List of dependencies.
    setup.py: Setup script for packaging the project.

## Running Tests

To run the tests, use a test runner like unittest or pytest.

Using unittest

```python -m unittest discover -s tests```

Using pytest

First, install pytest if you haven't already:

```pip install pytest```

Then, run:

```pytest```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

Feel free to customize the content to better fit your project's specifics, such as replacing placeholder text with your actual details and expanding sections as necessary.

