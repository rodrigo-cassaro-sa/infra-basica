# Storage de arquivos — MinIO/S3 (dono: BE-05)

Arquivo nunca fica no filesystem do container (efêmero no Easypanel). Tudo vai para
MinIO (self-hosted) ou S3, atrás de um port do core. Um único model `FileAsset` para o
projeto inteiro — upload do app, importação (BE-03), documentos de RAG (BE-04).

## Port (no core) e adapter (aqui)

```python
# apps/files/ports.py (core)
from typing import Protocol


class FileStorage(Protocol):
    def presign_upload(self, *, key: str, content_type: str, max_bytes: int, expires_s: int = 300) -> dict: ...
    def presign_download(self, *, key: str, filename: str, expires_s: int = 300) -> str: ...
    def head(self, *, key: str) -> dict | None: ...          # size, content_type, etag
    def delete(self, *, key: str) -> None: ...
```

```python
# apps/integrations/storage/adapter.py
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, EndpointConnectionError
from django.conf import settings

from apps.integrations.base.exceptions import IntegrationUnavailable, IntegrationValidationError


class S3FileStorage:
    """Implementa FileStorage. MinIO e S3 usam a mesma API."""

    def __init__(self) -> None:
        self.bucket = settings.STORAGE_BUCKET
        self.s3 = boto3.client(
            "s3",
            endpoint_url=settings.STORAGE_ENDPOINT_URL,       # MinIO: https://minio.seudominio
            aws_access_key_id=settings.STORAGE_ACCESS_KEY,
            aws_secret_access_key=settings.STORAGE_SECRET_KEY,
            region_name=settings.STORAGE_REGION,
            config=Config(signature_version="s3v4", connect_timeout=3, read_timeout=10, retries={"max_attempts": 1}),
        )

    def presign_upload(self, *, key, content_type, max_bytes, expires_s=300):
        try:
            return self.s3.generate_presigned_post(
                self.bucket, key,
                Fields={"Content-Type": content_type},
                Conditions=[{"Content-Type": content_type}, ["content-length-range", 1, max_bytes]],
                ExpiresIn=expires_s,
            )
        except EndpointConnectionError as exc:
            raise IntegrationUnavailable(str(exc), provider="storage", operation="presign_upload") from exc

    def presign_download(self, *, key, filename, expires_s=300):
        return self.s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key,
                    "ResponseContentDisposition": f'attachment; filename="{filename}"'},
            ExpiresIn=expires_s,
        )

    def head(self, *, key):
        try:
            r = self.s3.head_object(Bucket=self.bucket, Key=key)
        except ClientError as exc:
            if exc.response["Error"]["Code"] in {"404", "NoSuchKey"}:
                return None
            raise IntegrationValidationError(str(exc), provider="storage", operation="head") from exc
        return {"size": r["ContentLength"], "content_type": r["ContentType"], "etag": r["ETag"]}

    def delete(self, *, key):
        self.s3.delete_object(Bucket=self.bucket, Key=key)
```

`settings.PORTS["file_storage"] = "apps.integrations.storage.adapter.S3FileStorage"`.

## FileAsset (core, app `files`)

```python
class FileAsset(TenantModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Aguardando upload"
        READY = "ready", "Disponível"
        REJECTED = "rejected", "Rejeitado"

    key = models.CharField(max_length=300, unique=True)          # tenants/<id>/<uuid>
    original_name = models.CharField(max_length=255)             # só metadado, nunca path
    content_type = models.CharField(max_length=100)
    size = models.PositiveBigIntegerField(null=True, blank=True)
    purpose = models.CharField(max_length=40)                    # "avatar", "import", "rag_doc"
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
```

## Fluxo de upload do Expo (direto no storage, sem passar pelo Django)

```text
1. POST /api/v1/files/          {name, content_type, size, purpose}
   → service file_upload_start: valida tipo/tamanho por purpose, cria FileAsset(pending),
     devolve {id, upload: {url, fields}}  (presigned POST, 5 min)
2. App envia o arquivo direto para o MinIO com os fields.
3. POST /api/v1/files/{id}/complete/
   → service file_upload_complete: head() no storage, confere tamanho/tipo → READY ou REJECTED
4. Quem usa o arquivo recebe file_id (import job, avatar, documento de RAG).
```

Download: `GET /api/v1/files/{id}/download/` → selector checa visibilidade (tenant) →
302 para URL pré-assinada de 5 min. URL difícil de adivinhar não é permissão.

## Regras

- Chave gerada pelo backend (`tenants/<tenant_id>/<uuid4>`); nome original só como metadado.
- Tipos e tamanhos permitidos por `purpose`, validados no service (e reforçados pela condição do presign).
- Verificação de conteúdo real (magic bytes) na task que processa o arquivo, antes de usar.
- Bucket privado. Nada de `public-read`.
- Arquivo `pending` há mais de 24h → limpeza por tarefa periódica (BE-03).
- Credenciais do MinIO só em env; nunca no app.
