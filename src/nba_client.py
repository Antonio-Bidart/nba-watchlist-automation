import time
import logging
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
from src import config

logger = logging.getLogger(__name__)


def find_player_id(player_name: str):
    matches = players.find_players_by_full_name(player_name)
    if not matches:
        return None
    return matches[0]["id"]


def get_recent_games(player_id: int):
    """Devuelve los últimos N partidos (config.GAMES_LOOKBACK) del jugador, más reciente primero."""
    gamelog = playergamelog.PlayerGameLog(
        player_id=player_id,
        season=config.SEASON,
        season_type_all_star=config.SEASON_TYPE,
    )
    time.sleep(0.6)  # nba_api no tiene rate limit oficial, pero conviene no abusar de stats.nba.com

    df = gamelog.get_data_frames()[0]
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
