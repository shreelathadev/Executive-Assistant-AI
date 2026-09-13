"""
Shared rate limiter, applied only to endpoints that call Gemini, plus
the auth endpoints (signup/login). This app has no per-user quota
system, so a publicly reachable URL means anyone can hit these
endpoints -- each AI call costs real quota/money, and unlimited
login/signup attempts is a brute-force / spam-account risk.

Per-IP limiting is a blunt but sufficient guard at this stage; a real
multi-tenant product would rate-limit per authenticated user instead
for the AI endpoints (auth endpoints obviously stay per-IP, since
there's no user yet at signup/login time).
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)