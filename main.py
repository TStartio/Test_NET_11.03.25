from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from typing import Set, Dict
import uvicorn
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>Моё тестовое задание</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                }
                h1 {
                    color: #4CAF50;
                }
                p {
                    font-size: 1.1em;
                }
                .instruction {
                    margin-top: 20px;
                    padding: 10px;
                    background-color: #f1f1f1;
                    border-radius: 5px;
                }
                a {
                    color: #007bff;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <h1>Добро пожаловать в Моё тестовое задание!</h1>
            <p>Этот сервис помогает подобрать рекламные площадки для заданной локации, используя структуру Trie для быстрой обработки запросов.</p>

            <div class="instruction">
                <h2>Как использовать API:</h2>
                <ul>
                    <li><strong>Документация:</strong> Для удобной работы с API перейдите по <a href="/docs">ссылке</a>.</li>
                    <li><strong>Загрузка данных:</strong> Для загрузки данных используйте метод POST на <code>/upload</code> с файлом в следующем формате:</li>
                </ul>
                <pre>
Яндекс.Директ:/ru
Ревдинский рабочий:/ru/svrd/revda,/ru/svrd/pervik
Газета уральских москвичей:/ru/msk,/ru/permobl,/ru/chelobl
Крутая реклама:/ru/svrd
                </pre>

                <ul>
                    <li><strong>Поиск площадок:</strong> Для поиска рекламных площадок по локации используйте метод GET на <code>/search?location=<location></code></li>
                </ul>
            </div>
        </body>
    </html>
    """


# Структура данных для хранения локаций и площадок
class TrieNode:
    def __init__(self):
        self.children: Dict[str, 'TrieNode'] = {}
        self.platforms: Set[str] = set()


# Глобальное дерево для хранения данных
location_trie = TrieNode()


# Метод для добавления площадки в дерево по локации
def add_platform_to_trie(platform: str, location: str):
    logging.info(f"Добавляем площадку '{platform}' для локации '{location}'")
    current = location_trie
    parts = location.strip('/').split('/')

    # Создаём или переходим к узлам по пути, но не добавляем площадку в промежуточные узлы
    for i, part in enumerate(parts):
        if part not in current.children:
            current.children[part] = TrieNode()
        current = current.children[part]

    # Добавляем площадку только в конечный узел
    current.platforms.add(platform)
    logging.info(f"Площадка '{platform}' добавлена в конечный узел: {parts}")


# Метод загрузки данных из файла
@app.post("/upload")
async def upload_file(file: UploadFile):
    global location_trie
    # Очищаем текущее дерево
    location_trie = TrieNode()

    try:
        # Читаем файл
        content = await file.read()
        lines = content.decode('utf-8').splitlines()

        if not lines:
            raise HTTPException(status_code=400, detail="Файл пуст")

        logging.info("Загружаем файл:")
        for line in lines:
            logging.info(f"Обрабатываем строку: {line}")
            if not line.strip():
                logging.info("Пропущена пустая строка")
                continue
            try:
                platform, locations = line.split(':', 1)
                platform = platform.strip()
                if not platform or not locations:
                    logging.info(f"Пропущена некорректная строка: {line}")
                    continue
                location_list = locations.split(',')
                for loc in location_list:
                    loc = loc.strip()
                    if loc:
                        add_platform_to_trie(platform, loc)
            except ValueError:
                logging.info(f"Пропущена строка с ошибкой: {line}")
                continue

        return {"message": "Данные успешно загружены"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки файла: {str(e)}")


# Метод поиска площадок по локации
@app.get("/search")
async def search_platforms(location: str):
    if not location:
        return {"platforms": []}

    current = location_trie
    platforms = set()
    parts = location.strip('/').split('/')

    # Идем по дереву и собираем все площадки из узлов по пути
    temp_node = location_trie  # Начинаем с корня
    for part in parts:
        if part not in temp_node.children:
            break
        temp_node = temp_node.children[part]
        platforms.update(temp_node.platforms)

    return {"platforms": list(platforms)}


# Запуск сервиса
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
