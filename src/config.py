from dotenv import load_dotenv
import os

load_dotenv()


DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')

JWT_SECRET_TOKEN = os.getenv('JWT_SECRET_TOKEN')
ADMIN_SECRET = os.getenv('ADMIN_SECRET')


EMAIL_ADRESS = os.getenv('EMAIL_ADRESS')
EMAIL_PASS = os.getenv('EMAIL_PASS')


S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY')
S3_SECRET_KEY = os.getenv('S3_SECRET_KEY')
S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')