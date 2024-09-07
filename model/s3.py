import boto3
import uuid
import os
import re
from dotenv import load_dotenv
load_dotenv()

S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION')
CLOUDFRONT_DOMAIN = os.getenv('CLOUDFRONT_DOMAIN')

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION
)

class S3:
    def upload(photo):
        photo_key = f"{uuid.uuid4()}.{photo.filename.split('.')[-1]}"
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=photo_key,
            Body=photo.file,
            ContentType=photo.content_type
        )
        photo_url = f"https://{CLOUDFRONT_DOMAIN}/{photo_key}"
        return photo_url
    
    def delete(photo_url):
        pattern = r'd34y008x9viy5l\.cloudfront\.net/(.*)'
        match = re.search(pattern, photo_url)
        
        
        if match:
            photo_key = match.group(1)  # 提取出 photo key
        else:
            return False

        s3_client.delete_object(
            Bucket=S3_BUCKET_NAME,
            Key=photo_key
        )
        return True