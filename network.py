import socket
import threading
from shared import i18n

class BankServer:
    """
    Síťová vrstva serveru.
    Stará se o přijímání spojení a vytváření vláken pro klienty.
    """
    def __init__(self, host, port, controller, timeout=5.0):
        self.host = host
        self.port = port
        self.controller = controller  # Instance BankController z logic.py
        self.timeout = timeout
        self.server_socket = None
        self.is_running = False

    def start(self):
        """Spustí hlavní smyčku serveru."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # DŮLEŽITÉ: SO_REUSEADDR umožní restartovat server okamžitě po vypnutí
            # bez čekání na uvolnění portu operačním systémem.
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5) # Fronta pro 5 čekajících spojení
            self.is_running = True

            print(f"Server naslouchá na {self.host}:{self.port}...")
            print(f"{i18n.get('MSG_SERVER_STARTED')} {self.port}")

            while self.is_running:
                try:
                    # Hlavní vlákno zde "visí" a čeká na nového klienta
                    client_sock, addr = self.server_socket.accept()
                    
                    # Jakmile se někdo připojí, okamžitě pro něj vyrobíme vlákno
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_sock, addr)
                    )
                    # Daemon = True zajistí, že se vlákna ukončí, když vypneme hlavní program
                    client_thread.daemon = True 
                    client_thread.start()
                    
                except OSError:
                    # Nastane při vypínání serveru (socket se zavře)
                    break
                except Exception as e:
                    print(f"[SERVER ERROR] {e}")

        except Exception as e:
            print(f"[CRITICAL] Nepodařilo se spustit server: {e}")
        finally:
            self.stop()

    def stop(self):
        """Bezpečně ukončí server."""
        self.is_running = False
        if self.server_socket:
            self.server_socket.close()

    def handle_client(self, conn, addr):
        """
        Logika pro obsluhu jednoho konkrétního klienta.
        Běží ve vlastním vlákně.
        """
        ip, port = addr
        print(f"[NEW CONNECTION] {ip}:{port}")
        
        # Nastavení timeoutu pro toto spojení (podle zadání)
        conn.settimeout(self.timeout)

        try:
            while True:
                # Čekáme na data. 1024 bytů je pro textové příkazy až až.
                data = conn.recv(1024)
                
                if not data:
                    # Pokud přišlo "nic", znamená to, že klient ukončil spojení.
                    break
                
                # Dekódování a zpracování
                command_text = data.decode('utf-8').strip()
                if not command_text:
                    continue # Ignorujeme prázdné řádky
                
                print(f"[{ip}] RECV: {command_text}")
                
                # Zde voláme MOZEK (logic.py)
                response_text = self.controller.process_command(command_text)
                
                # Odeslání odpovědi
                conn.sendall((response_text + "\n").encode('utf-8'))
                print(f"[{ip}] SENT: {response_text}")

        except socket.timeout:
            print(f"[{ip}] TIMEOUT - klient byl příliš dlouho neaktivní.")
        except ConnectionResetError:
            print(f"[{ip}] DISCONNECT - klient násilně ukončil spojení.")
        except Exception as e:
            print(f"[{ip}] ERROR: {e}")
        finally:
            conn.close()
            print(f"[{ip}] Spojení uzavřeno.")