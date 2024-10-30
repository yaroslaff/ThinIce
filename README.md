# ThinIce - friendly client for Amazon Glacier

Thinice is a user-friendly client for AWS Glacier that features a local inventory. This local inventory allows you to instantly list uploaded archives, as retrieving inventory from Glacier can take several hours.

With the local inventory, you can quickly list archives by filename (ArchiveDescription), size, and upload age.

## Install
[pipx](https://github.com/pypa/pipx) method is recommended (pipx is easy to install).
~~~shell
pipx install thinice
~~~
or (better if in virtualenv):
~~~shell
pip3 install thinice
~~~

## Configuration
Create the config directory using the command `mkdir ~/.config/thinice`, and then create the config file at `~/.config/thinice/thinice.env`. Here’s an example:

~~~
AWS_ACCESS_KEY_ID = AK...
AWS_SECRET_ACCESS_KEY = FN...
AWS_REGION = eu-south-1
AWS_GLACIER_VAULT = mytest
~~~

Alternatively, you can supply this information via options: `--key-id`, `--secret-key`, `--region`, and `--vault`.

## Basic commands
### Inventory
First, you need to initialize the local inventory:
~~~shell
# Request inventory
thinice inventory

# Monitor when the job is complete (this may take a few hours)
thinice job

# Accept the inventory with the same command
thinice inventory

# Now you can list files
thinice ls
~~~

### Upload
Thinice supports multipart uploads and can handle upload of very large files

~~~shell
# No description explicitly given, description will be myarchive.zip
thinice upload /path/to/myarchive.zip

# Upload with description
thinice upload /path/to/myarchive.zip "My archive from 01/02/2003"
~~~

### Download
~~~shell
# To download, we should *warm* the file by transitioning it from cold to warm storage
# Here we use expedited retrieval tier to get file very fast.
thinice request myarchive.zip -t expedited

# Or by the first part of the ArchiveId (default: standard tier)
thinice request S39to

# Monitor the list to see when it becomes warm (this will take a few hours)
thinice ls


# Finally, download it
# A file with the description MyServer.tar.gz will be saved as MyServer.tar.gz (only if the description is a filename)
thinice download myarchive.zip

# Download a file with an ArchiveId starting with these characters
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
