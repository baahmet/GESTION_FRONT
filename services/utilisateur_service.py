import requests
from services.auth_service import AuthService

BASE_URL = f"{AuthService.BASE_URL}"

def get_utilisateurs():
    try:
        response = requests.get(f"{BASE_URL}/utilisateurs/", headers=AuthService.get_headers())
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}

def register_utilisateur(data):
    try:
        response = requests.post(f"{BASE_URL}/register/", json=data, headers=AuthService.get_headers())
        if response.status_code == 201:
            return {"success": True}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}

def update_utilisateur(utilisateur_id, data):
    try:
        response = requests.put(f"{BASE_URL}/utilisateurs/{utilisateur_id}/", json=data, headers=AuthService.get_headers())
        if response.status_code in (200, 204):
            return {"success": True}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}

def delete_utilisateur(utilisateur_id):
    try:
        response = requests.delete(f"{BASE_URL}/utilisateurs/{utilisateur_id}/", headers=AuthService.get_headers())
        if response.status_code in (200, 204):
            return {"success": True}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}
