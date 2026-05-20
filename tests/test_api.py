def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_status_endpoint(client):
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert "ready" in data
    assert "building" in data


def test_query_when_index_not_ready(client, monkeypatch):
    monkeypatch.setattr(
        "app.main.get_index_status",
        lambda: {"ready": False, "building": False, "error": None},
    )
    response = client.post("/query", json={"query": "What is the main theme?"})
    assert response.status_code == 200
    data = response.json()
    assert "No document index" in data["answer"]
    assert data["sources"] == []


def test_query_with_mocked_graph(client, monkeypatch):
    monkeypatch.setattr(
        "app.main.get_index_status",
        lambda: {"ready": True, "building": False, "error": None},
    )
    monkeypatch.setattr(
        "app.main.app_graph.invoke",
        lambda state: {
            "final_answer": "The book emphasizes living in the present moment.",
            "conversation": [{"user": "theme?", "bot": "present moment"}],
            "sources": [
                {
                    "id": 1,
                    "source": "book.pdf",
                    "page": 12,
                    "excerpt": "Only the present moment is real.",
                }
            ],
        },
    )
    response = client.post("/query", json={"query": "What is the main theme?"})
    assert response.status_code == 200
    data = response.json()
    assert "present moment" in data["answer"]
    assert len(data["sources"]) == 1
    assert data["sources"][0]["page"] == 12
