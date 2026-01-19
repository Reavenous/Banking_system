import sys
import signal
import time
from shared import i18n
from logic import BankController
from network import BankServer

# --- KONFIGURACE ---
# Port musí být v rozsahu 65525 - 65535
DEFAULT_PORT = 65525
HOST = "0.0.0.0" 
TIMEOUT = 60.0

def signal_handler(sig, frame):
    """
    Tato funkce se zavolá, když stiskneš Ctrl+C.
    Zajistí bezpečné vypnutí serveru.
    """
    print("\n[SYSTEM] Ukončování aplikace...")
    sys.exit(0)

def main():
    print("==========================================")
    print("   P2P BANK NODE - HACKER EDITION v1.0    ")
    print("==========================================")

    # 1. Výběr jazyka (Znovupoužitelnost v praxi)
    print("Choose language / Vyberte jazyk / Choisissez la langue")
    lang = input("(cs / en / fr) [default: cs]: ").strip().lower()
    
    if not lang:
        lang = 'cs'
    
    if i18n.set_language(lang):
        print(f"OK. Language set to: {lang.upper()}")
    else:
        print(f"Warning: Unknown language '{lang}'. Fallback to CS.")
        i18n.set_language('cs')

    # 2. Nastavení portu (Volitelné, aby se dalo spustit více bank na jednom PC)
    port_input = input(f"Port [{DEFAULT_PORT}]: ").strip()
    if port_input.isdigit():
        port = int(port_input)
    else:
        port = DEFAULT_PORT

    if not (65525 <= port <= 65535):
        print("!! VAROVÁNÍ: Port je mimo povolený rozsah zadání (65525-65535) !!")

    # 3. Inicializace komponent
    print("Initializing Core Logic...")
    controller = BankController()  # Načte data.json

    print("Initializing Network Layer...")
    server = BankServer(HOST, port, controller, timeout=TIMEOUT)

    # 4. Registrace "záchranné brzdy" (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)

    # 5. Start Serveru
    print("------------------------------------------")
    print(f"My IP: {controller.my_ip}")
    print("Ready to accept connections. Press Ctrl+C to stop.")
    print("------------------------------------------")
    
    # Toto zablokuje hlavní vlákno, dokud server neběží
    server.start()

if __name__ == "__main__":
    main()