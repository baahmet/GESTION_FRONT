import requests
from services.auth_service import AuthService

BASE_URL = f"{AuthService.BASE_URL}/journal/"

def get_audit_logs():
    try:
        response = requests.get(BASE_URL, headers=AuthService.get_headers())
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}
