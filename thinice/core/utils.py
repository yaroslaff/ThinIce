import datetime
from mypy_boto3_glacier import GlacierClient
import hashlib
from rich.pretty import pprint


def response2dt(response: dict):
    dt_fmt = "%a, %d %b %Y %H:%M:%S %Z"
    return datetime.datetime.strptime(response['ResponseMetadata']['HTTPHeaders']['date'], dt_fmt)

def iso2dt(isotime: str):
    """ convert ISO 8601 time like 2024-10-21T18:42:57.175Z or 1970-01-01T00:00:00Z or 2024-10-26 11:42:22.231Z to datetime """
    """
    """

    try:
        # 2024-10-25T20:42:20+00:00
        return datetime.datetime.fromisoformat(isotime)
    except ValueError:
        pass
    
    
    if ' ' in isotime:
        # 2024-10-26 11:42:22.231Z
        dt_fmt = "%Y-%m-%d %H:%M:%S.%fZ"
    elif '.' in isotime:
        # 2024-10-21T18:42:57.175Z
        dt_fmt = "%Y-%m-%dT%H:%M:%S.%fZ"
    else:
        # 1970-01-01T00:00:00Z
        dt_fmt = "%Y-%m-%dT%H:%M:%SZ"
    

    return datetime.datetime.strptime(isotime, dt_fmt).replace(tzinfo=datetime.timezone.utc)


def td2str(tdelta: datetime.timedelta):
    total_seconds = int(tdelta.total_seconds())
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    if days:
        return f"{days}d {hours:02}:{minutes:02}:{seconds:02}"
    else:
        return f"{hours:02}:{minutes:02}:{seconds:02}"

def get_element_by_field(lst, field, value):
    print("get by", field, value)
    pprint(lst[0])

    print(next((item for item in lst if item.get(field) == value), None))


    return next((item for item in lst if item.get(field) == value), None)

def calculate_sha256(stream):
    # Rewind the file to the beginning
    stream.seek(0)
    
    # Create a SHA-256 hash object
    sha256_hash = hashlib.sha256()

    # Read and update the hash in chunks to avoid memory issues with large files
    for chunk in iter(lambda: stream.read(4096), b""):
        sha256_hash.update(chunk)

    # Rewind the file to the beginning after processing
    stream.seek(0)
    
    # Return the hex representation of the hash
    return sha256_hash.hexdigest()

def kmgt(sz, frac=1):
    t={
        'K': pow(1024, 1),
        'M': pow(1024, 2),
        'G': pow(1024, 3),
        'T': pow(1024, 4),
        '': 1}

    for k in sorted(t,key=t.__getitem__,reverse=True):
        fmul = pow(10,frac)

        if sz>=t[k]:
            n = sz/float(t[k])

            tpl = "{:."+str(frac)+"f}{}"

            return tpl.format(n,k)

def from_kmgt(x: str) -> int:
    t={
        'K': pow(1024, 1),
        'M': pow(1024, 2),
        'G': pow(1024, 3),
        'T': pow(1024, 4),
        '': 1}

    suffix = x[len(x)-1].upper()
    if suffix in t:
        return int(x[0:(len(x)-1)]) * t[suffix]
    return int(x)

class UnusedGlacierJobIterator:
    def __init__(self, vault_name: str, client: GlacierClient):
        self.vault_name = vault_name
        self.client = client
        self.marker = None
        self.jobs = None
        self.current_index = 0
        self.limit = 100

    def _fetch_jobs(self) -> bool:
        """ Fetch jobs and update the jobs list, if False - stop iteration """
        try:
            if self.jobs is None:
                # first time call, no jobs yet
                response = self.client.list_jobs(
                    vaultName=self.vault_name, 
                    limit=str(self.limit)
                    )
                
                if len(response['JobList']) == 0:
                    return False

            else:
                if self.marker is None:
                    return False

                response = self.client.list_jobs(
                    vaultName=self.vault_name, 
                    marker=self.marker,
                    limit=str(self.limit)
                    )
                
            self.current_index = 0
            self.jobs = response['JobList']
            # Update marker for the next call
            self.marker = response.get('Marker')
            return True
        except Exception as e:
            raise RuntimeError(f"Error fetching jobs: {e}")



    def __iter__(self):
        return self

    def __next__(self):
        if self.jobs is None or self.current_index >= len(self.jobs):        
            # Fetch more jobs if the current list is exhausted
            if not self._fetch_jobs():
                raise StopIteration

        # Get the next job
        job = self.jobs[self.current_index]
        self.current_index += 1
        return job
