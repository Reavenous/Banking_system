import socket
import time
from shared import i18n

# Defaultní port, na kterém poslouchají ostatní banky ve třídě.
# Pokud se ve třídě dohodnete jinak, změň to zde nebo v main.py.
DEFAULT_TARGET_PORT = 65525

class NetworkClient:
    """
    Třída pro komunikaci s ostatními uzly (bankami).
    Otevírá klientské sockety (TCP connect).
    """
    def __init__(self, timeout=5):
        self.timeout = timeout

    def send_command(self, target_ip, command_text, target_port=DEFAULT_TARGET_PORT):
        """
        Pošle textový příkaz na cílovou IP a vrátí odpověď.
        Řeší připojení, odeslání, čekání na odpověď a odpojení.
        """
        s = None
        try:
            # Vytvoření socketu
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(self.timeout) 
            
            # Připojení k cizí bance
            s.connect((target_ip, target_port))
            
            # Odeslání dat (UTF-8, bez zbytečných mezer na konci)
            msg = command_text.strip()
            s.sendall(msg.encode('utf-8'))
            
            # Čekání na odpověď
            response = s.recv(1024) # 1KB buffer stačí na tyto zprávy
            if not response:
                return "ER Empty response"
            
            return response.decode('utf-8').strip()

        except socket.timeout:
            return f"ER Timeout ({target_ip} neodpovídá)"
        except ConnectionRefusedError:
            return f"ER Connection Refused ({target_ip} neběží)"
        except Exception as e:
            return f"ER Network Error: {str(e)}"
        finally:
            if s:
                s.close() # Vždy slušně zavřít spojení

class RobberyPlanner:
    """
    Logika pro úroveň HACKER.
    Skenuje síť a hledá nejlepší cíl pro loupež.
    """
    def __init__(self, client):
        self.client = client # Instance NetworkClient
        self.peers_file = "peers.txt"

    def _load_peers(self):
        """
        Načte seznam IP adres spolužáků ze souboru peers.txt.
        Každá IP na novém řádku.
        """
        peers = []
        try:
            with open(self.peers_file, "r") as f:
                for line in f:
                    ip = line.strip()
                    if ip and not ip.startswith("#"):
                        peers.append(ip)
        except FileNotFoundError:
            # Fallback pro testování, pokud soubor neexistuje
            print(f"[WARN] {self.peers_file} nenalezen, používám testovací seznam.")
            return ["127.0.0.1"] 
        return peers

    def plan_robbery(self, target_amount, my_ip):
        """
        Hlavní algoritmus loupeže.
        1. Oskenuje všechny banky (zjistí peníze a klienty).
        2. Vybere ty nejlepší, aby součet >= target_amount.
        3. Minimalizuje počet poškozených klientů.
        """
        peers = self._load_peers()
        candidates = [] # Seznam slovníků: {'ip': str, 'money': int, 'clients': int}
        
        print(f"[ROBBERY] Začínám skenovat síť. Cíl: {target_amount}")

        # 1. Fáze: Sběr dat (Scan)
        for ip in peers:
            if ip == my_ip: continue # Nebudeme vykrádat sami sebe

            # Zjistíme zůstatek (BA)
            resp_ba = self.client.send_command(ip, "BA")
            # Zjistíme počet klientů (BN)
            resp_bn = self.client.send_command(ip, "BN")

            # Analýza odpovědí (musí začínat BA/BN a následovat číslo)
            money = 0
            clients = 0
            
            if resp_ba.startswith("BA"):
                try: money = int(resp_ba.split()[1])
                except: money = 0
            
            if resp_bn.startswith("BN"):
                try: clients = int(resp_bn.split()[1])
                except: clients = 0

            # Pokud má banka peníze, přidáme ji na seznam kandidátů
            if money > 0:
                candidates.append({'ip': ip, 'money': money, 'clients': clients})
                print(f"[SCAN] {ip}: {money} $ / {clients} klientů")

        # 2. Fáze: Výběr obětí (Greedy Algorithm)
        # Seřadíme banky podle poměru "Peníze na jednoho klienta" sestupně.
        # Tím získáme "nejvíc muziky za nejmíň poškozených lidí".
        # (Abychom se vyhnuli dělení nulou, dáme clients+1 nebo 1)
        candidates.sort(key=lambda x: x['money'] / (x['clients'] if x['clients'] > 0 else 0.1), reverse=True)

        current_loot = 0
        victims_count = 0
        robbed_ips = []

        for bank in candidates:
            if current_loot >= target_amount:
                break
            
            robbed_ips.append(bank['ip'])
            current_loot += bank['money']
            victims_count += bank['clients']

        # 3. Fáze: Výsledek
        if current_loot == 0:
            return "RP V síti nejsou žádné peníze k loupeži."
        
        ips_str = " a ".join(robbed_ips)
        
        msg = (f"RP K dosažení cíle {target_amount} je třeba vyloupit banky: {ips_str}. "
               f"Získáte celkem {current_loot} a bude poškozeno {victims_count} klientů.")
        
        return msg