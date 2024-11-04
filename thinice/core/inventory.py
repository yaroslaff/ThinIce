import datetime
import json
import os
from typing import Optional

from .utils import iso2dt
from .locations import Locations
from rich.pretty import pprint
from .utils import kmgt, iso2dt, get_element_by_field
from .exceptions import NoInventory, InventoryIsOlder, InventoryIsSame

class Inventory():

    inventory: dict

    def __init__(self, locations: Locations, vault_name: str, verbose: bool = False):
        self.verbose = verbose
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

        if not '_debug' in self.inventory:
            self.inventory['_debug'] = dict()

        if not 'ignore' in self.inventory['_debug']:
            self.inventory['_debug']['ignore'] = list()


        # del self.inventory['submitted_jobs']

    def save(self):
        with open(self.path, 'w') as f:
            json.dump(self.inventory, f, indent=4)
    
    def load(self):
        with open(self.path, 'r') as f:
            self.inventory = json.load(f)

    def dump(self):
        pprint(self.inventory)

    def is_ignored(self, hash: str):
        """ check if hash matches any prefixes in _debug ignore with any() """
        env_ignore = os.getenv('THINICE_IGN')
        
        if env_ignore:
            if any(hash.startswith(prefix) for prefix in env_ignore.split(' ')):
                # ignored by env
                return True

        return any(hash.startswith(prefix) for prefix in self.inventory['_debug']['ignore'])


    """ INVENTORIES """

    def inventory_date(self) -> Optional[datetime.datetime]:
        """ return inventory date or None """
        try:
            return iso2dt(self.inventory['latest_inventory']['InventoryDate'])
        except KeyError:
            return None

    def set_latest_inventory(self, inv: dict, jobid: None, force: bool = False) -> bool: 
        if not self.inventory['latest_inventory']:
            self.inventory['latest_inventory'] = inv
            return

        try:
            cur_inv_date = iso2dt(self.inventory['latest_inventory']['InventoryDate'])
        except KeyError:
            # No local inventory yet, accept
            self.inventory['latest_inventory'] = inv
            self.cleanup()
            return

        new_inv_date = iso2dt(inv['InventoryDate'])

        if cur_inv_date == new_inv_date and not force:
            raise InventoryIsSame(f'Do not accept inventory job {jobid[:5]}. Local inventory date: {cur_inv_date.strftime("%Y-%m-%d %H:%M:%S")}; Job inventory date: {new_inv_date.strftime("%Y-%m-%d %H:%M:%S")}')
            
        if cur_inv_date > new_inv_date:
            raise InventoryIsOlder(f'Do not accept inventory job {jobid[:5]}. Local inventory date: {cur_inv_date.strftime("%Y-%m-%d %H:%M:%S")}; Job inventory date: {new_inv_date.strftime("%Y-%m-%d %H:%M:%S")}')

        self.inventory['latest_inventory'] = inv
        self.cleanup()
        return True


        # self.inventory['latest_inventory'] = response
    
    def cleanup(self):
        inv_date = self.inventory_date()
        # remove from deleted files which are already deleted
        for aid in self.inventory['deleted_files']:
            if not self._from_arclist_by_id(aid):
                # forget about deleted archive
                if self.verbose:
                    print(f'Archive {aid} is not in the inventory anymore. Removing it from deleted files.')
                self.inventory['deleted_files'].remove(aid)
            else:
                if self.verbose:
                    print(f'Archive {aid} is still in the inventory. Keeping it in deleted files.')

        uploaded = list()
        lost = list()
        # remove from uploaded files
        for up_id, uparchive in self.inventory['uploaded_files'].items():
            if self._from_arclist_by_id(up_id):
                uploaded.append(up_id)
            else:
                up_date = iso2dt(uparchive['CreationDate'])
                age = inv_date - up_date
                if age.days > 2:
                    lost.append(up_id)
        
        for up_id in uploaded:
            del self.inventory['uploaded_files'][up_id]

        for up_id in lost:
            del self.inventory['uploaded_files'][up_id]




    def get_latest_inventory(self):
        return self.inventory['latest_inventory']

    """ JOBS """

    def get_latest_job(self, job_id: str = None, action: str = None, archive_id: str = None, completed=None):
        """ get latest submitted job of type action """

        latest_job = None
        latest_job_dt = None

        for job in self.inventory['latest_jobs']['JobList']:

            if completed is not None and job['Completed'] != completed:
                continue

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
            'CreationDate': datetime.datetime.now(tz=datetime.timezone.utc).isoformat(timespec='seconds'),
            'ArchiveId': archiveId,
            'sha256': sha256,
            'basename': basename,
            'ArchiveDescription': description,
            'localdesc': localdesc,
            'Size': size
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

        for f in self.inventory['uploaded_files']:
            archive = self.get_uploaded_archive_info(f)
            archives.append(archive)

        return archives
    

    def _from_arclist_by_id(self, archive_id: str):
        return next((item for item in self.inventory['latest_inventory']['ArchiveList'] if item['ArchiveId'] == archive_id), None)


    def get_uploaded_archive_info(self, archive_id: str):
        utcnow = datetime.datetime.now(tz=datetime.timezone.utc)
        archive = dict(self.inventory['uploaded_files'][archive_id])
        archive['sz'] = kmgt(archive['Size'], frac=0)
        uploaded = iso2dt(archive['CreationDate'])
        archive['date'] = uploaded.strftime('%Y-%m-%d')
        archive['age'] = (utcnow - uploaded).days
        archive['status'] = 'Uploaded'
        return archive

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
