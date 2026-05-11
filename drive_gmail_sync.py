"""
drive_gmail_sync.py
-------------------
Script responsável por:
1️⃣ Autenticar com Gmail e Google Drive via OAuth 2.0
2️⃣ Buscar e-mails com anexos de fatura (ex: Nubank)
3️⃣ Fazer download dos anexos PDF
4️⃣ Enviar automaticamente os PDFs para uma pasta do Google Drive

Requisitos:
- credentials.json (baixado do Google Cloud Console)
- token.json (gerado automaticamente após o primeiro login)
"""

import pandas as pd
import src.models
from src.normalize import title_normalize
import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from dotenv import load_dotenv
from src.utils import load_transactions

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/drive.file",
]

# ID da pasta do Google Drive onde as faturas serão salvas
# 👉 Cole aqui o ID da pasta do Drive (ex: "1A2B3C4D5E6F7G8H9")
PASTA_DRIVE_ID = os.environ.get("PASTA_DRIVE_ID")


# ============================================================
# ⚙️ Função de autenticação
# ============================================================
def get_services():
    """Autentica via OAuth e retorna os serviços Gmail e Drive."""
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # Se não houver token ou estiver expirado, refaz o login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    gmail = build("gmail", "v1", credentials=creds)
    drive = build("drive", "v3", credentials=creds)
    return gmail, drive


# ============================================================
# ✉️ Buscar e baixar anexos de fatura no Gmail
# ============================================================
def buscar_faturas(gmail_service, termo_busca=None):
    """
    Busca e-mails com anexos .csv e baixa os arquivos localmente.
    Retorna lista com os nomes dos arquivos baixados.
    """
    termo_busca = termo_busca or 'from:"@nubank.com.br" has:attachment filename:csv'
    results = gmail_service.users().messages().list(userId="me", q=termo_busca).execute()
    mensagens = results.get("messages", [])

    if not mensagens:
        print("Nenhum e-mail de fatura encontrado.")
        return []

    baixados = []

    for msg in mensagens:
        msg_data = gmail_service.users().messages().get(userId="me", id=msg["id"]).execute()
        partes = msg_data["payload"].get("parts", [])

        for part in partes:
            if part.get("filename", "").endswith(".csv"):
                att_id = part["body"].get("attachmentId")
                if not att_id:
                    continue

                att = gmail_service.users().messages().attachments().get(
                    userId="me", messageId=msg["id"], id=att_id
                ).execute()

                file_data = base64.urlsafe_b64decode(att["data"])
                filename = part["filename"]

                os.makedirs("data", exist_ok=True)
                local_path = os.path.join("data", filename)

                with open(local_path, "wb") as f:
                    f.write(file_data)

                print(f"Arquivo CSV baixado: {filename}")
                baixados.append(local_path)

                df = load_transactions(local_path)
                if df is None:
                    # tenta ler e renomear colunas do formato Nubank em português
                    df = pd.read_csv(local_path)
                    df.columns = [col.strip() for col in df.columns]
                    df = df.rename(columns={"Data": "date", "Descrição": "title", "Valor": "amount"})
                    df["date"] = pd.to_datetime(df["date"], dayfirst=True)

                df = title_normalize(df)
                src.models.save_transactions(df)

    return baixados


# ============================================================
# ☁️ Enviar arquivos ao Google Drive
# ============================================================
def enviar_para_drive(drive_service, arquivos):
    """
    Faz upload dos arquivos baixados para a pasta do Google Drive.
    Retorna lista com os IDs dos arquivos criados.
    Serve para saber quais arquivos já foram importados e quais não
    """
    enviados = []
    for arquivo in arquivos:
        nome = os.path.basename(arquivo)
        file_metadata = {"name": nome}

        if PASTA_DRIVE_ID:
            file_metadata["parents"] = [PASTA_DRIVE_ID]

        media = MediaFileUpload(arquivo, mimetype="application/pdf")

        novo_arquivo = (
            drive_service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )

        enviados.append(novo_arquivo.get("id"))
        print(f"Arquivo enviado ao Drive: {nome} (ID: {novo_arquivo.get('id')})")

    return enviados


# ============================================================
# 🚀 Função principal — para usar no Streamlit
# ============================================================
def sincronizar_faturas():
    """
    1. Autentica Gmail + Drive
    2. Busca faturas por e-mail
    3. Envia automaticamente para o Drive
    """
    gmail, drive = get_services()
    baixados = buscar_faturas(gmail)

    if not baixados:
        return "Nenhuma nova fatura encontrada no Gmail."

    enviados = enviar_para_drive(drive, baixados)
    return f"{len(baixados)} fatura(s) baixada(s) e {len(enviados)} enviada(s) ao Google Drive com sucesso!"


# ============================================================
# 🔧 Execução direta (teste fora do Streamlit)
# ============================================================
if __name__ == "__main__":
    print("Iniciando sincronização de faturas...")
    resultado = sincronizar_faturas()
    print(resultado)
