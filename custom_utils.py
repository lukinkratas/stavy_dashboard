import boto3
import io
from dotenv import load_dotenv
import pandas as pd
import s3fs

load_dotenv()
s3_client = boto3.client('s3')
s3_filesystem = s3fs.S3FileSystem()
BUCKET_NAME = 'stavy'

def list_s3_csvs():

    # Get object from S3
    response = s3_client.list_objects_v2(
        Bucket=BUCKET_NAME,
        MaxKeys=1,
    )
    
    contents = response['Contents']
    return [content['Key'] for content in contents if content['Key']]

def fetch_csv(filename):

    # Get object from S3
    response = s3_client.get_object(
        Bucket=BUCKET_NAME,
        Key=filename
    )
    
    # Read the CSV data from the response
    csv_bytes = response['Body'].read().decode('utf-8')
    return pd.read_csv(io.StringIO(csv_bytes))

def transform_df(df):
    df['datum'] = pd.to_datetime(df['datum'])
    return df

def write_csv(df, filename):

    with s3_filesystem.open(f'{BUCKET_NAME}/{filename}', 'w') as s3_file:
        df.to_csv(s3_file, header=True, index=False)

def append_to_csv(appends_df, filename):

    with s3_filesystem.open(f'{BUCKET_NAME}/{filename}', 'a') as s3_file:
        appends_df.to_csv(s3_file, header=False, index=False)