from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from app.database.db import engine


def test_connection() -> None:
    try:
        connection = engine.connect()
        print("Подключение к базе прошло успешно!")
        connection.close()
    except Exception as exc:
        print("Ошибка подключения:", exc)


if __name__ == "__main__":
    test_connection()
