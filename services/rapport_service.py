import requests
from services.auth_service import AuthService

BASE_URL = f"{AuthService.BASE_URL}"

def get_rapports():
    url = f"{AuthService.BASE_URL}/rapports/"
    try:
        response = requests.get(url, headers=AuthService.get_headers())
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return {"success": True, "data": data}
            else:
                return {"success": False, "message": "Réponse inattendue du serveur."}
        else:
            return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}

def generer_rapport(data):
    """
    Génère un nouveau rapport via l'endpoint spécial (rapports/generer/).
    data = {budget_id, periode, type}
    """
    url = f"{AuthService.BASE_URL}/rapports/generer/"
    try:
        response = requests.post(url, json=data, headers=AuthService.get_headers())
        if response.status_code == 200:
            return {"success": True, "message": "Rapport généré avec succès."}
        return {"success": False, "message": response.json().get("error", response.text)}
    except Exception as e:
        return {"success": False, "message": str(e)}

def telecharger_rapport(rapport_id, save_path):
    """
    Télécharge le fichier du rapport et le sauvegarde sur le disque.
    """
    url = f"{BASE_URL}/rapports/{rapport_id}/telecharger/"
    try:
        response = requests.get(url, headers=AuthService.get_headers(), stream=True)
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return {"success": True}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}

def update_rapport(rapport_id, data):
    """
    Modifier les informations d'un rapport.
    """
    url = f"{BASE_URL}/rapports/{rapport_id}/"
    try:
        response = requests.put(url, json=data, headers=AuthService.get_headers())
        if response.status_code in (200, 204):
            return {"success": True}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}

def delete_rapport(rapport_id):
    """
    Supprimer un rapport financier.
    """
    url = f"{BASE_URL}/rapports/{rapport_id}/"
    try:
        response = requests.delete(url, headers=AuthService.get_headers())
        if response.status_code in (200, 204):
            return {"success": True}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}
