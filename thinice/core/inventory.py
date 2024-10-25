import datetime
import json

from typing import Optional

from .utils import iso2dt
from .locations import Locations
from rich.pretty import pprint
from .utils import kmgt, iso2dt, get_element_by_field
from .exceptions import NoInventory

class Inventory():

    inventory: dict

    def __init__(self, locations: Locations, vault_name: str):
        self.locations = locations
        self.vault_name = vault_name
        self.path = locations.base_path / (vault_name + '.json')
        self.inventory = None

        if self.path.exists():
            self.load()

        # fix it anyway (in case of upgrade)
        self.fix_inventory()
    
    def fix_inventory(self):

        if self.inventory is None:
            self.inventory = dict()

        if not 'latest_inventory' in self.inventory:
            self.inventory["latest_inventory"] = dict()
            self.inventory["latest_inventory"]['ArchiveList'] = list()

        if not 'latest_jobs' in self.inventory:
            self.inventory["latest_jobs"] = dict()

        if not 'deleted_files' in self.inventory:
            self.inventory["deleted_files"] = list()

        if not 'uploaded_files' in self.inventory:
            self.inventory["uploaded_files"] = dict()

        # del self.inventory['submitted_jobs']

    def save(self):
        with open(self.path, 'w') as f:
            json.dump(self.inventory, f, indent=4)
    
    def load(self):
        with open(self.path, 'r') as f:
            self.inventory = json.load(f)

    def dump(self):
        pprint(self.inventory)


    """ INVENTORIES """

    def inventory_date(self) -> Optional[datetime.datetime]:
        """ return inventory date or None """
        try:
            return datetime.datetime.fromisoformat(self.inventory['latest_inventory']['InventoryDate'])
        except KeyError:
            return None

    def set_latest_inventory(self, inv: dict) -> bool: 
        if not self.inventory['latest_inventory']:
            self.inventory['latest_inventory'] = inv
            return

        try:
            cur_inv_date = iso2dt(self.inventory['latest_inventory']['InventoryDate'])
        except KeyError:
            cur_inv_date = None
        new_int_date = iso2dt(inv['InventoryDate'])

        if cur_inv_date is None or cur_inv_date < new_int_date:
            self.inventory['latest_inventory'] = inv
            return True
        else:
            # print(f"current inv from {cur_inv_date} is not older then {new_int_date}")
            return False

        # self.inventory['latest_inventory'] = response
    
    def get_latest_inventory(self):
        return self.inventory['latest_inventory']

    """ JOBS """

    def get_latest_job(self, job_id: str = None, action: str = None, archive_id: str = None):
        """ get latest submitted job of type action """

        latest_job = None
        latest_job_dt = None

        for job in self.inventory['latest_jobs']['JobList']:            
            if action and job['Action'] != action:
                continue

            if job_id and job['JobId'] != job_id:
                continue
            
            try:
                if archive_id and job['ArchiveId'] != archive_id:
                    continue
            except KeyError:
                continue

            jobdt = iso2dt(job['CreationDate'])            

            if latest_job is None or jobdt > latest_job_dt:
                latest_job = job
                latest_job_dt = jobdt
        
        return latest_job

    def set_latest_jobs(self, response: dict):
        self.inventory['latest_jobs'] = response

    """ UPLOADED FILES """

    def add_uploaded_file(self, archiveId: str, sha256: str, basename: str, description: str, size: int, localdesc: str = None):
        self.inventory['uploaded_files'][archiveId] = {
            'uploaded_at': datetime.datetime.now(tz=datetime.timezone.utc).isoformat(timespec='seconds'),
            'archiveId': archiveId,
            'sha256': sha256,
            'basename': basename,
            'description': description,
            'localdesc': localdesc,
            'size': size
        }

    """ DELETED FILES """
    def add_deleted_file(self, archiveId: str):
        self.inventory['deleted_files'].append(archiveId)

    """ GET INVENTORY """

    def get_all_archives(self):
        archives = list()
        
        for f in self.inventory['latest_inventory']['ArchiveList']:
            archive = self.get_archive_info(f['ArchiveId'])
            archives.append(archive)

        return archives
    

    def _from_arclist_by_id(self, archive_id: str):
        return next((item for item in self.inventory['latest_inventory']['ArchiveList'] if item['ArchiveId'] == archive_id), None)


    def get_archive_info(self, archive_id: str):
        utcnow = datetime.datetime.now(tz=datetime.timezone.utc)

        archive = self._from_arclist_by_id(archive_id)

        if archive:
            archive = dict(archive)

            archive['sz'] = kmgt(archive['Size'], frac=0)
            # default status
            archive['status'] = 'Cold'
            uploaded = iso2dt(archive['CreationDate'])
            archive['date'] = uploaded.strftime('%Y-%m-%d')
            archive['age'] = (utcnow - uploaded).days

            # check it deeper, maybe ongoing jobs?
            # deleted?
            if archive_id in self.inventory['deleted_files']:
                archive['status'] = 'Deleted'
            else:
                # maybe we warming it up?
                job = self.get_latest_job(action='ArchiveRetrieval', archive_id=archive['ArchiveId'])
                if job:
                    if job['Completed']:
                        archive['status'] = 'Warm'
                        archive['ArchiveRetrievalJob'] = job
                    else:
                        archive['status'] = 'Requested'

            return archive
        else:
            print(f"Archive {archive_id[:5]}... not found in inventory, update inventory with: thinice inventory")

    def __repr__(self):
        return f"Inventory({self.path})"
