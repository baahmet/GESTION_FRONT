import requests
from services.auth_service import AuthService

BASE_URL = "http://localhost:8000/api"

def get_dashboard_data():
    """
    Récupère les budgets, recettes et dépenses pour calculer le dashboard global.
    """
    headers = AuthService.get_headers()

    if not headers.get("Authorization"):
        return {"success": False, "message": "Aucun token d'authentification. Veuillez vous reconnecter."}

    try:
        budgets = requests.get(f"{BASE_URL}/budgets/", headers=headers).json()
        recettes = requests.get(f"{BASE_URL}/recettes/", headers=headers).json()
        depenses = requests.get(f"{BASE_URL}/depenses/", headers=headers).json()

        if not isinstance(budgets, list) or not isinstance(recettes, list) or not isinstance(depenses, list):
            return {"success": False, "message": "Erreur lors de la récupération des données."}

        total_budget = sum(b.get("montant_total", 0) for b in budgets)
        total_recettes = sum(r.get("montant", 0) for r in recettes)
        total_depenses = sum(d.get("montant", 0) for d in depenses)

        budgets_en_cours = len([b for b in budgets if b.get("statut") == "en_cours"])
        budgets_clotures = len([b for b in budgets if b.get("statut") == "cloture"])

        taux_utilisation = round((total_depenses / total_budget * 100), 2) if total_budget else 0

        return {
            "success": True,
            "data": {
                "total_budget": total_budget,
                "total_recettes": total_recettes,
                "total_depenses": total_depenses,
                "taux_utilisation": taux_utilisation,
                "budgets_en_cours": budgets_en_cours,
                "budgets_clotures": budgets_clotures
            }
        }

    except Exception as e:
        return {"success": False, "message": f"Erreur : {str(e)}"}
