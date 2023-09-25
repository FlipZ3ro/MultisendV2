import json
from web3 import Web3

def send_tokens(w3, sender_address, private_key, contract_address, recipients, contract_abi):
    # Baca ABI dari file contract_abi.json (berdasarkan ABI yang Anda berikan)
    # with open('contract_abi.json', 'r') as abi_file:
    #     contract_abi = json.load(abi_file)

    # Buat objek kontrak
    contract = w3.eth.contract(address=contract_address, abi=contract_abi)

    # Nonaktifkan pengecekan gasPrice otomatis
    w3.middleware_onion.clear()

    # Definisikan harga gas yang cukup tinggi (misalnya 20 Gwei)
    gas_price = w3.to_wei('0.05', 'gwei')

    # Definisikan gas limit
    gas_limit = 200000

    # Definisikan nonce (jika Anda memiliki multiple transaksi, biasanya nonce harus disesuaikan secara manual)
    w3.eth.default_account = Web3.to_checksum_address(sender_address)  # Konversi ke format checksum
    nonce = w3.eth.get_transaction_count(sender_address)

    # Inisialisasi total gas yang dibutuhkan
    total_gas = 0

    # Kumpulkan data transaksi untuk setiap penerima beserta nomor urut transaksi
    txs = []
    tx_sequence_number = 0  # Nomor urut transaksi dimulai dari 0
    for recipient_address, amount in recipients.items():
        recipient_address_checksum = Web3.to_checksum_address(recipient_address)  # Konversi ke format checksum
        amount_in_wei = w3.to_wei(amount, 'ether')
        tx = contract.functions.transfer(recipient_address_checksum, amount_in_wei).build_transaction({
            'gas': gas_limit,
            'gasPrice': gas_price,
            'nonce': nonce,
        })
        txs.append((tx_sequence_number, tx))  # Menambahkan nomor urut bersama dengan transaksi yang akan dibuat
        total_gas += gas_limit
        nonce += 1
        tx_sequence_number += 1  # Menambahkan nomor urut untuk transaksi berikutnya

    # Hitung total biaya transaksi
    total_cost = total_gas * gas_price

    # Verifikasi apakah pengirim memiliki saldo yang cukup untuk mengirimkan total biaya transaksi
    sender_balance = w3.eth.get_balance(sender_address)
    if sender_balance < total_cost:
        raise ValueError("Saldo pengirim tidak mencukupi untuk biaya transaksi.")

    # Buat transaksi gabungan
    signed_txs = []
    for tx_sequence, tx in txs:
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        signed_txs.append((tx_sequence, signed_tx))

    # Kirim transaksi gabungan
    for tx_sequence, signed_tx in signed_txs:
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"Transaksi {tx_sequence} berhasil dikirim. Hash transaksi: {tx_hash.hex()}")
