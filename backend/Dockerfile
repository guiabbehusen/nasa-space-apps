# ============================================================
# 🐍 Etapa 1: Imagem base leve com Python
# ============================================================
FROM python:3.11-slim

# Criar diretório da aplicação
WORKDIR /app

# ============================================================
# 📦 Etapa 2: Instalar dependências
# ============================================================
COPY requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get remove -y build-essential && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# ============================================================
# 📂 Etapa 3: Copiar o código do backend (com estrutura modular)
# ============================================================
COPY . .

# ============================================================
# ⚙️ Etapa 4: Variáveis de ambiente
# ============================================================
# Impede criação de bytecode .pyc e ativa flush de logs imediatos
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Porta padrão do FastAPI/Uvicorn
ENV PORT=8000

# ============================================================
# 🚀 Etapa 5: Comando de inicialização
# ============================================================
# Usa Uvicorn para rodar FastAPI (mais robusto em containers)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
