import requests
import json
from datetime import datetime
from collections import defaultdict
import sqlite3
from sklearn.cluster import DBSCAN
import numpy as np

# BlockCypher API URL
API_URL = "https://api.blockcypher.com/v1/btc/main/addrs/{}/full"

# List of Bitcoin addresses
addresses = [
    
"1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH",
"1CUNEBjYrCn2y1SdiUMohaKUi4wpP326Lb",
"19ZewH8Kk1PDbSNdJ97FP4EiCjTRaZMZQA",
"1EhqbyUMvvs7BfL8goY6qcPbD6YKfPqb7e",
"1E6NuFjCi27W5zoXg8TRdcSRq84zJeBW3k",
"1PitScNLyp2HCygzadCh7FveTnfmpPbfp8",
"1McVt1vMtCC7yn5b9wgX1833yCcLXzueeC",
"1M92tSqNmQLYw33fuBvjmeadirh1ysMBxK",
"1CQFwcjw1dwhtkVWBttNLDtqL7ivBonGPV",
"1LeBZP5QCwwgXRtmVUvTVrraqPUokyLHqe",
"1PgQVLmst3Z314JrQn5TNiys8Hc38TcXJu",
"1DBaumZxUkM4qMQRt2LVWyFJq5kDtSZQot",
"1Pie8JkxBT6MGPz9Nvi3fsPkr2D8q3GBc1",
"1ErZWg5cFCe4Vw5BzgfzB74VNLaXEiEkhk",
"1QCbW9HWnwQWiQqVo5exhAnmfqKRrCRsvW",
"1BDyrQ6WoF8VN3g9SAS1iKZcPzFfnDVieY",
"1HduPEXZRdG26SUT5Yk83mLkPyjnZuJ7Bm",
"1GnNTmTVLZiqQfLbAdp9DVdicEnB5GoERE",
"1NWmZRpHH4XSPwsW6dsS3nrNWfL1yrJj4w",
"1HsMJxNiV7TLxmoF6uJNkydxPFDog4NQum",
"14oFNXucftsHiUMY8uctg6N487riuyXs4h",
"1CfZWK1QTQE3eS9qn61dQjV89KDjZzfNcv",
"1L2GM8eE7mJWLdo3HZS6su1832NX2txaac",
"1rSnXMr63jdCuegJFuidJqWxUPV7AtUf7",
"15JhYXn6Mx3oF4Y7PcTAv2wVVAuCFFQNiP",
"1JVnST957hGztonaWK6FougdtjxzHzRMMg",
"128z5d7nN7PkCuX5qoA4Ys6pmxUYnEy86k",
"12jbtzBb54r97TCwW3G1gCFoumpckRAPdY",
"19EEC52krRUK1RkUAEZmQdjTyHT7Gp1TYT",
"1LHtnpd8nU5VHEMkG2TMYYNUjjLc992bps",
"1LhE6sCTuGae42Axu1L1ZB7L96yi9irEBE",
"1FRoHA9xewq7DjrZ1psWJVeTer8gHRqEvR",
"187swFMjz1G54ycVU56B7jZFHFTNVQFDiu",
"1PWABE7oUahG2AFFQhhvViQovnCr4rEv7Q",
"1PWCx5fovoEaoBowAvF5k91m2Xat9bMgwb",
"1Be2UF9NLfyLFbtm3TCbmuocc9N1Kduci1",
"14iXhn8bGajVWegZHJ18vJLHhntcpL4dex",
"1HBtApAFA9B2YZw3G2YKSMCtb3dVnjuNe2",
"122AJhKLEfkFBaGAd84pLp1kfE7xK3GdT8",
"1EeAxcprB2PpCnr34VfZdFrkUWuxyiNEFv",
"1L5sU9qvJeuwQUdt4y1eiLmquFxKjtHr3E",
"1E32GPWgDyeyQac4aJxm9HVoLrrEYPnM4N",
"1PiFuqGpG8yGM5v6rNHWS3TjsG6awgEGA1",
"1CkR2uS7LmFwc3T2jV8C1BhWb5mQaoxedF",
"1NtiLNGegHWE3Mp9g2JPkgx6wUg4TW7bbk",
"1F3JRMWudBaj48EhwcHDdpeuy2jwACNxjP",
"1Pd8VvT49sHKsmqrQiP61RsVwmXCZ6ay7Z",
"1DFYhaB2J9q1LLZJWKTnscPWos9VBqDHzv",
"12CiUhYVTTH33w3SPUBqcpMoqnApAV4WCF",
"1MEzite4ReNuWaL5Ds17ePKt2dCxWEofwk",
"1NpnQyZ7x24ud82b7WiRNvPm6N8bqGQnaS",
"15z9c9sVpu6fwNiK7dMAFgMYSK4GqsGZim",
"15K1YKJMiJ4fpesTVUcByoz334rHmknxmT",
"1KYUv7nSvXx4642TKeuC2SNdTk326uUpFy",
"1LzhS3k3e9Ub8i2W1V8xQFdB8n2MYCHPCa",
"17aPYR1m6pVAacXg1PTDDU7XafvK1dxvhi",
"15c9mPGLku1HuW9LRtBf4jcHVpBUt8txKz",
"1Dn8NF8qDyyfHMktmuoQLGyjWmZXgvosXf",
"1HAX2n9Uruu9YDt4cqRgYcvtGvZj1rbUyt",
"1Kn5h2qpgw9mWE5jKpk8PP4qvvJ1QVy8su",
"1AVJKwzs9AskraJLGHAZPiaZcrpDr1U6AB",
"1Me6EfpwZK5kQziBwBfvLiHjaPGxCKLoJi",
"1NpYjtLira16LfGbGwZJ5JbDPh3ai9bjf4",
"16jY7qLJnxb7CHZyqBP8qca9d51gAjyXQN",
"18ZMbwUFLMHoZBbfpCjUJQTCMCbktshgpe",
"13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so",
"1BY8GQbnueYofwSuFAT3USAhGjPrkxDdW9",
"1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ",
"19vkiEajfhuZ8bs8Zu2jgmC6oqZbWqhxhG",
"19YZECXj3SxEZMoUeJ1yiPsw8xANe7M7QR",
"1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU",
"1JTK7s9YVYywfm5XUH7RNhHJH1LshCaRFR",
"12VVRNPi4SJqUTsp6FmqDqY5sGosDtysn4",
"1FWGcVDK3JGzCC3WtkYetULPszMaK2Jksv",
"1J36UjUByGroXcCvmj13U6uwaVv9caEeAt",
"1DJh2eHFYQfACPmrvpyWc8MSTYKh7w9eRF",
"1Bxk4CQdqL9p22JEtDfdXMsng1XacifUtE",
"15qF6X51huDjqTmF9BJgxXdt1xcj46Jmhb",
"1ARk8HWJMn8js8tQmGUJeQHjSE7KRkn2t8",
"1BCf6rHUW6m3iH2ptsvnjgLruAiPQQepLe",
"15qsCm78whspNQFydGJQk5rexzxTQopnHZ",
"13zYrYhhJxp6Ui1VV7pqa5WDhNWM45ARAC",
"14MdEb4eFcT3MVG5sPFG4jGLuHJSnt1Dk2",
"1CMq3SvFcVEcpLMuuH8PUcNiqsK1oicG2D",
"1Kh22PvXERd2xpTQk3ur6pPEqFeckCJfAr",
"1K3x5L6G57Y494fDqBfrojD28UJv4s5JcK",
"1PxH3K1Shdjb7gSEoTX7UPDZ6SH4qGPrvq",
"16AbnZjZZipwHMkYKBSfswGWKDmXHjEpSf",
"19QciEHbGVNY4hrhfKXmcBBCrJSBZ6TaVt",
"1L12FHH2FHjvTviyanuiFVfmzCy46RRATU",
"1EzVHtmbN4fs4MiNk3ppEnKKhsmXYJ4s74",
"1AE8NzzgKE7Yhz7BWtAcAAxiFMbPo82NB5",
"17Q7tuG2JwFFU9rXVj3uZqRtioH3mx2Jad",
"1K6xGMUbs6ZTXBnhw1pippqwK6wjBWtNpL",
"19eVSDuizydXxhohGh8Ki9WY9KsHdSwoQC",
"15ANYzzCp5BFHcCnVFzXqyibpzgPLWaD8b",
"18ywPwj39nGjqBrQJSzZVq2izR12MDpDr8",
"1CaBVPrwUxbQYYswu32w7Mj4HR4maNoJSX",
"1JWnE6p6UN7ZJBN7TtcbNDoRcjFtuDWoNL",
"1KCgMv8fo2TPBpddVi9jqmMmcne9uSNJ5F",
"1CKCVdbDJasYmhswB6HKZHEAnNaDpK7W4n",
"1PXv28YxmYMaB8zxrKeZBW8dt2HK7RkRPX",
"1AcAmB6jmtU6AiEcXkmiNE9TNVPsj9DULf",
"1EQJvpsmhazYCcKX5Au6AZmZKRnzarMVZu",
"1CMjscKB3QW7SDyQ4c3C3DEUHiHRhiZVib",
"18KsfuHuzQaBTNLASyj15hy4LuqPUo1FNB",
"15EJFC5ZTs9nhsdvSUeBXjLAuYq3SWaxTc",
"1HB1iKUqeffnVsvQsbpC6dNi1XKbyNuqao",
"1GvgAXVCbA8FBjXfWiAms4ytFeJcKsoyhL",
"12JzYkkN76xkwvcPT6AWKZtGX6w2LAgsJg",
"1824ZJQ7nKJ9QFTRBqn7z7dHV5EGpzUpH3",
"18A7NA9FTsnJxWgkoFfPAFbQzuQxpRtCos",
"1NeGn21dUDDeqFQ63xb2SpgUuXuBLA4WT4",
"174SNxfqpdMGYy5YQcfLbSTK3MRNZEePoy"
]

