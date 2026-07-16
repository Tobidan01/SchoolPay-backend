import json

from app.schemas.webhook import (
    NombaWebhookPayload,
)
from app.services.nomba_signature_service import (
    NombaSignatureService,
)


TIMESTAMP = "2026-07-15T12:05:00Z"


def main() -> None:
    with open(
        "payload.json",
        "r",
        encoding="utf-8",
    ) as file:
        raw_payload = json.load(file)

    payload = (
        NombaWebhookPayload.model_validate(
            raw_payload
        )
    )

    signature = (
        NombaSignatureService.generate_signature(
            payload=payload,
            timestamp=TIMESTAMP,
        )
    )

    print("\nHashing payload:")
    print(
        NombaSignatureService
        ._build_hashing_payload(
            payload=payload,
            timestamp=TIMESTAMP,
        )
    )

    print("\nPostman headers:")
    print(
        f"nomba-timestamp: {TIMESTAMP}"
    )
    print(
        f"nomba-signature: {signature}"
    )


if __name__ == "__main__":
    main()