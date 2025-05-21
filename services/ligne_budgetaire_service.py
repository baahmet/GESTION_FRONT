# services/ligne_budgetaire_service.py
import requests
from services.auth_service import AuthService

BASE_URL = f"{AuthService.BASE_URL}/lignes/"


def get_lignes_by_budget(budget_id):
    """
    Récupère les lignes budgétaires associées à un budget donné.
    """
    try:
        response = requests.get(BASE_URL, headers=AuthService.get_headers(), params={"budget": budget_id})
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}


def create_ligne_budgetaire(data, budget_disponible=None):
    """
    Crée une nouvelle ligne budgétaire pour un budget.
    Vérifie si le montant alloué dépasse le budget disponible (optionnel).
    """
    try:
        if budget_disponible is not None and data['montant_alloue'] > budget_disponible:
            return {"success": False, "message": "Montant alloué dépasse le budget disponible."}

        response = requests.post(BASE_URL, json=data, headers=AuthService.get_headers())
        if response.status_code == 201:
            return {"success": True, "message": "Ligne ajoutée."}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}



def update_ligne_budgetaire(ligne_id, data):
    try:
        response = requests.put(f"{BASE_URL}{ligne_id}/", json=data, headers=AuthService.get_headers())
        if response.status_code == 200:
            return {"success": True}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}

def delete_ligne_budgetaire(ligne_id):
    try:
        response = requests.delete(f"{BASE_URL}{ligne_id}/", headers=AuthService.get_headers())
        if response.status_code in (200, 204):
            return {"success": True}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}
