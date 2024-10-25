from mypy_boto3_glacier import GlacierClient
from mypy_boto3_glacier.type_defs import ListJobsOutputTypeDef

import datetime
import math

from .credentials import AWSCredentials
from .locations import Locations
from .inventory import Inventory
from .utils import iso2dt, calculate_sha256
from .rawglacier.multipart import calculate_part_size, initiate_upload, upload_part, complete_upload, calculate_tree_hash
from .exceptions import ArchiveNotRetrieved
from rich.pretty import pprint
import rich.progress
import boto3
import hashlib
import json
import datetime
from mypy_boto3_glacier import GlacierClient, GlacierServiceResource
from typing import Any, IO
from pathlib import Path
import os

class GlacierVault:
    credentials: AWSCredentials
    client: GlacierClient
    session: boto3.Session
    resource: GlacierServiceResource
    vault: Any
    locations: Locations
    inventory: Inventory
    vault_name: str
    repeat_request: datetime.timedelta
    
    def __init__(self, credentials: AWSCredentials, vault_name: str | None = None):
        self.credentials = credentials
        self.vault_name = vault_name
        self.locations = Locations(base_path=os.path.expanduser(f'~/.local/share/thinice/{credentials.key_id}/'))
        self.session = boto3.Session(
            aws_access_key_id=credentials.key_id,
            aws_secret_access_key=credentials.secret_key,
            region_name=credentials.region
        )
        self.client = self.session.client('glacier')

        if vault_name is not None:
            self.inventory = Inventory(locations=self.locations, vault_name=vault_name)

        self.repeat_request = datetime.timedelta(hours=1)

        # self.resource = boto3.resource('glacier')
        #self.client = boto3.client('glacier')
        #self.vault = self.resource.Vault('-',self.vaultName)


    def list_vaults(self):
        response = self.client.list_vaults()
        # return [vault['VaultName'] for vault in response['VaultList']]
        return response['VaultList']
    
    def list_jobs(self) -> ListJobsOutputTypeDef:
        """ request current jobs and save it in inventory """
        response = self.client.list_jobs(vaultName=self.vault_name)
        self.inventory.set_latest_jobs(response)
        self.inventory.save()
        
        return response['JobList']

    def accept_inventory(self, job: dict) -> bool:
        assert job['Action'] == 'InventoryRetrieval'
        assert job['Completed'] == True and job['StatusCode'] == 'Succeeded'

        job_output = self.client.get_job_output(accountId='-', vaultName=self.vault_name, jobId=job['JobId'])
        inv = json.load(job_output['body'])
        if self.inventory.set_latest_inventory(inv):
            self.inventory.save()
            return True
        return False
    
    def upload_stream(self, stream: IO[bytes], description: str, localdesc: str = None):

        sha256sum = calculate_sha256(stream)        

        response = self.client.upload_archive(
            vaultName=self.vault_name,
            archiveDescription=description,
            body=stream)

        # record this upload
        self.inventory.add_uploaded_file(
            archiveId=response['archiveId'], 
            sha256=sha256sum,
            basename=stream.name,
            description=description, size = os.fstat(stream.fileno()).st_size,
            localdesc=localdesc)
        
        self.inventory.save()

        archiveId = response['archiveId']
        return archiveId


    def upload_stream_multipart(self, stream: IO[bytes], description: str, localdesc: str = None):
        total_size = os.fstat(stream.fileno()).st_size
        sha256sum = calculate_sha256(stream)        

        part_size = calculate_part_size(total_size=total_size)

        # Step 1: Initiate the multipart upload
        upload_id = initiate_upload(client=self.client, vault_name=self.vault_name, desc=description, part_size=part_size)

        # Step 2: Upload parts
        part_checksums = []
        range_start = 0

        while True:
            part_data = stream.read(part_size)
            if not part_data:
                break  # End of file
            
            # Upload part and get checksum
            checksum = upload_part(
                client=self.client,
                vault_name=self.vault_name, 
                upload_id=upload_id, 
                range_start=range_start, 
                part_data=part_data, 
                total_size=total_size)
            part_checksums.append(checksum)
            
            # Update the range start for the next part
            range_start += len(part_data)  # Move to the next part's start position

        # calculate checksum
        # Step 3: Calculate the final checksum
        tree_hash = calculate_tree_hash(part_checksums)

        # Step 3: Complete the multipart upload        
        archive_id = complete_upload(
            client=self.client,
            vault_name=self.vault_name,
            upload_id=upload_id,
            checksum=tree_hash,
            archive_size=total_size)                

        # record this upload
        self.inventory.add_uploaded_file(archiveId=archive_id, description=description, size=total_size)
        self.inventory.add_uploaded_file(
            archiveId=archive_id, 
            sha256=sha256sum,
            basename=stream.name,
            description=description, 
            size=total_size,
            localdesc=localdesc)


        self.inventory.save()


        return archive_id

    def upload_file(self, path: Path, description: str | None):
        description = description or path.name
        with open(path, 'rb') as stream:
            archiveId = self.upload_stream(stream=stream, description=description)
        return archiveId

    def request_inventory(self, force=False):
        job_params = {
            'Type': 'inventory-retrieval',
            'Format': 'JSON'
        }

        now = datetime.datetime.now(tz=datetime.timezone.utc)
        latest_job = self.inventory.get_latest_job(action='InventoryRetrieval')
        if latest_job:
            # isn't it too recent?
            latest_job_dt = iso2dt(latest_job['CreationDate'])
            if ((now - latest_job_dt) < self.repeat_request) and not force:
                print("too recent")
                return
        

        response = self.client.initiate_job(
            vaultName=self.vault_name,
            jobParameters=job_params)
        # pprint(response)

        self.list_jobs()

        # self.inventory.add_job(response)
        self.inventory.save()

    def list_archives(self):
        archives = self.inventory.get_all_archives()
        return archives

    def get_by_arc_spec(self, arc_spec: str):
        archives = list()
        for arc in self.inventory.get_all_archives():
            if arc['ArchiveId'].startswith(arc_spec):
                archives.append(arc)
            if arc['ArchiveDescription'] == arc_spec:
                archives.append(arc)
        return archives
    
    def request_download(self, archive_id):
        response = self.client.initiate_job(
            vaultName=self.vault_name,
            jobParameters={
                'Type': 'archive-retrieval',
                'ArchiveId': archive_id,
                'Tier': 'Standard'  # Can also use 'Expedited' or 'Bulk'
            }
        )
        pprint(response)
        job_id = response['jobId']
        print(f"Retrieval job initiated. Job ID: {job_id}")

    def delete_archive(self, archive_id):
        r = self.client.delete_archive(
            vaultName = self.vault_name,
            archiveId = archive_id
        )

        self.inventory.add_deleted_file(archive_id)
        self.inventory.save()

    def download_job(self, job_id: str, stream: IO[bytes], update_fn = None):
        chunk_size = 1024 * 1024
        response = self.client.get_job_output(vaultName=self.vault_name, jobId=job_id)
        written = 0
        for chunk in response['body'].iter_chunks(chunk_size=chunk_size):
            written += stream.write(chunk)
            if update_fn:
                update_fn(written)

    def download_archive(self, archive_id: str, stream: IO[bytes]):
        print("download archive", archive_id)
        job = self.inventory.get_latest_job(action='ArchiveRetrieval', archive_id=archive_id)
        if not job or job['Completed'] != True or job['StatusCode'] != 'Succeeded':
            raise ArchiveNotRetrieved
        
        self.download_job(job_id=job['JobId'], stream=stream)




    def __repr__(self):
        return f'GlacierVault(vault_name={self.vault_name})'