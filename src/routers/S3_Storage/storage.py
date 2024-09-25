from contextlib import asynccontextmanager
from aiobotocore.session import get_session
from fastapi import UploadFile, HTTPException
from starlette import status

from config import S3_ACCESS_KEY, S3_SECRET_KEY, S3_ENDPOINT_URL, S3_BUCKET_NAME


class S3Client:
    def __init__(
            self,
            access_key: str,
            secret_key: str,
            endpoint_url: str,
            bucket_name: str,
    ):
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
        }
        self.bucket_name = bucket_name
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def upload_file(
            self,
            file: UploadFile,
            file_name: str
    ):
        content = await file.read()
        try:
            async with self.get_client() as client:
                await client.put_object(
                    Bucket=self.bucket_name,
                    Key=f"{file_name}.png",
                    Body=content)
            return f"{self.config['endpoint_url']}/{self.bucket_name}/{file_name}.png"
        except Exception as expention:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f'{expention}')


async def get_s3_storage():
    s3_client = S3Client(access_key=S3_ACCESS_KEY,
                         secret_key=S3_SECRET_KEY,
                         endpoint_url=S3_ENDPOINT_URL,
                         bucket_name=S3_BUCKET_NAME)
    yield s3_client

async def main(image_name: str):
    s3_client = S3Client(access_key='W77TIK2WQC780GH1BSXU',
                         secret_key='NaSjxnG17Pmp8MOzCehNBUbs3puDqGpYcsSw5FLq',
                         endpoint_url='https://gmhost.space',
                         bucket_name='shop-bucket')
    await s3_client.upload_file(image_name)
    return f'{s3_client.config["endpoint_url"]}/{s3_client.bucket_name}/{image_name}'