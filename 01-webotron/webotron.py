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

from pathlib import Path
import mimetypes
import boto3
from botocore.exceptions import ClientError
import click

# Session created using pythonAutomation credential
# Session created using us-east-1 as the region defined in AWS config
# us-east-1 is defined as the region in the pythonAutomation configuration file
session = boto3.Session(profile_name='pythonAutomation')

# Call the s3 resoruce within the session craeted above
s3 = session.resource('s3')

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
    for bucket in s3.buckets.all():
        print(bucket)


@cli.command('list_bucket_objects')
def list_bucket_objects(bucket):
    """List objects in a bucket"""
    for obj in s3.Bucket(bucket).objects.all():
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
    s3_bucket = None
    try:
        s3_bucket = s3.create_bucket(
            Bucket=bucket
        )
    # Create an exception that when ClientError is defined as 'e'
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            s3_bucket = s3.Bucket(bucket)
        else:
            raise e

    policy = """
    {
        "Version": "2012-10-17",
        "Statement": [{
        "Sid": "PublicReadGetObject",
        "Effect": "Allow",
        "Principal": "*",
        "Action": ["s3:GetObject"],
        "Resource": ["arn:aws:s3:::%s/*"]
        }
      ]
    }
    """ % s3_bucket.name
    policy = policy.strip()

    pol = s3_bucket.Policy()
    pol.put(Policy=policy)

    ws = s3_bucket.Website()
    ws.put(WebsiteConfiguration={
        'ErrorDocument': {
            'Key': 'error.html'
        },
        'IndexDocument': {
            'Suffix': 'index.html'
        }
    })

    return

# Uploads a file to S3
def upload_file(s3_bucket, path, key):
    content_type = mimetypes.guess_type(key)[0] or 'text/plain'

    s3_bucket.upload_file(
        path,
        key,
        ExtraArgs={
            'ContentType': content_type
        })


"""When the sync function is called, root will take the "pathname" argument and
 expand the full user context of the folder (C:/Users/Abhishek.Masabattula)
 then resolve it to show the full path name.
 expanduser method allows for the pathname with user context appear. This is
 expecially helpful if you define root as the current dir using PathLib's
 Path function. (i.e. root=Path(./kitten_web))

 This makes it possible to use "./kitten_web" as the pathname and still have
 the function resolve the full name of the directory"""


@cli.command('sync')
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucket')
def sync(pathname, bucket):
    """Sync contents of PATHNAME to BUCKET"""
    s3_bucket = s3.Bucket(bucket)
    root = Path(pathname).expanduser().resolve()

    def handle_directory(target):
        for p in target.iterdir():
            if p.is_dir():
                handle_directory(p)
            if p.is_file():
                upload_file(s3_bucket, str(p), str(p.relative_to(root)))

    handle_directory(root)


if __name__ == '__main__':
    cli()
