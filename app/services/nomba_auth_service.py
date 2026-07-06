import httpx

from app.core.config import settings


class NombaAuthService:

    @staticmethod
    def issue_token():

        response = httpx.post(
            f"{settings.NOMBA_BASE_URL}/v1/auth/token/issue",
            headers={
                "accountId": settings.NOMBA_PARENT_ACCOUNT_ID,
                "Content-Type": "application/json",
            },
            json={
                "grant_type": "client_credentials",
                "client_id": settings.NOMBA_CLIENT_ID,
                "client_secret": settings.NOMBA_PRIVATE_KEY,
            },
            timeout=30,
        )
        print("BASE URL:", settings.NOMBA_BASE_URL)
        print("FULL URL:", f"{settings.NOMBA_BASE_URL}/v1/auth/token/issue")
        print("ACCOUNT:", settings.NOMBA_PARENT_ACCOUNT_ID)
        data = response.json()

        if response.status_code >= 400:
            raise Exception(
                f"Nomba Error: {data.get('description')}"
            )

        return data["data"]   # ✅ only return the nested data


    @staticmethod
    def get_access_token():

        token_data = NombaAuthService.issue_token()

        return token_data["access_token"]