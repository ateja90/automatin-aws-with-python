# -*- coding: UTF-8 -*-
import mimetypes
from pathlib import Path
import boto3
from botocore.exceptions import ClientError

""" Classes of S3 Buckets"""

# Helps organize data and code together


class BucketManager:
    """Manage an S3 bucket"""
    # BucketManager object is created and initialized/contructed using fxn
    # "__init__" below
    def __init__(self, session):
        """Create a bucketmanager object"""
        self.s3 = session.resource('s3')

    def all_buckets(self):
        """ Get an iterator for all buckets"""
        return self.s3.buckets.all()

    def all_objects(self, bucket_name):
        """ Get an iterator for all objects in a bucket"""
        return self.s3.Bucket(bucket_name).objects.all()

    def init_bucket(self, bucket_name):
        """Create a new bucket"""
        s3_bucket = None
        try:
            s3_bucket = self.s3.create_bucket(
                Bucket=bucket_name
            )
        # Create an exception that when ClientError is defined as 'e'
        # If bucket already exists, s3_bucket variable will be set to the
        # bucket name
        except ClientError as error:
            if error.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                s3_bucket = self.s3.Bucket(bucket_name)
            else:
                raise error
        return s3_bucket

    def set_policy(self, bucket):
        """ Set policy for a new bucket to be readable by anyone"""
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
        """ % bucket.name

        policy = policy.strip()

        pol = bucket.Policy()
        pol.put(Policy=policy)

    def config_s3website(self, bucket):
        """Configure bucket to be a website"""
        bucket.Website().put(WebsiteConfiguration={
            'ErrorDocument': {
                'Key': 'error.html'
            },
            'IndexDocument': {
                'Suffix': 'index.html'
            }
        })

    @staticmethod
    def upload_file(bucket, path, key):
        """Upload path to S3_bucket at key"""
        content_type = mimetypes.guess_type(key)[0] or 'text/plain'

        return bucket.upload_file(
            path,
            key,
            ExtraArgs={
                'ContentType': content_type
            })

    def sync_bucket(self, pathname, bucket_name):
        bucket = self.s3.Bucket(bucket_name)
        root = Path(pathname).expanduser().resolve()

        def handle_directory(target):
            for p in target.iterdir():
                if p.is_dir():
                    handle_directory(p)
                if p.is_file():
                    self.upload_file(bucket, str(p), str(p.relative_to(root)))

        handle_directory(root)
