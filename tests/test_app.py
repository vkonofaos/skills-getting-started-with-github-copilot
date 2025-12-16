from fastapi.testclient import TestClient
from src import app as app_module
from src.app import app, activities

client = TestClient(app)


def test_get_activities():
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    # Basic sanity check for a known activity
    assert "Programming Class" in data


def test_signup_and_unregister():
    activity = "Programming Class"
    email = "tester@example.com"

    # Ensure test email is not present initially
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Sign up
    res = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert res.status_code == 200
    body = res.json()
    assert "Signed up" in body.get("message", "")

    # Verify participant appears
    data = client.get("/activities").json()
    assert email in data[activity]["participants"]

    # Unregister
    res2 = client.delete(f"/activities/{activity}/signup", params={"email": email})
    assert res2.status_code == 200
    body2 = res2.json()
    assert "Removed" in body2.get("message", "")

    # Verify removal
    data2 = client.get("/activities").json()
    assert email not in data2[activity]["participants"]


def test_prevent_duplicate_signup():
    activity = "Programming Class"
    email = "duplicate@example.com"

    # Clean up if necessary
    participants = activities[activity]["participants"]
    if email in participants:
        participants.remove(email)

    # First signup should succeed
    r1 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r1.status_code == 200

    # Second signup should fail with 400
    r2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r2.status_code == 400

    # Cleanup
    if email in participants:
        participants.remove(email)
