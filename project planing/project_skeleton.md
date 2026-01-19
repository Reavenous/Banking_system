1. shared.py (Univerzální dílna)

    Obsah: Třídy LocalizationManager (překlady) a ThreadSafeJsonStorage (atomické ukládání).

    Závislost: Nezávisí na ničem. Ostatní závisí na něm.

2. logic.py (Bankovní úředník)

    Obsah: Třída BankController.

    Co dělá:

        Obsahuje metody jako create_account, deposit, get_balance.

        Jako jediná sahá na data (ThreadSafeJsonStorage).

        Zde bude rozhodovací strom: "Je to příkaz BC? -> Vrať IP."

        Spolupracuje s hacker.py, když zjistí, že IP adresa v příkazu není naše.

3. network.py (Spojovatelka)

    Obsah: Třída BankServer a funkce handle_client.

    Co dělá:

        Otevře port (socket bind/listen).

        Ve smyčce přijímá klienty.

        Pro každého klienta spustí vlákno.

        Hlídá timeouty (aby se vlákno nezaseklo).

        Přijme "surový text", předá ho do logic.py a výsledek pošle zpět.

4. hacker.py (Agent v terénu)

    Obsah: Třída NetworkClient a RobberyPlanner.

    Co dělá:

        Obsahuje funkci pro připojení k cizí bance (socket connect).

        Proxy: Když logic.py řekne "tohle není pro nás", hacker.py to pošle dál.

        Robbery: Obsahuje algoritmus, který oběhne IP adresy, posbírá zůstatky a naplánuje loupež.

5. main.py (Generální ředitel)

    Obsah: Spouštěcí kód.

    Co dělá:

        Zeptá se uživatele na jazyk (CZ/EN/FR).

        Nastaví port a timeout.

        Vytvoří instance BankController a BankServer.

        Spustí to celé (server.start()).