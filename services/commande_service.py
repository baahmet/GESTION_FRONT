import requests
from services.auth_service import AuthService

BASE_URL = f"{AuthService.BASE_URL}/commandes/"

def get_commandes():
    try:
        response = requests.get(BASE_URL, headers=AuthService.get_headers())
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}

def create_commande(data):
    try:
        response = requests.post(BASE_URL, json=data, headers=AuthService.get_headers())
        if response.status_code == 201:
            return {"success": True}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}

def delete_commande(commande_id):
    try:
        url = f"{BASE_URL}{commande_id}/"
        response = requests.delete(url, headers=AuthService.get_headers())
        if response.status_code in (200, 204):
            return {"success": True}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}

def valider_commande(commande_id, statut):
    try:
        url = f"{BASE_URL}{commande_id}/valider/"
        response = requests.post(url, json={"statut": statut}, headers=AuthService.get_headers())
        if response.status_code == 200:
            return {"success": True}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}
