def test_homepage_loads(client):
    res = client.get("/")
    assert res.status_code == 200


def test_adopt_page_loads(client):
    res = client.get("/adopt")
    assert res.status_code == 200


def test_animals_api_returns_json(client):
    res = client.get("/animals/")
    assert res.status_code == 200
    data = res.get_json()
    assert "animals" in data
    assert isinstance(data["animals"], list)
