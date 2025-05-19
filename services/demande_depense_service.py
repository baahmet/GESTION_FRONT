import requests
from services.auth_service import AuthService

BASE_URL = f"{AuthService.BASE_URL}/demandes/"

def get_demandes_depense():
    """
    Récupère la liste des demandes de dépense.
    """
    try:
        response = requests.get(BASE_URL, headers=AuthService.get_headers())
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}

def create_demande_depense(data):
    try:
        response = requests.post(BASE_URL, json=data, headers=AuthService.get_headers())
        if response.status_code == 201:
            # Si le backend ne renvoie pas de message, on force un message par défaut
            return {"success": True, "message": "Demande de dépense créée avec succès."}
        return {"success": False, "message": response.json().get("error", "Erreur lors de la création.")}
    except Exception as e:
        return {"success": False, "message": str(e)}

def valider_demande_depense(demande_id, statut):
    url = f"{BASE_URL}{demande_id}/valider/"
    data = {"statut": statut}
    try:
        response = requests.post(url, json=data, headers=AuthService.get_headers())
        if response.status_code == 200:
            return {"success": True, "message": response.json().get("message", "Traitement effectué.")}
        else:
            # Sécuriser l'accès au message d'erreur
            try:
                error_msg = response.json().get("error", response.text)
            except Exception:
                error_msg = response.text
            return {"success": False, "message": error_msg}
    except Exception as e:
        return {"success": False, "message": str(e)}


def delete_demande_depense(demande_id):
        url = f"{BASE_URL}{demande_id}/"
        try:
            response = requests.delete(url, headers=AuthService.get_headers())
            if response.status_code in (200, 204):
                return {"success": True, "message": "Demande supprimée avec succès."}
            return {"success": False, "message": response.text}
        except Exception as e:
            return {"success": False, "message": str(e)}

def update_demande_depense(demande_id, data, files=None):
    """
    Met à jour une dépense (tant qu’elle est en attente).
    """
    url = f"{BASE_URL}{demande_id}/"
    try:
        response = requests.put(url, data=data, files=files, headers=AuthService.get_headers())
        if response.status_code in (200, 204):
            return {"success": True, "message": "Dépense mise à jour avec succès."}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}
