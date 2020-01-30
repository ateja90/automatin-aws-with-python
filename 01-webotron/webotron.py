#!/user/bin/python
# -*- coding: UTF-8 -*-

"""
    Webotron automates the process of deploying static websites to AWS
    - Configure AWS S3 buckets
        - Create them
        - Set them up for static website hosting
        - Deploy local files
    - Configure DNS with AWS Route 53
    - Configure a content delivery network with SSL and CloudFront
"""

import boto3
import click
from bucket import BucketManager

# Session created using pythonAutomation credential
# Session created using us-east-1 as the region defined in AWS config
# us-east-1 is defined as the region in the pythonAutomation configuration file
session = boto3.Session(profile_name='pythonAutomation')
bucket_manager = BucketManager(session)

# Define a click group called 'cli' to be used by the functions below
# click.group is the same as click.command,
# except the command class (cls) is set to "Group"
@click.group()
def cli():
    """Webotron deploys websites to AWS"""
    pass


# the @cli will transfer the command to the cli group above.
# If you don't give the click command a name (in green text),
# it will get the name of the function being called
@cli.command('list_buckets')
def list_buckets():
    """List all s3 buckets"""
    for bucket in bucket_manager.all_buckets():
        print(bucket)


@cli.command('list_bucket_objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    """List objects in a bucket"""
    for obj in bucket_manager.all_objects(bucket):
        print(obj)


# Creating a click argument creates a parameter for the function.
# You do not need to specify the parameter
# when calling the function, just have to mention the arguments in the order
# that they appear
# Example below shows creating an argument called "bucket" to be used a
# parameter in the function below
@cli.command('setup_bucket')
@click.argument('bucket')
def setup_bucket(bucket):
    """Create and configure S3 bucket"""
    s3_bucket = bucket_manager.init_bucket(bucket)
    bucket_manager.set_policy(s3_bucket)
    bucket_manager.config_s3website(s3_bucket)
    return


"""When the sync function is called, root will take the "pathname" argument and
 expand the full user context of the folder (C:/Users/Abhishek.Masabattula)
 then resolve it to show the full path name.
 expanduser method allows for the pathname with user context appear. This is
 expecially helpful if you define root as the current dir using PathLib's
 Path function. (i.e. root=Path(./kitten_web))

 This makes it possible to use "./kitten_web" as the pathname and still have
 the function resolve the full name of the directory"""


@cli.command('sync_bucket')
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucket')
def sync_bucket(pathname, bucket):
    """Sync contents of PATHNAME to BUCKET"""
    bucket_manager.sync_bucket(pathname, bucket)


# __main__ is the script in this file
if __name__ == '__main__':
    cli()
