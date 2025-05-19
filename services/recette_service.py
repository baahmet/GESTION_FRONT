import requests
from services.auth_service import AuthService

BASE_URL = f"{AuthService.BASE_URL}/recettes/"

def get_recettes():
    try:
        response = requests.get(BASE_URL, headers=AuthService.get_headers())
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}

def create_recette(data, justificatif_path=None):
    try:
        headers = AuthService.get_headers()
        headers.pop('Content-Type', None)  # Important pour multipart/form-data

        files = {'justificatif': open(justificatif_path, 'rb')} if justificatif_path else None

        response = requests.post(BASE_URL, data=data, files=files, headers=headers)

        if response.status_code == 201:
            return {"success": True, "message": "Recette ajoutée avec succès."}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}

def delete_recette(recette_id):
    try:
        response = requests.delete(f"{BASE_URL}{recette_id}/", headers=AuthService.get_headers())
        if response.status_code in (200, 204):
            return {"success": True}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}

def update_recette(recette_id, data, justificatif_path=None):
    try:
        headers = AuthService.get_headers()
        headers.pop('Content-Type', None)

        files = {'justificatif': open(justificatif_path, 'rb')} if justificatif_path else None

        response = requests.patch(f"{BASE_URL}{recette_id}/", data=data, files=files, headers=headers)

        if response.status_code == 200:
            return {"success": True, "message": "Recette mise à jour avec succès."}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}
