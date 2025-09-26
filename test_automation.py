import requests
import pytest
import json

BASE_URL = "http://localhost:8080"

@pytest.fixture
def client():
    return requests.Session()

def test_cadastro_duplicado(client):
    # Primeiro cadastro (deve passar)
    payload = {"email": "dupe@test.com", "password": "senha123"}
    response = client.post(f"{BASE_URL}/register", json=payload)
    assert response.status_code == 201, "Falha no cadastro inicial"

    # Segundo cadastro (duplicata - esperado 409, mas pode ser bug 200)
    response = client.post(f"{BASE_URL}/register", json=payload)
    assert response.status_code in [400, 409], f"Duplicata permitida (bug): {response.status_code} - {response.text}"

def test_parcelamento_zero(client):
    payload = {"amount": 1000, "rate": 5, "installments": 0}
    response = client.post(f"{BASE_URL}/installment/simulate", json=payload)
    # Esperado: 400 (validação); se 500, é bug de crash
    if response.status_code == 500:
        pytest.fail(f"Bug crítico: Crash 500 com HTML - {response.text[:100]}")
    assert response.status_code != 200, "Parcelamento zero aceito como válido (bug de negócio)"

def test_juros_negativo(client):
    payload = {"principal": -1000, "rate": 5, "time": 1}
    response = client.post(f"{BASE_URL}/interest/simple", json=payload)
    assert response.status_code == 400, f"Valores negativos aceitos (bug): {response.status_code} - {response.text}"

# Rode com: pytest test_automation.py -v
