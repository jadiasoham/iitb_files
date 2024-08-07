from minio import Minio
from django.conf import settings
from DjangoMinio.settings import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_SECURE

def get_minio_client():
    client = Minio(
        settings.MINIO_ENDPOINT,
        access_key= MINIO_ACCESS_KEY,
        secret_key= MINIO_SECRET_KEY,
        secure= MINIO_SECURE
    )
    return client