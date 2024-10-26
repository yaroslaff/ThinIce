# ThinIce - friendly client for Amazon Glacier 

## Understanding the difference: Amazon S3 Glacier vs. Amazon S3 Glacier Deep Archive 
These are two different services (though both offer low-cost storage).

|                                          | Glacier            | Glacier deep archive | 
| ---                                      | ---                | ---                  | 
| Launched                                 | 2012               | 2018                 |
| Storage cost (USD/GB/mo)                 | $0.004             | $0.00099             |
| Retrieval cost (Gb) and time (Expedited) | **$0.036, 1-5min** | Not available        |
| Retrieval cost/time (Standard)           | $0.012, 3-5h       | $0.0018 (12h)          |
| Retrieval cost/time (Bulk)               | $0, 5-12h          | $0.0025 (48h)        |

> Note: Prices depend on the region and can change over time, and they may not always be very clear. For current pricing, see: https://aws.amazon.com/s3/glacier/pricing/, https://aws.amazon.com/s3/pricing/, and https://docs.aws.amazon.com/AmazonS3/latest/userguide/restoring-objects-retrieval-options.html.


While Glacier Deep Archive is four times cheaper for storage, Glacier offers Expedited retrieval, which is not very expensive. When needed, you can recover files almost as quickly as if they were on your local disk (compared to 12 hours with Deep Archive). This difference can be crucial in business cases. Additionally, Standard and Bulk retrieval options are available at a lower cost.

For each 1 TB of archives it costs just $4 per month for Glacier (compared to $1 per month for Deep Archive). You spend an extra $3 per month for peace of mind, knowing you can recover files in a few minutes.

ThinIce works with Glacier but not with Glacier Deep Archive. For the latter, consider using tools like [s3cmd](https://github.com/s3tools/s3cmd) or [s4cmd](https://github.com/bloomreach/s4cmd).

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
