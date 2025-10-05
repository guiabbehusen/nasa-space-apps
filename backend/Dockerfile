# Etapa 1: Escolher a imagem base
FROM python:3.9-slim



# Etapa 3: Copiar arquivos de dependências e instalar
COPY requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get remove -y build-essential && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# Etapa 4: Copiar o restante do código da aplicação
COPY . .

# Etapa 5: Copiar o arquivo .env (opcional — geralmente melhor montá-lo em tempo de execução)
# COPY .env .env

# Etapa 6: Variáveis de ambiente padrão
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Etapa 7: Definir comando padrão
CMD ["python", "main.py"]
