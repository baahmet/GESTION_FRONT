# services/budget_service.py
import requests
from services.auth_service import AuthService

BASE_URL = f"{AuthService.BASE_URL}/budgets/"

def get_budgets():
    """
    Récupère la liste des budgets depuis l'API.
    """
    try:
        response = requests.get(BASE_URL, headers=AuthService.get_headers())
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}

def create_budget(data):
    """
    Crée un nouveau budget via l'API.
    Données attendues : dict contenant exercice, montant_total, montant_disponible, comptable
    """
    try:
        response = requests.post(BASE_URL, json=data, headers=AuthService.get_headers())
        if response.status_code == 201:
            return {"success": True, "message": "Budget créé avec succès."}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}


def cloturer_budget(budget_id):
    url = f"{BASE_URL}{budget_id}/"
    try:
        response = requests.patch(url, json={"statut": "cloture"}, headers=AuthService.get_headers())
        if response.status_code == 200:
            return {"success": True, "message": "Budget clôturé avec succès."}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}


def update_budget(budget_id, data):
    url = f"{BASE_URL}{budget_id}/"
    try:
        response = requests.patch(url, json=data, headers=AuthService.get_headers())
        if response.status_code in (200, 204):
            return {"success": True}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}




def delete_budget(budget_id):
    url = f"{BASE_URL}{budget_id}/"
    try:
        response = requests.delete(url, headers=AuthService.get_headers())
        if response.status_code in (200, 204):
            return {"success": True}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}





def get_budget_evolution_chart():
    """
    Appelle l'API pour obtenir le graphique d'évolution budgétaire
    Encodé en base64
    """
    url = f"{BASE_URL}/evolution_chart/"
    try:
        headers = AuthService.get_headers()
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return {"success": True, "data": response.json().get("image_base64")}
        else:
            return {"success": False, "message": "Erreur serveur lors du chargement du graphique."}
    except Exception as e:
        return {"success": False, "message": f"Erreur réseau : {str(e)}"}

# services/budget_service.py
import requests
from services.auth_service import AuthService

BASE_URL = f"{AuthService.BASE_URL}/budgets/"

def get_budgets():
    """
    Récupère la liste des budgets depuis l'API.
    """
    try:
        response = requests.get(BASE_URL, headers=AuthService.get_headers())
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}

def create_budget(data):
    """
    Crée un nouveau budget via l'API.
    Données attendues : dict contenant exercice, montant_total, montant_disponible, comptable
    """
    try:
        response = requests.post(BASE_URL, json=data, headers=AuthService.get_headers())
        if response.status_code == 201:
            return {"success": True, "message": "Budget créé avec succès."}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}


def cloturer_budget(budget_id):
    url = f"{BASE_URL}{budget_id}/"
    try:
        response = requests.patch(url, json={"statut": "cloture"}, headers=AuthService.get_headers())
        if response.status_code == 200:
            return {"success": True, "message": "Budget clôturé avec succès."}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}


def update_budget(budget_id, data):
    url = f"{BASE_URL}{budget_id}/"
    try:
        response = requests.patch(url, json=data, headers=AuthService.get_headers())
        if response.status_code in (200, 204):
            return {"success": True}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}




def delete_budget(budget_id):
    url = f"{BASE_URL}{budget_id}/"
    try:
        response = requests.delete(url, headers=AuthService.get_headers())
        if response.status_code in (200, 204):
            return {"success": True}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}





def get_budget_evolution_chart():
    """
    Appelle l'API pour obtenir le graphique d'évolution budgétaire
    Encodé en base64
    """
    url = f"{BASE_URL}/evolution_chart/"
    try:
        headers = AuthService.get_headers()
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return {"success": True, "data": response.json().get("image_base64")}
        else:
            return {"success": False, "message": "Erreur serveur lors du chargement du graphique."}
    except Exception as e:
        return {"success": False, "message": f"Erreur réseau : {str(e)}"}

