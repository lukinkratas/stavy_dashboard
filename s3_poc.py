import boto3
import pandas as pd
import io
from dotenv import load_dotenv

load_dotenv()

S3_PATH = r's3://stavy/data.csv'

# Initialize S3 client
s3_client = boto3.client('s3')

# Parse S3 path
bucket_name = S3_PATH.split('/')[2]
key = '/'.join(S3_PATH.split('/')[3:])

try:
    # Get object from S3
    response = s3_client.get_object(Bucket=bucket_name, Key=key)
    
    # Read the CSV data from the response
    csv_content = response['Body'].read().decode('utf-8')
    df = pd.read_csv(io.StringIO(csv_content))
    
    print(f"Successfully read CSV from S3. Shape: {df.shape}")

    print(f"{df=}")
    
except Exception as e:
    print(f"Error reading CSV from S3: {str(e)}")
