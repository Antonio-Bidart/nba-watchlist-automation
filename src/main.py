import logging
import datetime
from src import config, sheets_client, nba_client, rules, notifier

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def run():
    logger.info("=== Arrancando corrida de NBA Watchlist ===")

    try:
        watchlist = sheets_client.get_watchlist()
    except Exception as e:
        logger.exception("No se pudo leer la watchlist")
        _notificar_error(f"No se pudo leer el Sheet de watchlist: {e}")
        return

    if not watchlist:
        logger.info("Watchlist vacía, no hay nada que procesar.")
        return

    try:
        procesados = sheets_client.get_processed_game_ids()
    except Exception as e:
        logger.exception("No se pudo leer el historial")
        _notificar_error(f"No se pudo leer el Sheet de historial: {e}")
        return

    nuevas_notificaciones = 0

    for entrada in watchlist:
        jugador = entrada["jugador"]
        umbral = entrada["umbral"]

        try:
            player_id = nba_client.find_player_id(jugador)
            if player_id is None:
                logger.warning(f"No encontré a '{jugador}' en la NBA API, salteo.")
                continue
            juegos = nba_client.get_recent_games(player_id)
        except Exception as e:
            logger.exception(f"Error consultando partidos de {jugador}")
            _notificar_error(f"Falló la consulta a la NBA API para {jugador}: {e}")
            continue

        for juego in juegos:
            clave = (jugador, juego["game_id"])
            if clave in procesados:
                continue  # idempotencia: ya está en el Historial

            cumple, motivo = rules.evaluate_game(
                juego["puntos"], juego["rebotes"], juego["asistencias"], umbral
            )

            try:
                sheets_client.append_historial({
                    "Jugador": jugador,
                    "Fecha_partido": juego["fecha"],
                    "Game_ID": juego["game_id"],
                    "Puntos": juego["puntos"],
                    "Rebotes": juego["rebotes"],
                    "Asistencias": juego["asistencias"],
                    "Cumple_umbral": "Sí" if cumple else "No",
                    "Fecha_procesado": datetime.datetime.now().isoformat(timespec="seconds"),
                })
            except Exception as e:
                logger.exception(f"No pude escribir en Historial para {jugador}")
                _notificar_error(f"Falló la escritura en Historial para {jugador}: {e}")
                continue

            if cumple:
                try:
                    notifier.send_email(
                        subject=f"🏀 {jugador} tuvo un buen partido",
                        body=(
                            f"{jugador} jugó el {juego['fecha']}\n\n"
                            f"Puntos: {juego['puntos']}\n"
                            f"Rebotes: {juego['rebotes']}\n"
                            f"Asistencias: {juego['asistencias']}\n\n"
                            f"Motivo: {motivo}"
                        ),
                    )
                    nuevas_notificaciones += 1
                except Exception:
                    logger.exception(f"No pude mandar el mail para {jugador}")

    logger.info(f"=== Corrida terminada. Notificaciones enviadas: {nuevas_notificaciones} ===")


def _notificar_error(detalle: str):
    try:
        notifier.send_email(subject="⚠️ Falló la corrida de NBA Watchlist", body=detalle)
    except Exception:
        logger.exception("Encima falló el mail de error. Revisar logs de GitHub Actions a mano.")


if __name__ == "__main__":
    run()