# Initialize SQLite database
conn = sqlite3.connect('bitcoin_analysis.db')
cursor = conn.cursor()

def setup_database():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            address TEXT,
            tx_hash TEXT,
            block_height INTEGER,
            block_index INTEGER,
            received_time TEXT,
            confirmed_time TEXT,
            total INTEGER,
            fees INTEGER,
            size INTEGER,
            preference TEXT,
            double_spend BOOLEAN,
            confirmations INTEGER,
            relayed_by TEXT,
            confidence REAL,
            ver INTEGER,
            vin_size INTEGER,
            vout_size INTEGER,
            time_to_confirm REAL,
            inputs TEXT,
            outputs TEXT
        )
    ''')
    conn.commit()

def store_transaction_details(address, details):
    cursor.execute('''
        INSERT INTO transactions (address, tx_hash, block_height, block_index, received_time, confirmed_time, total, fees, size, preference, double_spend, confirmations, relayed_by, confidence, ver, vin_size, vout_size, time_to_confirm, inputs, outputs)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (address, details['Transaction Hash'], details['Block Height'], details['Block Index'], details['Received Time'], details['Confirmed Time'], details['Total'], details['Fees'], details['Size'], details['Preference'], details['Double Spend'], details['Confirmations'], details['Relayed By'], details['Confidence'], details['Ver'], details['Vin Size'], details['Vout Size'], details['Time to Confirm'], json.dumps(details['Inputs']), json.dumps(details['Outputs'])))
    conn.commit()

