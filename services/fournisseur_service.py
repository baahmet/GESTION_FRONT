import requests
from services.auth_service import AuthService

BASE_URL = f"{AuthService.BASE_URL}/fournisseurs/"

def get_fournisseurs():
    response = requests.get(BASE_URL, headers=AuthService.get_headers())
    if response.status_code == 200:
        return {"success": True, "data": response.json()}
    return {"success": False, "message": response.text}

def create_fournisseur(data):
    response = requests.post(BASE_URL, json=data, headers=AuthService.get_headers())
    if response.status_code in (200, 201):
        return {"success": True}
    return {"success": False, "message": response.text}

def update_fournisseur(fournisseur_id, data):
    url = f"{BASE_URL}{fournisseur_id}/"
    response = requests.put(url, json=data, headers=AuthService.get_headers())
    if response.status_code in (200, 204):
        return {"success": True}
    return {"success": False, "message": response.text}

def delete_fournisseur(fournisseur_id):
    url = f"{BASE_URL}{fournisseur_id}/"
    response = requests.delete(url, headers=AuthService.get_headers())
    if response.status_code in (200, 204):
        return {"success": True}
    return {"success": False, "message": response.text}
