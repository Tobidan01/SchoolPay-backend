from app.services.nomba_auth_service import NombaAuthService


def main():
    token = NombaAuthService.get_access_token()

    print("\n====================")
    print("ACCESS TOKEN")
    print("====================")
    print(token)


if __name__ == "__main__":
    main()