def get_first_received_transaction(address):
    response = requests.get(API_URL.format(address))
    if response.status_code == 200:
        data = response.json()
        txs = data.get("txs", [])
        for tx in txs:
            for output in tx.get("outputs", []):
                if address in output.get("addresses", []):
                    return tx  # Return the first transaction where the address appears as a recipient
    return None

def extract_public_key(script):
    # Placeholder function to extract public key from script
    # In real-world scenarios, this might require parsing the scriptPubKey and other data
    # Example: P2PKH script: "76a914{pubkey_hash}88ac"
    if script.startswith("76a914") and script.endswith("88ac"):
        return script[6:-4]  # Extract the public key hash
    return None

def identify_address_type(script):
    if script.startswith("76a914") and script.endswith("88ac"):
        return "P2PKH"
    elif script.startswith("a914") and script.endswith("87"):
        return "P2SH"
    elif script.startswith("0014"):
        return "P2WPKH"
    elif script.startswith("0020"):
        return "P2WSH"
    return "Unknown"

def get_comprehensive_details(tx):
    details = {
        "Transaction Hash": tx.get("hash"),
        "Block Height": tx.get("block_height"),
        "Block Index": tx.get("block_index"),
        "Received Time": tx.get("received"),
        "Confirmed Time": tx.get("confirmed"),
        "Total": tx.get("total"),
        "Fees": tx.get("fees"),
        "Size": tx.get("size"),
        "Preference": tx.get("preference"),
        "Double Spend": tx.get("double_spend"),
        "Confirmations": tx.get("confirmations"),
        "Relayed By": tx.get("relayed_by"),
        "Confidence": tx.get("confidence"),
        "Ver": tx.get("ver"),
        "Vin Size": tx.get("vin_sz"),
        "Vout Size": tx.get("vout_sz"),
        "Transaction Time": tx.get("received"),
        "Inputs": [],
        "Outputs": []
    }
    for inp in tx.get("inputs", []):
        input_details = {
            "Previous Transaction Hash": inp.get("prev_hash"),
            "Output Index": inp.get("output_index"),
            "Script": inp.get("script"),
            "Addresses": inp.get("addresses"),
            "Output Value": inp.get("output_value"),
            "Sequence": inp.get("sequence"),
            "Age": inp.get("age"),
            "Witness": inp.get("witness"),
            "Public Key": extract_public_key(inp.get("script")),
            "Address Type": identify_address_type(inp.get("script")),
            "Nonce": inp.get("nonce")  # Adding nonce for same-nonce heuristic
        }
        details["Inputs"].append(input_details)
    
    for out in tx.get("outputs", []):
        output_details = {
            "Value": out.get("value"),
            "Script": out.get("script"),
            "Addresses": out.get("addresses"),
            "Spent By": out.get("spent_by"),
            "Data Hex": out.get("data_hex"),
            "Data String": out.get("data_string"),
            "Output Index": out.get("n"),
            "Public Key": extract_public_key(out.get("script")),
            "Address Type": identify_address_type(out.get("script"))
        }
        details["Outputs"].append(output_details)
    
    # Derive additional data
    received_time = datetime.strptime(tx.get("received"), '%Y-%m-%dT%H:%M:%S.%fZ')
    confirmed_time = datetime.strptime(tx.get("confirmed"), '%Y-%m-%dT%H:%M:%S.%fZ') if tx.get("confirmed") else None
    details["Time to Confirm"] = (confirmed_time - received_time).total_seconds() if confirmed_time else None
    
    return details

