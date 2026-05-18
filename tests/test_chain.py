def test_verify_chain_ok(client):
    headers = {"X-API-KEY": "sati-demo-key"}
    payload = {
        "id": "TX-CHAIN-1",
        "monto": 100.0,
        "moneda": "USD",
        "comercio_id": "COM-01"
    }
    r = client.post("/ingest", json=payload, headers=headers)
    assert r.status_code == 200

    verify = client.get("/verify-chain", headers=headers)
    assert verify.status_code == 200
    body = verify.json()
    assert body["status"] == "VERIFIED"
    assert body["invalid_records"] == 0


def test_verify_chain_requires_api_key(client):
    verify = client.get("/verify-chain")
    assert verify.status_code == 401
    assert verify.json() == {"detail": "Unauthorized"}


def test_audit_requires_api_key(client):
    headers = {"X-API-KEY": "sati-demo-key"}
    payload = {
        "id": "TX-AUD-1",
        "monto": 100.0,
        "moneda": "USD",
        "comercio_id": "COM-01"
    }
    r = client.post("/ingest", json=payload, headers=headers)
    assert r.status_code == 200

    audit = client.get(f"/audit/{payload['id']}")
    assert audit.status_code == 401
    assert audit.json() == {"detail": "Unauthorized"}


def test_kpis_requires_api_key(client):
    kpis = client.get("/kpis")
    assert kpis.status_code == 401
    assert kpis.json() == {"detail": "Unauthorized"}


def test_duplicate_increments_duplicate_attempts(client):
    headers = {"X-API-KEY": "sati-demo-key"}
    payload = {
        "id": "TX-DUP-COUNT",
        "monto": 10.0,
        "moneda": "USD",
        "comercio_id": "COM-01"
    }
    r1 = client.post("/ingest", json=payload, headers=headers)
    assert r1.status_code == 200
    r2 = client.post("/ingest", json=payload, headers=headers)
    assert r2.status_code == 409

    kpis = client.get("/kpis", headers=headers)
    assert kpis.status_code == 200
    body = kpis.json()
    assert body["duplicate_attempts"] == 1
