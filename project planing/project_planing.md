1. Vrstva: Data Management (Persistence Layer)

Tohle je základna. Musí být neprůstřelná.

    Co to dělá: Stará se o data na disku a v paměti. Řeší atomicitu a zamykání vláken.

     Znovupoužitelná část (Generic): ThreadSafeJsonStorage

        Napíšeme třídu, která neví nic o bance. Je jí jedno, jestli ukládá účty, nebo seznam nákupů.

        Funkce: load(), save(data), get(key), set(key, value).

        Vychytávky:

            Má v sobě threading.RLock, takže je bezpečná pro více vláken.

            Implementuje atomický zápis (přes temp soubor + rename), aby se data nepoškodila při pádu.

     Bankovní část (Specific): BankRepository

        Dědí nebo využívá ThreadSafeJsonStorage.

        Teprve tady jsou metody jako deposit_money, withdraw_money, create_account. Ty už volají ty obecné metody nad konkrétními daty.

2. Vrstva: Core Logic (Business Layer)

Mozek aplikace. Zde se rozhoduje, co se stane.

    Co to dělá: Validuje vstupy a řídí procesy (lokální vs. proxy).

     Znovupoužitelná část (Generic): CommandProcessor & I18nProvider (Lokalizace)

        I18nProvider: Třída, která načte JSON/slovník s překlady (CZ, EN, FR). Má metodu translate(key, lang). Tohle použiješ v každém svém budoucím projektu.

        CommandProcessor: Abstraktní třída, která umí vzít řádku textu, rozsekat ji podle mezer a zavolat příslušnou funkci.

     Bankovní část (Specific): BankController

        Implementuje logiku příkazů AC, BC, AD...

        Zde bude logika: "Když je IP moje, volej BankRepository. Když je cizí, volej NetworkClient."

        Zde bude logika pro Robbery Plan (procházení seznamu bank).

3. Vrstva: Networking (Communication Layer)

Brána do světa. Musí být robustní a blbuvzdorná.

    Co to dělá: Otevírá porty, spravuje vlákna, hlídá timeouty.

     Znovupoužitelná část (Generic): ThreadedTCPServer

        Zase – třída, která neví, že je banka.

        Umí:

            Nastartovat server na daném portu.

            Přijmout klienta.

            Spustit pro něj vlákno.

            Hlídat Timeouty (to je v zadání klíčové!).

            Logovat připojení/odpojení.

     Bankovní část (Specific): BankProtocolHandler

        Funkce, kterou ten server zavolá, když přijde zpráva.

        Tato funkce jen předá data do BankControlleru a pošle odpověď zpátky klientovi.

4. Vrstva: Utilities (Cross-Cutting Concerns)

Pomocníci, kteří prostupují celou aplikací.

     Znovupoužitelné části:

        CustomLogger: Třída obalující standardní Python logging. Nastaví formátování (čas, thread ID, level) a logování do souboru i konzole. Zadání vyžaduje, aby bylo z logu jasné, co se děje.

        ConfigLoader: Třída pro načtení konfigurace (Port, Timeout, IP sousedů) z argumentů příkazové řádky nebo .env souboru.

Vizualizace toku dat (Sequence)

Abychom si ověřili, že to dává smysl, podívejme se, co se stane, když přijde příkaz AD 10001/10.1.2.3 500:

    Networking (ThreadedTCPServer): Přijme bajty, dekóduje na String (UTF-8). Předá to dál.

    Logic (BankController):

        Parsuje text. Vidí AD.

        Koukne na IP 10.1.2.3.

        Je to moje IP? -> ANO.

    Data (BankRepository -> ThreadSafeJsonStorage):

        Zamkne zámek (Lock).

        Načte zůstatek. Přičte 500. Uloží.

        Odemkne zámek.

    Logic (I18nProvider): Vybere správnou odpověď (např. jen "AD" nebo chybovou hlášku ve francouzštině, pokud by to selhalo).

    Networking: Odešle odpověď klientovi.