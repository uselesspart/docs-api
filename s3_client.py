import io
from datetime import datetime
from mimetypes import guess_type

import boto3
from botocore.config import Config as BotoConfig

from config import settings


class S3Client:
    def __init__(self):
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region,
            config=BotoConfig(signature_version="s3v4"),
        )
        self.bucket = settings.s3_bucket_name

    def upload_file(
        self,
        file_content: bytes,
        filename: str,
        folder: str = "generated",
        content_type: str | None = None,
        public: bool = True,
    ) -> dict:
        """
        Загружает файл в S3 и возвращает информацию о нём.

        Returns:
            {
                "key": "generated/2024/01/15/abc123_report.pdf",
                "url": "https://s3.twcstorage.ru/bucket/generated/...",
                "size": 1024,
                "content_type": "application/pdf"
            }
        """
        # Генерируем уникальный ключ с датой для организации
        now = datetime.utcnow()
        safe_filename = self._sanitize_filename(filename)
        key = f"{folder}/{now:%Y/%m/%d}/{safe_filename}"

        # Определяем content-type
        if not content_type:
            content_type, _ = guess_type(filename)
            content_type = content_type or "application/octet-stream"

        # Параметры загрузки
        extra_args = {"ContentType": content_type}
        if public:
            extra_args["ACL"] = "public-read"

        # Загружаем
        self._client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=file_content,
            **extra_args,
        )

        # Формируем публичный URL
        url = f"{settings.public_base_url}/{key}"

        return {
            "key": key,
            "url": url,
            "size": len(file_content),
            "content_type": content_type,
        }

    def upload_fileobj(
        self,
        file_obj: io.IOBase,
        filename: str,
        folder: str = "generated",
        content_type: str | None = None,
    ) -> dict:
        """Загружает файл-объект (стрим) в S3."""
        content = file_obj.read()
        return self.upload_file(content, filename, folder, content_type)

    def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """
        Генерирует временную подписанную ссылку.
        Полезно для приватных файлов.
        """
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in,
        )

    def delete_file(self, key: str) -> None:
        """Удаляет файл из S3."""
        self._client.delete_object(Bucket=self.bucket, Key=key)

    def file_exists(self, key: str) -> bool:
        """Проверяет наличие файла."""
        try:
            self._client.head_object(Bucket=self.bucket, Key=key)
            return True
        except self._client.exceptions.ClientError:
            return False

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Очистка имени файла от нежелательных символов."""
        import re
        filename = re.sub(r'[^\w\-_\.]', '_', filename)
        return filename[:100]  # ограничиваем длину


# Singleton
s3_client = S3Client()