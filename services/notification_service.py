import requests
from services.auth_service import AuthService

BASE_URL = f"{AuthService.BASE_URL}/notifications/"

import requests
from services.auth_service import AuthService

def get_notifications():
        try:
            response = requests.get(BASE_URL, headers=AuthService.get_headers())
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return {"success": False, "message": response.text}
        except Exception as e:
            return {"success": False, "message": str(e)}

def mark_as_read(notification_id):
    try:
        if notification_id == "all":
            response = requests.post(f"{BASE_URL}marquer_toutes_lues/", headers=AuthService.get_headers())
        else:
            response = requests.post(f"{BASE_URL}/{notification_id}/marquer_lue/", headers=AuthService.get_headers())

        if response.status_code in [200, 201]:
            return {"success": True}
        else:
            return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}



def get_notifications():
    try:
        response = requests.get(BASE_URL, headers=AuthService.get_headers())
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "message": response.text}
    except Exception as e:
        return {"success": False, "message": str(e)}