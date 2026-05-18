def test_read_root(client):
    """Prueba el endpoint raíz."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "SATI API is running. Fintech Audit System Active."}

def test_ingest_transaction_valid(client):
    """
    Prueba la ingesta de una transacción válida.
    """
    payload = {
        "id": "TX-12345",
        "monto": 1500.50,
        "moneda": "USD",
        "comercio_id": "COM-99"
    }
    response = client.post("/ingest", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["transaction_id"] == payload["id"]
    assert body["status"] == "SUCCESS"
    assert len(body["audit_hash"]) == 64

    audit = client.get(f"/audit/{payload['id']}")
    assert audit.status_code == 200
    audit_body = audit.json()
    assert audit_body["transaction_id"] == payload["id"]
    assert audit_body["integrity_status"] == "VERIFIED"
    assert audit_body["record_hash_ok"] is True
    assert audit_body["chain_ok"] is True

def test_ingest_transaction_invalid_amount(client):
    """Prueba que la validación semántica rechace montos negativos."""
    payload = {
        "id": "TX-ERR",
        "monto": -10.0,
        "moneda": "USD",
        "comercio_id": "COM-01"
    }
    response = client.post("/ingest", json=payload)
    assert response.status_code == 422 # Error de validación Pydantic
    assert "monto" in response.text

def test_ingest_duplicate_returns_409(client):
    payload = {
        "id": "TX-DUP",
        "monto": 10.0,
        "moneda": "USD",
        "comercio_id": "COM-01"
    }
    r1 = client.post("/ingest", json=payload)
    assert r1.status_code == 200
    r2 = client.post("/ingest", json=payload)
    assert r2.status_code == 409

def test_audit_nonexistent_returns_404(client):
    response = client.get("/audit/NO_EXISTE")
    assert response.status_code == 404

def test_health_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "OK"
