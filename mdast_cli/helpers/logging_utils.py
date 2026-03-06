from collections.abc import Mapping
from typing import Any, Optional


def redact(data: Optional[Mapping[str, Any]]) -> Mapping[str, Any]:
    if not data:
        return {}
    result = dict(data)
    email = result.get('email')
    if isinstance(email, str) and '@' in email:
        name, _, domain = email.partition('@')
        if name:
            masked = (name[0] + '***') if len(name) > 1 else '*'
            result['email'] = f'{masked}@{domain}'
        else:
            result['email'] = '***'
    return result


