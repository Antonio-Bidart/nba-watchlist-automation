import time
import logging
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
from src import config

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
BASE_DELAY = 3      # segundos entre reintentos
REQUEST_TIMEOUT = 60  # segundos, más alto que el default de 30 de nba_api


def find_player_id(player_name: str):
    matches = players.find_players_by_full_name(player_name)
    if not matches:
        return None
    return matches[0]["id"]


def get_recent_games(player_id: int):
    df = None
    last_error = None

    for intento in range(1, MAX_RETRIES + 1):
        try:
            gamelog = playergamelog.PlayerGameLog(
                player_id=player_id,
                season=config.SEASON,
                season_type_all_star=config.SEASON_TYPE,
                timeout=REQUEST_TIMEOUT,
            )
            df = gamelog.get_data_frames()[0]
            break
        except Exception as e:
            last_error = e
            logger.warning(f"Intento {intento}/{MAX_RETRIES} falló consultando la NBA API: {e}")
            if intento < MAX_RETRIES:
                time.sleep(BASE_DELAY * intento)

    if df is None:
        raise last_error

    if df.empty:
        return []

    df = df.head(config.GAMES_LOOKBACK)
    games = []
    for _, row in df.iterrows():
        games.append({
            "game_id": str(row["Game_ID"]),
            "fecha": row["GAME_DATE"],
            "puntos": int(row["PTS"]),
            "rebotes": int(row["REB"]),
            "asistencias": int(row["AST"]),
        })
    return games
