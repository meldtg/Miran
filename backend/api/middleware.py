import hmac
import hashlib
import json
from urllib.parse import unquote
from django.http import JsonResponse
from config import BOT_TOKEN


class TelegramAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.bot_token = (BOT_TOKEN or "").strip()

    def standardize_user_data(self, data: dict) -> dict:
        return {
            'id': data.get('id'),
            'first_name': data.get('first_name'),
            'username': data.get('username'),
            'photoUrl': data.get('photo_url') or data.get('photoUrl')
        }

    def __call__(self, request):
        request.user_data = None

        auth_header = request.headers.get("auth")
        if not auth_header:
            return self.get_response(request)

        if not self.validate_init_data(auth_header):
            return JsonResponse({"error": "Invalid auth token"}, status=401)

        decoded_data = {k: unquote(v) for k, v in [pair.split('=', 1) for pair in auth_header.split('&')]}
        user_data_str = decoded_data.get("user", "{}")
        try:
            raw_user_data = json.loads(user_data_str)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid user data"}, status=400)

        standardized = self.standardize_user_data(raw_user_data)

        request.user_data = standardized
        return self.get_response(request)

    def validate_init_data(self, init_data: str) -> bool:
        try:
            vals = {k: unquote(v) for k, v in [pair.split('=', 1) for pair in init_data.split('&')]}
            received_hash = vals.get('hash', '').strip()
            if not received_hash or not self.bot_token:
                return False
            data_check_string = '\n'.join(f"{k}={v}" for k, v in sorted(vals.items()) if k != 'hash')
            secret_key = hmac.new(b"WebAppData", self.bot_token.encode(), hashlib.sha256).digest()
            computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest().strip()
            return computed_hash == received_hash
        except Exception:
            return False


