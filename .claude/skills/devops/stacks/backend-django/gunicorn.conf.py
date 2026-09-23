"""docker/gunicorn.conf.py — valores por env, defaults seguros para VPS pequena."""

import multiprocessing
import os

bind = "0.0.0.0:8000"
workers = int(os.getenv("GUNICORN_WORKERS", min(multiprocessing.cpu_count() * 2 + 1, 5)))
threads = int(os.getenv("GUNICORN_THREADS", 2))
worker_class = os.getenv("GUNICORN_WORKER_CLASS", "gthread")

# Request não segura trabalho longo (BE-02 manda para fila). 30s é teto, não meta.
timeout = int(os.getenv("GUNICORN_TIMEOUT", 30))
graceful_timeout = 20
keepalive = 5

# Recicla worker para conter vazamento de memória
max_requests = 1000
max_requests_jitter = 100

# Logs em stdout; acesso já aparece no Traefik → access log desligado aqui
accesslog = None
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info").lower()

# Atrás do Traefik (rede interna do Easypanel)
forwarded_allow_ips = "*"

# gunicorn >= 26 abre um socket de controle no cwd (/app/.gunicorn/), que é do
# root na imagem — o processo roda como `app` e loga "Permission denied" a cada
# boot. Apontar para um diretório gravável mantém /app somente leitura.
control_socket = os.getenv("GUNICORN_CONTROL_SOCKET", "/tmp/gunicorn.ctl")
