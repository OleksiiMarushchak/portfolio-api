from fastapi import Request
from slowapi import Limiter


def client_ip(request: Request) -> str:
    # На Fly справжня IP клієнта в заголовку Fly-Client-IP; локально його немає.
    return request.headers.get("fly-client-ip") or (
        request.client.host if request.client else "unknown"
    )


limiter = Limiter(key_func=client_ip)