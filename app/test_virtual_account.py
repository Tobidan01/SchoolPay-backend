import uuid

from app.services.nomba_service import NombaService


def main():

    response = NombaService.create_virtual_account(
        account_ref=str(uuid.uuid4()),
        account_name="John Doe",
    )

    print(response)


if __name__ == "__main__":
    main()