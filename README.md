# Gemini AI agent – konverzační verze

Tento projekt používá Gemini API, uchovává historii konverzace během běhu programu
a nabízí Gemini Python nástroj `calculate` pro základní matematické výpočty.

## 1. Nastav API klíč

Vytvoř v této složce soubor `.env` s tímto obsahem:

```text
GEMINI_API_KEY=SEM_VLOZ_SVUJ_GEMINI_API_KLIC
```

## 2. Instalace (Windows / PowerShell)

Otevři terminál v této složce a spusť:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 3. Spuštění

```powershell
.\.venv\Scripts\python.exe main.py
```

Můžeš zadávat více otázek v jedné relaci. Agent si v rámci běžícího programu
uchovává historii, takže rozumí navazujícím otázkám. Pro ukončení napiš `konec`.

## Příklady

- `Kolik je 5 krát 7?`
- `A kolik je tento výsledek krát 10?`
- `Napiš mi krátký vtip.`

Při matematických otázkách se agent pokusí použít nástroj `calculate`.
V terminálu se objeví zpráva, když Python tuto funkci spustí.

## Poznámky

- Gemini API má vlastní limity používání a případné poplatky.
- Pokud Google vrátí dočasnou chybu 503, program požadavek několikrát zopakuje.
- Historie se uchovává pouze do ukončení programu.
