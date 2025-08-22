# Use uma imagem oficial do Python como base
FROM python:3.12-slim-bookworm

# Defina o diretório de trabalho dentro do container
WORKDIR /app

# Copie o arquivo requirements.txt para o diretório de trabalho
COPY requirements.txt .

# Instale as dependências Python
RUN pip install --no-cache-dir -r requirements.txt django-cors-headers


# Copie todo o código da aplicação para o diretório de trabalho
COPY . .

# Coletar arquivos estáticos (para Nginx servir)
RUN python manage.py collectstatic --noinput

# Expor a porta que o Gunicorn/Uvicorn irá usar
EXPOSE 8000

# Comando para rodar a aplicação Gunicorn em produção
# Adapte 'membertruck_api.wsgi' para o seu módulo WSGI real
# Use 4 workers e bind para 0.0.0.0:8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "membertruck_api.wsgi:application"]
