from app import app


def test_root():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200


def test_root_html_content():
    client = app.test_client()
    response = client.get("/")
    html = response.data.decode("utf-8")
    assert "<!DOCTYPE html>" in html
    assert "Entregable 4" in html
    assert "¡Hola!" in html