from fastapi.testclient import TestClient


def test_get_users_respects_org_config(client: TestClient, sample_data):
    response = client.get(
        "/api/v1/users",
        params={
            "org_id": sample_data["org_b"],
            "limit": 1,
        },
    )
    assert response.status_code == 200
    payload = response.json()

    assert payload["count"] == 1
    assert payload["total_page"] == 1
    record = payload["data"][0]
    assert set(record.keys()) == {
        "id",
        "org_id",
        "first_name",
        "last_name",
        "location",
    }
    assert record["org_id"] == sample_data["org_b"]
    assert "email" not in record
    assert "department" not in record


def test_get_users_filters_by_department(client: TestClient, sample_data):
    response = client.get(
        "/api/v1/users",
        params={
            "org_id": sample_data["org_a"],
            "department": "Engineering",
            "limit": 10,
        },
    )
    assert response.status_code == 200
    payload = response.json()

    assert payload["count"] == 1
    assert payload["page"] == 1
    assert payload["data"][0]["first_name"] == "Alice"
    assert payload["data"][0]["department"] == "Engineering"


def test_get_filter_values_returns_distinct_sets(client: TestClient, sample_data):
    response = client.get("/api/v1/users/filters")
    assert response.status_code == 200
    payload = response.json()

    assert set(payload["locations"]) == {"USA", "Canada"}
    assert set(payload["departments"]) == {"Engineering", "Operations", "Finance"}
    assert set(payload["positions"]) == {"Engineer", "Manager", "Analyst"}

    org_names = {org["name"] for org in payload["organizations"]}
    assert org_names == {"Org A", "Org B"}
