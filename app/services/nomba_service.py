# app/services/nomba_service.py

import uuid
import httpx

from app.core.config import settings
from app.services.nomba_auth_service import (
    NombaAuthService,
)


class NombaService:

    @staticmethod
    def create_virtual_account(student):
        

        token = NombaAuthService.get_access_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "accountId": settings.NOMBA_PARENT_ACCOUNT_ID,
            "Content-Type": "application/json",
        }

        payload = {
            "accountRef": str(student.id),
            "accountName": f"{student.first_name} {student.last_name}",
    }

        response = httpx.post(
            f"{settings.NOMBA_BASE_URL}/v1/accounts/virtual",
            headers=headers,
            json=payload,
            timeout=30,
        )

        
        print(response.status_code)
        print(response.text)

        response.raise_for_status()

        return response.json()