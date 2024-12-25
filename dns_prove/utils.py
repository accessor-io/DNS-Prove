import hashlib

def build_proof(name, rrsig, rrset):
    proof = {
        "name": name,
        "rrsig": rrsig,
        "rrset": rrset
    }
    return proof

def construct_rrsig(name, type, ttl, algorithm, key, signature):
    return {
        "name": name,
        "type": type,
        "ttl": ttl,
        "class": "IN",
        "flush": False,
        "data": {
            "typeCovered": type,
            "algorithm": algorithm,
            "labels": 0,
            "originalTTL": ttl,
            "expiration": 2528174800,
            "inception": 1526834834,
            "keyTag": 5647,
            "signersName": name,
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
    return hashlib.sha256(data.encode()).hexdigest()
