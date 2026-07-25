"""Fail closed until the exact Cop-owned parity manifest is accepted."""

PENDING_MESSAGE = (
    "PENDING: no Cop-owned shared-contract proposal or accepted parity manifest is available; "
    "hash verification was not run."
)


def main() -> int:
    """Report the missing external contract gate without inventing a format."""
    print(PENDING_MESSAGE)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
