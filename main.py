import sys
import os

# Добавляем текущую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импортируем main из src
from src.main import main, asyncio, platform

# Запускаем игру
if __name__ == "__main__":
    # Для запуска на настольной платформе
    if platform.system() != "Emscripten":
        asyncio.run(main())
    else:
        # Для запуска в браузере
        asyncio.ensure_future(main())