# ThinIce - friendly client for Amazon Glacier 

## Install
~~~shell
pipx install thinice
~~~
or (recommended: in virtualenv):
~~~shell
pip3 install thinice
~~~

## Configuration
Write `.env` config file, example:
~~~
AWS_ACCESS_KEY_ID = AK...
AWS_SECRET_ACCESS_KEY = FN...
AWS_REGION = eu-south-1
AWS_GLACIER_VAULT = mytest
~~~

Or you can supply this via options: `--key-id`, `--secret-key`, `--region` and `--vault`.

## Basic commands
### Inventory
First, you need to initialize local inventory:
~~~shell
# request inventory
thinice inventory

# watch when job complete (will take few hours)
thinice job

# now accept inventory with same command
thinice inventory

# now you can list files
thinice ls
~~~

### Upload
Thinice support multipart uploads and can upload very large files
~~~shell
# No description explicitly given, description will be myarchive.zip
thinice upload /path/to/myarchive.zip

# No description explicitly given, description will be myarchive.zip
thinice upload /path/to/myarchive.zip "My archive from 01/02/2003"
~~~

### Download
~~~shell
# To download, we should *warm* file, transit it from cold to warm storage
thinice request myarchive.zip

# or by first part of ArchiveId
thinice request S39to

# watch it in list to become warm (will take few hours)
thinice ls

# and finally download it
# file with this description MyServer.tar.gz will be saved as MyServer.tar.gz (only if description is a filename)
thinice download myarchive.zip

# download file with ArchiveId starting with this characters
thinice download S39to myarchive.zip
~~~

### Delete
~~~shell
# delete archive with this ArchiveId
thinice delete S39to

# delete all archives with this ArchiveDescription
thinice delete myarchive.zip
~~~

### Other commands
~~~shell
# help
thinice -h
thinice download -h

# list vaults
thinice vaults

# list jobs
thinice jobs
~~~
