"""Field rules shared by several schemas, written once so every form checks them the same way."""

from typing import Annotated

from pydantic import AfterValidator


def tidy_name(name: str) -> str:
    """Trim stray spaces and refuse an empty name."""
    name = name.strip()
    if not name:
        raise ValueError("Enter a full name")
    return name


def tidy_email(email: str) -> str:
    """Ignore spaces and capitals, and refuse anything that is clearly not one email address."""
    email = email.strip().lower()
    local, _, domain = email.partition("@")
    if not local or "." not in domain or "@" in domain:
        raise ValueError("Enter a valid email address")
    return email


PersonName = Annotated[str, AfterValidator(tidy_name)]
EmailAddress = Annotated[str, AfterValidator(tidy_email)]
