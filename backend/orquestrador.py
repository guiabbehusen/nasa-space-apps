import asyncio
import schedule
import time
import logging
from datetime import datetime
from pymongo import MongoClient

from core.utils import calculate_aqi_from_pm25, get_aqi_category
from core.meteomatics import fetch_meteomatics
from services.rag_geo import gerar_json_via_slm, carregar_dados_csv, carregar_ou_criar_index, buscar_pontos_proximos
from services.relatorio import gerar_relatorio_amigavel, carregar_csv, carregar_txt
from email.mime.text import MIMEText
import smtplib
import os
import json

# ----------------------------------------
# CONFIGURAÇÕES
# ----------------------------------------
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://tempo11user:Us4UtOpZXsiR2VF0@cluster0.xj6qna.mongodb.net/retryWrites=true&w=majority")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "users")

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "dtrigoaraujo@gmail.com")
SMTP_PASS = os.getenv("SMTP_PASS", "jsyx iffa hucd bdab")

DATA_CSV = "./services/data/tempo.csv"
CHEM_EFFECTS_CSV = "./services/data/chemical_effects.csv"
AQI_ABOUT = "./services/data/about_aqi.txt"

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
        logger.error(f"❌ Erro ao enviar email para {dest}: {e}")


async def processar_usuario(usuario, df, index):
    """Processa um usuário: checa AQI e envia email se acima do limite."""
    lat = usuario.get("lat") or usuario.get("latitude")
    lon = usuario.get("lon") or usuario.get("longitude")
    profile = usuario.get("profile", "adulto")
    threshold = usuario.get("thresholds", {}).get("aqi", 100)
    email = usuario.get("email")

    if not lat or not lon or not email:
        logger.warning(f"Usuário inválido: {usuario}")
        return

    aqi_atual, categoria = await get_air_quality_data(lat, lon)
    if aqi_atual is None:
        return

    logger.info(f"{email}: AQI={aqi_atual} ({categoria})")

    if aqi_atual > threshold:
        df_resultado = buscar_pontos_proximos(lat, lon, index, df, k=10)
        json_final = gerar_json_via_slm(lat, lon, df_resultado)

        json_path = f"./services/data/resultado_{lat}_{lon}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(json_final)

        aqi_json = json.loads(json_final)
        chem_effects = carregar_csv(CHEM_EFFECTS_CSV)
        about_aqi_text = carregar_txt(AQI_ABOUT)

        relatorio_texto = gerar_relatorio_amigavel(aqi_atual, aqi_json, chem_effects, about_aqi_text, profile)
        enviar_email(email, f"⚠️ Alerta de Qualidade do Ar ({categoria})", relatorio_texto)


async def tarefa_diaria():
    """Executa a rotina completa — consulta todos os usuários e processa AQI."""
    logger.info("🚀 Iniciando rotina diária...")
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB_NAME]
        usuarios = list(db["subscriptions"].find({}))  # <-- agora busca todos
    except Exception as e:
        logger.error(f"Erro ao conectar ao MongoDB: {e}")
        return

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
    logger.info("⏰ Orquestrador agendado para 12:00 diariamente.")
    schedule.every().day.at("12:00").do(lambda: asyncio.create_task(tarefa_diaria()))

    while True:
        schedule.run_pending()
        await asyncio.sleep(30)


async def iniciar_orquestrador():
    """Inicia o orquestrador (para uso dentro do FastAPI)."""
    asyncio.create_task(agendar_tarefas())
    logger.info("🧠 Orquestrador iniciado em background.")


# ----------------------------------------
# MODO TESTE DIRETO
# ----------------------------------------
if __name__ == "__main__":
    print("🧩 Rodando orquestrador manualmente (modo teste)...")
    asyncio.run(tarefa_diaria())
