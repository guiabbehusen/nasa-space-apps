import asyncio
import schedule
import time
import logging
from datetime import datetime
from pymongo import MongoClient

from core.utils import calculate_aqi_from_pm25, get_aqi_category
from core.meteomatics import fetch_meteomatics
from rag_geo import gerar_json_via_slm, carregar_dados_csv, carregar_ou_criar_index, buscar_pontos_proximos
from relatorio import gerar_relatorio_amigavel, carregar_json, carregar_csv, carregar_txt
from email.mime.text import MIMEText
import smtplib
import os
import json

# ----------------------------------------
# CONFIGURAÇÕES
# ----------------------------------------
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "air_monitor")

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "seu_email@gmail.com")
SMTP_PASS = os.getenv("SMTP_PASS", "sua_senha")

DATA_CSV = "./data/tempo.csv"
CHEM_EFFECTS_CSV = "./data/chemical_effects.csv"
AQI_ABOUT = "./data/about_aqi.txt"

logger = logging.getLogger("air-orchestrator")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# ----------------------------------------
# FUNÇÕES AUXILIARES
# ----------------------------------------
async def get_air_quality_data(lat, lon):
    """Consulta a API e retorna AQI e categoria."""
    params = ["pm2p5:ugm3"]
    try:
        data = await fetch_meteomatics(params, lat, lon, hours=1)
        pm25 = data["data"][0]["coordinates"][0]["dates"][0]["value"]
        aqi = calculate_aqi_from_pm25(pm25)
        categoria = get_aqi_category(aqi)
        return aqi, categoria
    except Exception as e:
        logger.error(f"Erro ao buscar dados do ar ({lat},{lon}): {e}")
        return None, "Erro"


def enviar_email(dest, assunto, corpo):
    """Envia e-mail com o relatório."""
    msg = MIMEText(corpo, "plain", "utf-8")
    msg["Subject"] = assunto
    msg["From"] = SMTP_USER
    msg["To"] = dest
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        logger.info(f"✅ Email enviado para {dest}")
    except Exception as e:
        logger.error(f"Erro ao enviar email para {dest}: {e}")


async def processar_usuario(usuario, df, index):
    """Processa 1 usuário: checa AQI e envia email se acima do limite."""
    lat, lon = usuario["latitude"], usuario["longitude"]
    profile = usuario.get("profile", "adulto")
    threshold = usuario.get("aqi_threshold", 100)
    email = usuario["email"]

    aqi_atual, categoria = await get_air_quality_data(lat, lon)
    if aqi_atual is None:
        return

    logger.info(f"{email}: AQI={aqi_atual} ({categoria})")

    if aqi_atual > threshold:
        df_resultado = buscar_pontos_proximos(lat, lon, index, df, k=10)
        json_final = gerar_json_via_slm(lat, lon, df_resultado)

        json_path = f"./data/resultado_{lat}_{lon}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(json_final)

        aqi_json = json.loads(json_final)
        chem_effects = carregar_csv(CHEM_EFFECTS_CSV)
        about_aqi_text = carregar_txt(AQI_ABOUT)

        relatorio_texto = gerar_relatorio_amigavel(aqi_atual, aqi_json, chem_effects, about_aqi_text, profile)

        enviar_email(email, f"⚠️ Alerta de Qualidade do Ar ({categoria})", relatorio_texto)


async def tarefa_diaria():
    """Executa a rotina completa — pode ser chamada direto."""
    logger.info("🚀 Iniciando rotina diária...")
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    usuarios = list(db["users"].find({}))
    logger.info(f"Total de usuários encontrados: {len(usuarios)}")

    if not usuarios:
        logger.warning("Nenhum usuário encontrado.")
        return

    df = carregar_dados_csv()
    index = carregar_ou_criar_index(df)
    tasks = [processar_usuario(u, df, index) for u in usuarios]
    await asyncio.gather(*tasks)

    logger.info("🏁 Rotina concluída com sucesso!")


async def agendar_tarefas():
    """Agenda execução diária (12:00)."""
    schedule.every().day.at("12:00").do(lambda: asyncio.create_task(tarefa_diaria()))
    logger.info("⏰ Orquestrador agendado para 12:00 diariamente.")
    while True:
        schedule.run_pending()
        await asyncio.sleep(30)


async def iniciar_orquestrador():
    """Inicia o orquestrador (para usar dentro do FastAPI)."""
    asyncio.create_task(agendar_tarefas())
    logger.info("🧠 Orquestrador iniciado em background.")

# ----------------------------------------
# MODO TESTE DIRETO
# ----------------------------------------
if __name__ == "__main__":
    print("🧩 Rodando orquestrador manualmente (modo teste)...")
    asyncio.run(tarefa_diaria())
