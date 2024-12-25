from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidKey, InvalidSignature

class Result:
    def __init__(self, proofs):
        self.proofs = proofs

    def to_submit(self):
        # Convert proof data to format needed for submission
        return self.proofs[0]  # For now, just return first proof

# Constructing a proof
name = '.'
sig = {
    'name': '.',
    'type': 'RRSIG',
    'ttl': 0,
    'class': 'IN',
    'flush': False,
    'data': {
        'typeCovered': 'DNSKEY',
        'algorithm': 253,
        'labels': 0,
        'originalTTL': 3600,
        'expiration': 2528174800,
        'inception': 1526834834,
        'keyTag': 5647,
        'signersName': '.',
        'signature': b''  # Empty signature, you need to populate this
    }
}

rrs = [
    {
        'name': '.',
        'type': 'DNSKEY',
        'ttl': 3600,
        'class': 'IN',
        'flush': False,
        'data': {
            'flags': 257,
            'algorithm': 253,
            'key': bytes.fromhex("1111")
        }
    },
    {
        'name': '.',
        'type': 'DNSKEY',
        'ttl': 3600,
        'class': 'IN',
        'flush': False,
        'data': {
            'flags': 257,
            'algorithm': 253,
            'key': bytes.fromhex("1111")
        }
    },
    {
        'name': '.',
        'type': 'DNSKEY',
        'ttl': 3600,
        'class': 'IN',
        'flush': False,
        'data': {
            'flags': 257,
            'algorithm': 253,
            'key': bytes.fromhex("1112")
        }
    }
]

# Convert the data to bytes for serialization
data_bytes = name.encode() + sig['data']['signature']
for rr in rrs:
    data_bytes += rr['data']['key']

# Instantiate Result object and generate input data
result = Result([(name, sig, rrs)])
proof_data = result.to_submit()
                                                                                                         
# Verifying a signed text record containing an Ethereum address
def verify_signed_text_record(signature, message, public_key):
    try:
        public_key_bytes = bytes.fromhex(public_key)      
        public_key_obj = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256K1(), public_key_bytes)
        public_key_obj.verify(signature, message.encode(), ec.ECDSA(utils.Prehashed(ec.SHA256())))
        return True
    except ValueError as e:
        # Handle malformed public key
        print(f"Invalid public key format: {e}")
        return False
    except InvalidKey as e:
        # Handle invalid key
        print(f"Invalid key: {e}")
        return False
    except InvalidSignature as e:
        # Handle invalid signature
        print(f"Invalid signature: {e}")
        return False

# Example usage
signature = b''  # Empty signature
message = 'Example message'
public_key = '044e5e5f1e26a1c273d2bfb46117b98409123831c3e9f1d154d022231c434f3b5a94a0f1374348c61752fd1c609ec56a169857d9ab1c90fcb25d9f3cddbc5a2d0'  # Example public key
result = verify_signed_text_record(signature, message, public_key)
print(result)

# Add proper signature generation
def generate_signature(private_key, message):
    return private_key.sign(
        message.encode(),
        ec.ECDSA(hashes.SHA256())
    )

def validate_public_key(public_key_hex):
    try:
        public_key_bytes = bytes.fromhex(public_key_hex)
        if len(public_key_bytes) != 65:  # Uncompressed public key length
            return False
        ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256K1(), public_key_bytes)
        return True
    except (ValueError, Exception):
        return False
