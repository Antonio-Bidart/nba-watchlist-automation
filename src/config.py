import os
import json
from dotenv import load_dotenv

load_dotenv()  # no hace nada si no hay .env (caso GitHub Actions), carga variables si lo hay (caso local)

# --- Google Sheets ---
SHEET_ID = os.environ["SHEET_ID"]
WATCHLIST_TAB = os.environ.get("WATCHLIST_TAB", "Respuestas de formulario 1")
HISTORIAL_TAB = os.environ.get("HISTORIAL_TAB", "Historial")

SERVICE_ACCOUNT_INFO = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])

# --- NBA data ---
SEASON = os.environ.get("NBA_SEASON", "2025-26")
SEASON_TYPE = os.environ.get("NBA_SEASON_TYPE", "Regular Season")  # o "Playoffs"
GAMES_LOOKBACK = int(os.environ.get("GAMES_LOOKBACK", "5"))  # cuántos partidos recientes revisar por jugador

# --- Reglas ---
DEFAULT_THRESHOLD_PTS = int(os.environ.get("DEFAULT_THRESHOLD_PTS", "30"))

# --- Notificaciones ---
GMAIL_ADDRESS = os.environ["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
NOTIFY_TO = os.environ.get("NOTIFY_TO", GMAIL_ADDRESS)
