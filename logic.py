import socket
import random
from shared import i18n, ThreadSafeJsonStorage

try:
    from hacker import NetworkClient, RobberyPlanner
except ImportError:
    NetworkClient = None
    RobberyPlanner = None

class BankController:
    """
    Hlavní logika banky.
    Rozhoduje, zda příkaz vykonat lokálně, nebo ho poslat dál (Proxy).
    """
    def __init__(self, storage_file='data.json'):
        self.storage = ThreadSafeJsonStorage(storage_file)
        self.my_ip = self._get_local_ip()
        
        self.net_client = NetworkClient() if NetworkClient else None
        self.robber = RobberyPlanner(self.net_client) if RobberyPlanner else None

    def _get_local_ip(self):
        """Zjistí skutečnou IP adresu tohoto stroje v síti."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def process_command(self, raw_command):
        """
        Vstupní bod. Vezme text příkazu a vrátí textovou odpověď.
        """
        if not raw_command:
            return ""

        parts = raw_command.strip().split()
        if not parts:
            return ""

        cmd_code = parts[0].upper()

        try:
            # --- 1. ROUTING PŘÍKAZŮ ---
            
            # BC - Bank Code (Vrací vždy mou IP)
            if cmd_code == "BC":
                return f"BC {self.my_ip}"

            # BN - Bank Number (Počet klientů - Lokální)
            if cmd_code == "BN":
                return self._local_bn()

            # BA - Bank Amount (Celková suma - Lokální)
            if cmd_code == "BA":
                return self._local_ba()
            
            # AC - Account Create (Vytvoření účtu - Lokální)
            if cmd_code == "AC":
                return self._local_ac()

            # RP - Robbery Plan (HACKER FEATURE)
            if cmd_code == "RP":
                if self.robber:
                    target_amount = int(parts[1]) if len(parts) > 1 else 0
                    return self.robber.plan_robbery(target_amount, self.my_ip)
                else:
                    return i18n.get("ERR_UNKNOWN_CMD")

            # --- 2. PŘÍKAZY S ČÍSLEM ÚČTU (AD, AW, AB, AR) ---            
            if cmd_code in ["AD", "AW", "AB", "AR"]:
                if len(parts) < 2:
                    return f"{i18n.get('ERR_INVALID_FORMAT')}"
                
                # Formát: KOD CISLO/IP [CASTKA]
                account_full = parts[1] # např. 10001/10.1.2.3
                
                if '/' not in account_full:
                    return f"{i18n.get('ERR_INVALID_FORMAT')}"

                acc_num_str, target_ip = account_full.split('/')

                # -- ROZHODNUTÍ: LOKÁLNĚ NEBO PROXY? --
                if target_ip == self.my_ip or target_ip in ["127.0.0.1", "localhost"]:
                    return self._handle_local_account_cmd(cmd_code, acc_num_str, parts)
                else:
                    if self.net_client:
                        print(f"[LOG] Proxying command {cmd_code} to {target_ip}")
                        return self.net_client.send_command(target_ip, raw_command)
                    else:
                        return i18n.get("ERR_INTERNAL") 
            return i18n.get("ERR_UNKNOWN_CMD")

        except Exception as e:
            print(f"[ERROR] Logic error: {e}")
            return f"{i18n.get('ERR_INTERNAL')} ({str(e)})"

    def _handle_local_account_cmd(self, cmd, acc_num, parts):
        """Zpracování AD, AW, AB, AR pro MOJI banku."""
        data = self.storage.load()
        
        # Validace existence účtu (kromě AC, ale ten je řešen zvlášť)
        if acc_num not in data:
            return i18n.get("ERR_ACCOUNT_NOT_FOUND")

        # AD - Deposit
        if cmd == "AD":
            if len(parts) < 3: return i18n.get("ERR_INVALID_FORMAT")
            try:
                amount = int(parts[2])
            except ValueError: return i18n.get("ERR_INVALID_FORMAT")
            
            if amount < 0: return i18n.get("ERR_INVALID_FORMAT")
            
            data[acc_num] += amount
            self.storage.save(data)
            return "AD"

        # AW - Withdrawal
        if cmd == "AW":
            if len(parts) < 3: return i18n.get("ERR_INVALID_FORMAT")
            try:
                amount = int(parts[2])
            except ValueError: return i18n.get("ERR_INVALID_FORMAT")

            if data[acc_num] < amount:
                return i18n.get("ERR_LOW_FUNDS")
            
            data[acc_num] -= amount
            self.storage.save(data)
            return "AW"

        # AB - Balance
        if cmd == "AB":
            balance = data[acc_num]
            return f"AB {balance}"

        # AR - Remove
        if cmd == "AR":
            if data[acc_num] > 0:
                return i18n.get("ERR_ACCOUNT_NOT_EMPTY")
            
            del data[acc_num]
            self.storage.save(data)
            return "AR"

    def _local_ac(self):
        """Vytvoří nový účet u nás."""
        data = self.storage.load()
        
        new_acc = str(random.randint(10000, 99999))
        while new_acc in data:
            new_acc = str(random.randint(10000, 99999))
        
        # Založení s nulou
        data[new_acc] = 0
        self.storage.save(data)
        
        return f"AC {new_acc}/{self.my_ip}"

    def _local_bn(self):
        data = self.storage.load()
        return f"BN {len(data)}"

    def _local_ba(self):
        data = self.storage.load()
        total = sum(data.values())
        return f"BA {total}"