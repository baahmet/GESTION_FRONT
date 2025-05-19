import requests
from services.auth_service import AuthService

BASE_URL = f"{AuthService.BASE_URL}/depenses/"

def get_depenses():
    """
    Récupère la liste des dépenses.
    """
    try:
        response = requests.get(BASE_URL, headers=AuthService.get_headers())
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}

def create_depense(data, files=None):
    """
    Crée une nouvelle dépense (Comptable).
    """
    try:
        response = requests.post(BASE_URL, data=data, files=files, headers=AuthService.get_headers())
        if response.status_code in (200, 201):
            return {"success": True, "message": "Dépense enregistrée avec succès."}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}

def update_depense(depense_id, data, files=None):
    """
    Met à jour une dépense (tant qu’elle est en attente).
    """
    url = f"{BASE_URL}{depense_id}/"
    try:
        response = requests.put(url, data=data, files=files, headers=AuthService.get_headers())
        if response.status_code in (200, 204):
            return {"success": True, "message": "Dépense mise à jour avec succès."}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}

def delete_depense(depense_id):
    """
    Supprime une dépense (si non validée).
    """
    url = f"{BASE_URL}{depense_id}/"
    try:
        response = requests.delete(url, headers=AuthService.get_headers())
        if response.status_code in (200, 204):
            return {"success": True, "message": "Dépense supprimée avec succès."}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}

def superviser_depense(depense_id):
    """
    Supervision de la dépense par CSA.
    """
    url = f"{BASE_URL}{depense_id}/superviser/"
    try:
        response = requests.post(url, headers=AuthService.get_headers())
        if response.status_code == 200:
            return {"success": True, "message": "Supervision effectuée."}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}

def valider_depense(depense_id, statut):
    """
    Validation ou rejet d'une dépense par le Directeur.
    """
    url = f"{BASE_URL}{depense_id}/valider/"
    payload = {"statut_validation": statut}
    try:
        response = requests.post(url, json=payload, headers=AuthService.get_headers())
        if response.status_code == 200:
            return {"success": True, "message": f"Dépense {statut}."}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}
