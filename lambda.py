import json
import boto3
import os
from botocore.exceptions import ClientError

s3 = boto3.client('s3')
BUCKET = os.environ.get("S3_BUCKET", "")  # Environment variable

def object_exists(key):
    try:
        s3.head_object(Bucket=BUCKET, Key=key)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            return False
        raise

def lambda_handler(event, context):
    print("Received event:", event)
    print("Environment variables:", dict(os.environ))

    if not BUCKET:
        raise ValueError("S3_BUCKET environment variable not set")

    try:
        filename = None
        # Support both direct and agent formats
        if "parameters" in event and "filename" in event["parameters"]:
            filename = event["parameters"]["filename"]
        elif "fileName" in event:
            filename = event["fileName"]
        else:
            filename = "inlandmarine.json"

        print(f"Checking if file exists: {filename}")

        key_to_read = filename if object_exists(filename) else "Template.json"
        print(f"Reading file: {key_to_read}")

        response = s3.get_object(Bucket=BUCKET, Key=key_to_read)
        data = json.loads(response['Body'].read().decode('utf-8'))

        return {
            "statusCode": 200,
            "body": json.dumps(data)
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
