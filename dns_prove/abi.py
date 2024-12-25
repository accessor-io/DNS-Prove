# Basic DNSSEC Oracle ABI - you'll want to replace this with your actual Oracle ABI
dnssec_oracle_abi = [
    {
        "inputs": [{"type": "bytes", "name": "proof"}],
        "name": "verifySignedTextRecord",
        "outputs": [{"type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function"
    }
    # Add other ABI entries as needed
] 