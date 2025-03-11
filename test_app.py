import pytest
from fastapi.testclient import TestClient
from main import app, add_platform_to_trie, location_trie, TrieNode  # Импортируем нужные объекты

client = TestClient(app)

@pytest.fixture
def reset_trie():
    """Очищаем trie перед каждым тестом"""
    global location_trie
    location_trie = TrieNode()
    yield

def test_search_platforms(reset_trie):
    """Тестирование поиска рекламных площадок"""
    # Добавим тестовые данные вручную
    add_platform_to_trie("Яндекс.Директ", "/ru")
    add_platform_to_trie("Ревдинский рабочий", "/ru/svrd/revda")
    add_platform_to_trie("Ревдинский рабочий", "/ru/svrd/pervik")
    add_platform_to_trie("Газета уральских москвичей", "/ru/msk")
    add_platform_to_trie("Газета уральских москвичей", "/ru/permobl")
    add_platform_to_trie("Газета уральских москвичей", "/ru/chelobl")
    add_platform_to_trie("Крутая реклама", "/ru/svrd")

    # Тестовые запросы к API
    response = client.get("/search?location=/ru/svrd/revda")
    assert response.status_code == 200
    assert set(response.json()["platforms"]) == {"Яндекс.Директ", "Крутая реклама", "Ревдинский рабочий"}