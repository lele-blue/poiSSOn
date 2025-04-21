import os

from django.apps import AppConfig


class OtpWebauthnConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'otp_webauthn'

    def ready(self):
        aaguid_mapping_path = os.path.join(os.path.dirname(__file__), "data", "aaguids.json")
        if not os.path.isfile(aaguid_mapping_path):
            print("Downloading AAGUID mapping")
            import urllib3, shutil
            pool = urllib3.PoolManager()
            with open(aaguid_mapping_path, "wb") as out, pool.request("GET", "https://raw.githubusercontent.com/passkeydeveloper/passkey-authenticator-aaguids/refs/heads/main/combined_aaguid.json", preload_content=False) as resp:
                shutil.copyfileobj(resp, out)

            resp.release_conn()

            print("Downloaded AAGUID mapping")
