
from mypy_boto3_glacier import GlacierClient
from mypy_boto3_glacier.type_defs import ListJobsOutputTypeDef


from .credentials import AWSCredentials
import boto3

class GlacierVault:
    credentials: AWSCredentials
    client: GlacierClient
    vault_name: str
    
    def __init__(self, credentials: AWSCredentials, vault_name: str | None = None):
        self.credentials = credentials
        self.vault_name = vault_name
        self.client = boto3.client(
            'glacier',
            aws_access_key_id=credentials.key_id,
            aws_secret_access_key=credentials.secret_key
        )
        # self.resource = boto3.resource('glacier')
        #self.client = boto3.client('glacier')
        #self.vault = self.resource.Vault('-',self.vaultName)


    def list_vaults(self):
        response = self.client.list_vaults()
        # return [vault['VaultName'] for vault in response['VaultList']]
        return response['VaultList']
    
    def list_jobs(self) -> ListJobsOutputTypeDef:
        response = self.client.list_jobs(vaultName=self.vault_name)
        print(type(response))
        print(response)
        print(type(response['JobList']))        
        return response['JobList']

    def __repr__(self):
        return f'GlacierVault(vault_name={self.vault_name})'