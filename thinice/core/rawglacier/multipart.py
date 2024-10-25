import hashlib
from rich.pretty import pprint

def initiate_upload(client, vault_name, desc: str, part_size):
    response = client.initiate_multipart_upload(
        vaultName=vault_name, 
        archiveDescription=desc,
        partSize=str(part_size))
    return response['uploadId']

def upload_part(client, vault_name, upload_id, range_start, part_data, total_size):
    range_end = range_start + len(part_data) - 1
    response = client.upload_multipart_part(
        vaultName=vault_name,
        uploadId=upload_id,
        range='bytes {}-{}/{}'.format(range_start, range_end, total_size),
        body=part_data
    )

    return response['checksum']

def complete_upload(client, vault_name, upload_id, checksum, archive_size):
    response = client.complete_multipart_upload(
        vaultName=vault_name,
        uploadId=upload_id,
        checksum=checksum,
        archiveSize=str(archive_size)
    )
    return response['archiveId']

def calculate_part_size(total_size):
    def round_up_to_power_of_two(n):
        # Если n уже степень двойки, просто возвращаем его
        if n & (n - 1) == 0:
            return n
        # Иначе находим ближайшую степень двойки
        return 1 << (n - 1).bit_length()


    # Определение минимального и максимального размеров части
    min_part_size = 4 * 1024 * 1024  # 4 МБ
    max_part_size = 4 * 1024 * 1024 * 1024  # 4 ГБ
    
    psize = round_up_to_power_of_two( int(total_size / 10000) )

    if psize<min_part_size:
        return min_part_size
    if psize>max_part_size:
        return max_part_size
    return psize

def calculate_tree_hash(part_checksums):
    # Calculate the tree hash based on part checksums
    if not part_checksums:
        return None
    
    # Create a list to hold the hashes
    hashes = []
    
    # For each part checksum, convert it to bytes and hash it
    for checksum in part_checksums:
        hashes.append(bytes.fromhex(checksum))
    
    # While there is more than one hash, calculate the next level of tree hash
    while len(hashes) > 1:
        new_hashes = []
        for i in range(0, len(hashes), 2):
            if i + 1 < len(hashes):
                # Concatenate two hashes and hash the result
                combined = hashes[i] + hashes[i + 1]
                new_hash = hashlib.sha256(combined).digest()
                new_hashes.append(new_hash)
            else:
                # If there's an odd number of hashes, carry over the last one
                new_hashes.append(hashes[i])
        hashes = new_hashes
    
    # Return the final tree hash as a hex string
    return hashes[0].hex()
