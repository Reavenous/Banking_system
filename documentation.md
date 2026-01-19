# P2P Bank Node (Hacker Edition)

**Autor:** Alexandre Basseville  
**Jazyk:** Python 3.x  

---

## 1. Architektura aplikace

Aplikace je navržena jako **vícevláknový TCP server** s **modulární architekturou**, která striktně odděluje:

- síťovou komunikaci  
- byznys logiku  
- správu dat  

Toto rozdělení zajišťuje přehlednost kódu a splňuje požadavek na **fyzickou paralelizaci** (samostatná vlákna pro klienty).

---

### Schéma zapojení (Data Flow)

> *(Zde vlož vybraný diagram – např. Mermaid render nebo obrázek z Draw.io)*

---

### Struktura modulů

#### `main.py`
- Vstupní bod aplikace  
- Inicializuje konfiguraci  
- Volí jazyk  
- Spouští server  

#### `network.py`
- Síťová vrstva  
- Obsahuje `BankServer`, který:
  - pro každého příchozího klienta startuje nové vlákno (`threading.Thread`)
  - řeší timeouty
  - zajišťuje stabilitu spojení  

#### `logic.py`
- Mozek aplikace (`BankController`)
- Rozparsuje textové příkazy
- Rozhoduje:
  - zda příkaz vykonat lokálně (zápis do dat)
  - nebo jej přesměrovat (Proxy)

#### `hacker.py`
- Klientský modul
- Obsahuje logiku:
  - pro připojení k cizím uzlům (Proxy)
  - algoritmus plánování loupeže (**RP – Robbery Planner**)
- Skenuje síť a vybírá cíle

#### `shared.py`
- Sdílené knihovny  
- Viz sekce **Znovupoužití kódu**

---

## 2. Znovupoužití kódu (Reusable Code)

V souladu se zadáním byly vytvořeny **univerzální komponenty**, které:

- nejsou závislé na bankovní logice
- lze je využít i v dalších projektech

Tyto komponenty se nacházejí v souboru `shared.py`.

---

### `LocalizationManager`

Třída pro správu **vícejazyčných aplikací**.

**Vlastnosti:**
- Dynamické přepínání jazyků (CZ / EN / FR)
- Oddělení textových řetězců od logiky kódu
- Snadná rozšiřitelnost o další jazyky

---

### `ThreadSafeJsonStorage`

Generická třída pro **perzistentní ukládání dat do JSON**.

**Klíčové vlastnosti:**

- **Thread Safety**  
  - Řešeno pomocí `threading.RLock()`

- **Atomic Save**  
  - Zápis do dočasného souboru  
  - Následné atomické přejmenování  
  - Ochrana dat při pádu aplikace

---

## 3. Použité zdroje a AI

Při vývoji a návrhu architektury byl využit **AI asistent (LLM)**.

- **AI Model:** Google Gemini  
- **Způsob použití:**
  - konzultace návrhových vzorů (Controller–Service pattern)
  - generování Mermaid diagramů pro vizualizaci architektury
  - debugging síťové komunikace (Telnet vs. raw sockets)
  - optimalizace algoritmu *Robbery Planner*

- **Promptování:**
  - Iterativní vývoj
  - Postupné ladění implementace
  - Řešení okrajových případů (např. `UnicodeDecodeError` při chybném kódování klienta)

**Odkaz na konverzaci s AI:**  
[Gemini Chat Log](https://gemini.google.com/app/3f22d5c7c0ff6ff7?hl=cs)

---