def main():
    setup_database()
    for address in addresses:
        tx = get_first_received_transaction(address)
        if tx:
            details = get_comprehensive_details(tx)
            store_transaction_details(address, details)
            print(f"First transaction details for address {address}:")
            print(json.dumps(details, indent=4))
        else:
            print(f"No transactions found for address {address}")
    
    # Analyze for commonalities
    analyze_commonalities()

def analyze_commonalities():
    cursor.execute('SELECT * FROM transactions')
    transactions = cursor.fetchall()

    address_types = defaultdict(int)
    public_keys = defaultdict(list)
    times_to_confirm = []
    shared_inputs = defaultdict(list)
    nonce_groups = defaultdict(list)
    address_reuse = defaultdict(list)
    chain_heuristics = defaultdict(list)

    for tx in transactions:
        tx_hash = tx[1]
        inputs = json.loads(tx[18])
        outputs = json.loads(tx[19])
        for inp in inputs:
            address_types[inp['Address Type']] += 1
            public_keys[inp['Public Key']].append(tx_hash)
            shared_inputs[inp['Addresses'][0]].append(tx_hash)
            if inp['Nonce'] is not None:
                nonce_groups[inp['Nonce']].append(inp['Addresses'][0])
        for out in outputs:
            address_types[out['Address Type']] += 1
            public_keys[out['Public Key']].append(tx_hash)
            address_reuse[out['Addresses'][0]].append(tx_hash)
            chain_heuristics[out['Addresses'][0]].append(tx_hash)
        if tx[17]:
            times_to_confirm.append(tx[17])

    print("\nCommonalities Analysis:")
    print("Address Types Distribution:")
    for addr_type, count in address_types.items():
        print(f"{addr_type}: {count}")
    
    print("\nPublic Key Usage:")
    for pub_key, txs in public_keys.items():
        if pub_key:
            print(f"Public Key {pub_key} used in transactions: {txs}")
    
    print("\nShared Inputs (addresses used as inputs in multiple transactions):")
    for addr, txs in shared_inputs.items():
        print(f"Address {addr} used in transactions: {txs}")

    print("\nSame-Nonce Groups:")
    for nonce, addrs in nonce_groups.items():
        print(f"Nonce {nonce} used by addresses: {addrs}")

    print("\nAddress Reuse:")
    for addr, txs in address_reuse.items():
        print(f"Address {addr} reused in transactions: {txs}")

    print("\nChain Heuristics (addresses appearing in chains of transactions):")
    for addr, txs in chain_heuristics.items():
        print(f"Address {addr} involved in chained transactions: {txs}")

        if times_to_confirm:
            avg_time_to_confirm = sum(times_to_confirm) / len(times_to_confirm)
            print(f"\nAverage Time to Confirm: {avg_time_to_confirm} seconds")

        # Advanced clustering and anomaly detection
        cluster_and_anomaly_detection(transactions)

def cluster_and_anomaly_detection(transactions):
    # Prepare data for clustering
    transaction_data = []
    for tx in transactions:
        tx_hash = tx[1]
        inputs = json.loads(tx[18])
        outputs = json.loads(tx[19])
        for inp in inputs:
            transaction_data.append([inp['Previous Transaction Hash'], inp['Output Index'], inp['Output Value'], inp['Addresses'][0]])
        for out in outputs:
            transaction_data.append([out['Value'], out['Addresses'][0]])

    # Convert data to numpy array for clustering
    data = np.array(transaction_data)

    # Apply DBSCAN clustering algorithm
    clustering = DBSCAN(eps=0.5, min_samples=2).fit(data)
    labels = clustering.labels_

    print("\nClustering Results:")
    unique_labels = set(labels)
    for label in unique_labels:
        if label == -1:
            # Noise points
            print(f"Cluster {label} (Noise):")
        else:
            print(f"Cluster {label}:")
        cluster_points = data[labels == label]
        for point in cluster_points:
            print(point)

    # Anomaly detection: transactions that are classified as noise (label -1) can be considered anomalies
    anomalies = data[labels == -1]
    print("\nAnomalies Detected:")
    for anomaly in anomalies:
        print(anomaly)

if __name__ == "__main__":
    main()
