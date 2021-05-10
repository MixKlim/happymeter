from starlette.testclient import TestClient
from app.app import app

client = TestClient(app)

# def test_root():
#     resp = client.get("/")
#     assert resp.status_code == 200
#     assert resp.json() == {"name": "happiness prediction app"}


def test_predict():
    json_blob = {
        "city_services": 5,
        "housing_costs": 2,
        "school_quality": 2,
        "local_policies": 4,
        "maintenance": 4,
        "social_events": 5
    }
    resp = client.post("/predict", json=json_blob)
    assert resp.status_code == 200
    assert resp.json() == {
        "prediction": 1,
        "probability": 0.5801989510171809
    }
