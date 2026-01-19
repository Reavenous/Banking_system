import json
import threading
import os
import tempfile
import shutil

class LocalizationManager:
    """
    Univerzální správce jazyků.
    Umožňuje nastavit jazyk aplikace a vracet přeložené texty.
    """
    def __init__(self, default_lang='cs'):
        self.current_lang = default_lang
        self._messages = {
            "ERR_INTERNAL": {
                "cs": "ER Interní chyba serveru.",
                "en": "ER Internal server error.",
                "fr": "ER Erreur interne du serveur."
            },
            "ERR_UNKNOWN_CMD": {
                "cs": "ER Neznámý příkaz.",
                "en": "ER Unknown command.",
                "fr": "ER Commande inconnue."
            },
            "ERR_INVALID_FORMAT": {
                "cs": "ER Chybný formát příkazu.",
                "en": "ER Invalid command format.",
                "fr": "ER Format de commande invalide."
            },
            "ERR_ACCOUNT_EXISTS": {
                "cs": "ER Účet již existuje.",
                "en": "ER Account already exists.",
                "fr": "ER Le compte existe déjà."
            },
            "ERR_ACCOUNT_NOT_FOUND": {
                "cs": "ER Účet nenalezen.",
                "en": "ER Account not found.",
                "fr": "ER Compte introuvable."
            },
            "ERR_LOW_FUNDS": {
                "cs": "ER Nedostatek finančních prostředků.",
                "en": "ER Insufficient funds.",
                "fr": "ER Fonds insuffisants."
            },
            "ERR_ACCOUNT_NOT_EMPTY": {
                "cs": "ER Nelze smazat účet, na kterém jsou peníze.",
                "en": "ER Cannot delete account with remaining funds.",
                "fr": "ER Impossible de supprimer un compte avec des fonds."
            },
            "MSG_SERVER_STARTED": {
                "cs": "Server spuštěn na portu",
                "en": "Server started on port",
                "fr": "Serveur démarré sur le port"
            },
            "MSG_CLIENT_CONNECTED": {
                "cs": "Připojen nový klient:",
                "en": "New client connected:",
                "fr": "Nouveau client connecté :"
            }
        }

    def set_language(self, lang_code):
        """Nastaví aktuální jazyk (cs, en, fr)."""
        if lang_code in ['cs', 'en', 'fr']:
            self.current_lang = lang_code
            return True
        return False

    def get(self, key):
        """Vrátí text podle klíče a aktuálně nastaveného jazyka."""
        msg_dict = self._messages.get(key)
        if not msg_dict:
            return f"MISSING_TRANSLATION: {key}"
        return msg_dict.get(self.current_lang, msg_dict.get('en')) 


class ThreadSafeJsonStorage:
    """
    Bezpečné úložiště dat.
    1. Thread-safe: Používá zámek (Lock), aby se vlákna nepbila.
    2. Atomic Save: Používá dočasný soubor pro bezpečný zápis.
    """
    def __init__(self, filename):
        self.filename = filename
        self.lock = threading.RLock() 
        
    def load(self):
        """Načte data ze souboru. Pokud neexistuje, vrátí prázdný slovník."""
        with self.lock:
            if not os.path.exists(self.filename):
                return {}
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}

    def save(self, data):
        """
        Atomicky uloží data.
        Zapíše do .tmp a pak přejmenuje. Nikdy nezanechá poškozený soubor.
        """
        with self.lock:
            # 1. Vytvoříme dočasný soubor ve stejném adresáři
            dir_name = os.path.dirname(self.filename) or '.'
            tmp_fd, tmp_path = tempfile.mkstemp(dir=dir_name, text=True)
            
            try:
                # 2. Zapíšeme data
                with os.fdopen(tmp_fd, 'w', encoding='utf-8') as tmp_file:
                    json.dump(data, tmp_file, indent=4)
                
                # 3. Atomické přejmenování 
                os.replace(tmp_path, self.filename)
            except Exception as e:
                # Úklid v případě chyby
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                raise e

i18n = LocalizationManager()