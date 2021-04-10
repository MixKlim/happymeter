from starlette.testclient import TestClient

from app import app

client = TestClient(app)

def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"name": "iris flower prediction app"}


def test_predict():
    json_blob = {
        "sepal_length": "3.0",
        "sepal_width": "5.0", 
        "petal_length": "2.0", 
        "petal_width": "1.0"
    }
    resp = client.post("/predict", json=json_blob)
    assert resp.status_code == 200
    assert resp.json() == {
        "prediction": "Iris-setosa",
        "probability": 0.5
    }