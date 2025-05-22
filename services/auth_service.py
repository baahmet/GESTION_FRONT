import requests

class AuthService:
    BASE_URL = "http://localhost:8000/api"
    temp_email = None
    token = None
    user_data = {}

    @classmethod
    def get_headers(cls):
        return {"Authorization": f"Bearer {cls.token}"} if cls.token else {}

    @classmethod
    def login(cls, email, password):
        try:
            response = requests.post(f"{cls.BASE_URL}/login/", json={
                "email": email,
                "password": password
            })
            if response.status_code == 200:
                cls.temp_email = email
                return {"success": True, "message": response.json().get("message", "Code envoyé.")}
            return {"success": False, "message": response.json().get("error", "Identifiants invalides.")}
        except Exception as e:
            return {"success": False, "message": f"Erreur serveur : {str(e)}"}

    @classmethod
    def verify_code(cls, code):
        try:
            response = requests.post(f"{cls.BASE_URL}/login/2fa/", json={
                "email": cls.temp_email,
                "code": code
            })
            if response.status_code == 200:
                data = response.json()
                cls.token = data.get("access")
                cls.user_data = data.get("user", {})  # {"nom": "Faty", "role": "Comptable", ...}
                print(f"🔵 USER DATA = {cls.user_data}")
                return {"success": True, "message": "Connexion réussie."}
            return {"success": False, "message": response.json().get("error", "Code invalide.")}
        except Exception as e:
            return {"success": False, "message": f"Erreur serveur : {str(e)}"}

    @classmethod
    def resend_code(cls):
        try:
            response = requests.post(f"{cls.BASE_URL}/2fa/resend/", json={"email": cls.temp_email})
            if response.status_code == 200:
                return {"success": True, "message": "Nouveau code envoyé."}
            return {"success": False, "message": response.json().get("error", "Erreur lors du renvoi.")}
        except Exception as e:
            return {"success": False, "message": f"Erreur serveur : {str(e)}"}

    # 🔹 GETTERS propre pour afficher dans l'UI :
    @classmethod
    def get_user_role(cls):
        return cls.user_data.get("role", "").lower()

    @classmethod
    def get_user_nom(cls):
        return cls.user_data.get("nom", "Utilisateur")

    @classmethod
    def get_user_email(cls):
        return cls.user_data.get("email", "Utilisateur")

    @classmethod
    def logout(cls):
        cls.user_data = {}
        cls.token = None
        cls.temp_email = None

    @classmethod
    def refresh_user_data(cls):
        try:
            response = requests.get(f"{cls.BASE_URL}/me/", headers=cls.get_headers())
            if response.status_code == 200:
                cls.user_data = response.json()
        except Exception as e:
            print("Erreur refresh_user_data:", e)


def update_my_account(data):
    try:
        url = f"{AuthService.BASE_URL}/me/update/"
        response = requests.put(url, json=data, headers=AuthService.get_headers())
        if response.status_code in (200, 204):
            return {"success": True}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}

