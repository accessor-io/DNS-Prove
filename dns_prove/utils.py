import hashlib

def build_proof(name, rrsig, rrset):
    proof = {
        "name": name,
        "rrsig": rrsig,
        "rrset": rrset
    }
    return proof

def construct_rrsig(name, type, ttl, algorithm, key, signature):
    """Construct an RRSIG record"""
    return {
        "name": name,
        "type": "RRSIG",
        "ttl": ttl,
        "class": "IN",
        "flush": False,
        "data": {
            "typeCovered": type,
            "algorithm": algorithm,
            "key": key,
            "signature": signature
        }
    }

def construct_rrset(name, type, ttl, flags, algorithm, key):
    return {
        "name": name,
        "type": type,
        "ttl": ttl,
        "class": "IN",
        "flush": False,
        "data": {
            "flags": flags,
            "algorithm": algorithm,
            "key": key
        }
    }

def hash_data(data):
    """Hash data using SHA256"""
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).digest()
