#  P2P Bank Node (Hacker Edition)

**Autor:** Alexandre Basseville  
**Jazyk:** Python 3.x  
**Verze:** 1.0 (Hacker Level)

---

##  Popis projektu

Tato aplikace je implementací **P2P bankovního uzlu (Node)** podle architektury *peer-to-peer*.  
Každá instance aplikace funguje jako **samostatná banka**, která:

- spravuje účty klientů,
- komunikuje s ostatními bankami v síti,
- dokáže přeposílat příkazy mezi uzly.

Projekt splňuje požadavky na úroveň **HACKER**, což zahrnuje:

1. **Základní operace**  
   Zakládání účtů, vklady, výběry (`AC`, `AD`, `AW`, …)

2. **Proxy funkcionalita**  
   Přeposílání příkazů do cizích bank, pokud IP adresa neodpovídá lokálnímu uzlu.

3. **Robbery Plan (RP)**  
   Algoritmus pro automatické skenování sítě a plánování loupeže s cílem:
   - maximalizovat zisk
   - minimalizovat počet poškozených klientů

---

##  Funkce a vlastnosti

- **Vícevláknový server**  
  Využívá `threading` pro paralelní obsluhu více klientů současně.

- **Odolná architektura**  
  Striktní oddělení:
  - síťové vrstvy
  - aplikační logiky
  - datové vrstvy

- **Bezpečná data**  
  Implementace **atomického zápisu** do souboru (*Atomic Save*), která zabraňuje
  poškození databáze při pádu aplikace.

- **Lokalizace**  
  Podpora dynamického přepínání jazyků:
  - 🇨🇿 CZ
  - 🇬🇧 EN
  - 🇫🇷 FR

- **Smart Networking**  
  - Ošetření `Telnet` handshake znaků  
  - Robustní timeouty a síťová stabilita

---

##  Instalace a spuštění

### Požadavky

- Python **3.6** nebo novější
- Pouze standardní knihovna  
  *(není potřeba `pip install`)*

---

###  Spuštění aplikace

1. Otevřete terminál ve složce projektu
2. Spusťte hlavní skript:

```bash
python main.py
```
3.  Postupujte podle pokynů na obrazovce:
    * Zvolte jazyk (default: `cs`).
    * Potvrďte port (default: `65525`).

### Konfigurace sousedů (pro Robbery Plan)
Pro funkčnost příkazu `RP` (Loupež) vytvořte v kořenovém adresáři soubor `peers.txt` a vložte do něj IP adresy ostatních bank (každou na nový řádek).
Příklad `peers.txt`:

```text
192.168.1.15
10.0.0.5
127.0.0.1
```

##  Ovládání a Příkazy

K aplikaci se připojte pomocí **PuTTY** (typ spojení: *Raw*) nebo přes **netcat**.

| Kód | Příkaz | Popis | Příklad |
| :--- | :--- | :--- | :--- |
| **BC** | Bank Code | Vrátí IP adresu banky. | `BC` |
| **AC** | Account Create | Vytvoří nový účet. Vrátí Číslo/IP. | `AC` |
| **AD** | Account Deposit | Vloží peníze na účet. | `AD 10001/10.0.0.1 500` |
| **AW** | Account Withdraw | Vybere peníze z účtu. | `AW 10001/10.0.0.1 200` |
| **AB** | Account Balance | Zobrazí zůstatek. | `AB 10001/10.0.0.1` |
| **AR** | Account Remove | Smaže prázdný účet. | `AR 10001/10.0.0.1` |
| **BA** | Bank Amount | Celková suma peněz v bance. | `BA` |
| **BN** | Bank Number | Počet klientů v bance. | `BN` |
| **RP** | Robbery Plan | (Hacker) Naplánuje loupež v síti. | `RP 1000000` |

---

##  Architektura Kódu

Projekt je rozdělen do modulů pro snadnou údržbu a rozšiřitelnost:

* **`main.py`**: Vstupní bod, inicializace a konfigurace.
* **`network.py`**: TCP Listener, správa vláken a síťová komunikace.
* **`logic.py`**: Business logika, parsování příkazů a routing (Local vs Proxy).
* **`hacker.py`**: Klientský modul pro připojení k cizím uzlům a logika loupeže.
* **`shared.py`**: Univerzální sdílené nástroje (Lokalizace, ThreadSafe Storage).
* **`data.json`**: Persistentní úložiště účtů (vytváří se automaticky).

---

> Vytvořeno jako projekt pro předmět Programové vybavení.
