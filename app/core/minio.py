import logging
from minio import Minio
from app.config import Config

logger = logging.getLogger(__name__)

def get_minio_client() -> Minio:
    """
    Get a MinIO client instance
    """
    logger.info("Create MinIO client instance.")
    return Minio(
        endpoint=Config.MINIO_URL,
        access_key=Config.MINIO_ACCESS_KEY,
        secret_key=Config.MINIO_SECRET_KEY,
        secure=False # Set to True if using HTTPS
    )

def init_minio():
    """
    Initialize MinIO by creating the bucket if it doesn't exist.
    """
    client = get_minio_client()
    logger.info(f"Checking if bucket {Config.BUCKET_NAME} exists.")
    found = client.bucket_exists(Config.BUCKET_NAME)
    if not found:
        logger.info(f"Bucket {Config.BUCKET_NAME} does not exist. Creating bucket")
        client.make_bucket(Config.BUCKET_NAME)
    else:
        logger.info(f"Bucket {Config.BUCKET_NAME} already exists.")



