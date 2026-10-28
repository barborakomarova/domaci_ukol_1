import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise SystemExit(
        "Chybí GEMINI_API_KEY. Vytvoř v projektu soubor .env "
        "a vlož do něj svůj Gemini API klíč."
    )

client = genai.Client(api_key=api_key)

# Používáme model, který je uvedený v aktuální dokumentaci Gemini API.
MODEL = "gemini-3.5-flash"

SYSTEM_INSTRUCTION = """
Jsi užitečný asistent a odpovídáš česky.
Pamatuj si kontext celé probíhající konverzace a rozuměj navazujícím otázkám.
Pokud uživatel žádá o matematický výpočet, použij nástroj calculate.
Do parametru expression vlož pouze matematický výraz, například 17*850.
Nesnaž se výsledek výpočtu odhadovat, pokud můžeš použít nástroj.
Pokud nástroj vrátí chybu, vysvětli ji uživateli.
Odpovídej přirozeně a stručně.
"""


def calculate(expression: str) -> str:
    """Safely calculate a basic arithmetic expression.

    Args:
        expression: Mathematical expression using numbers, +, -, *, /,
            parentheses and decimal points.
    """
    allowed = set("0123456789+-*/(). ")

    if not expression or any(char not in allowed for char in expression):
        return "Chyba: výraz obsahuje nepovolené znaky."

    print(f"\n  [Nástroj calculate] Python počítá výraz: {expression}")

    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except ZeroDivisionError:
        return "Chyba: nelze dělit nulou."
    except Exception:
        return "Chyba: výraz se nepodařilo vypočítat."


def send_with_retries(chat, message: str) -> str:
    """Send a message and retry a few times on temporary server errors."""
    for attempt in range(3):
        try:
            response = chat.send_message(message)
            return response.text or "Model nevrátil textovou odpověď."
        except Exception as exc:
            error_message = str(exc).upper()
            temporary_error = (
                "503" in error_message
                or "UNAVAILABLE" in error_message
                or "INTERNAL SERVER ERROR" in error_message
            )

            if temporary_error and attempt < 2:
                wait_seconds = 2 ** (attempt + 1)
                print(
                    f"\nGemini je dočasně nedostupné. "
                    f"Další pokus za {wait_seconds} sekund..."
                )
                time.sleep(wait_seconds)
                continue
            raise


def main() -> None:
    chat = client.chats.create(
        model=MODEL,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=[calculate],
        ),
    )

    print("=" * 55)
    print("Tvůj Gemini AI agent je připraven!")
    print("Můžeš pokládat navazující otázky.")
    print("Pro ukončení napiš: konec")
    print("=" * 55)

    while True:
        try:
            question = input("\nTy: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nProgram ukončen.")
            break

        if not question:
            print("Napiš prosím otázku.")
            continue

        if question.lower() in {"konec", "exit", "quit"}:
            print("Program ukončen. Díky za konverzaci!")
            break

        try:
            answer = send_with_retries(chat, question)
            print(f"\nGemini: {answer}")
        except Exception as exc:
            error_message = str(exc)
            upper_error = error_message.upper()

            print("\nPožadavek se nepodařilo dokončit.")
            if "503" in error_message or "UNAVAILABLE" in upper_error:
                print(
                    "Model Gemini je momentálně nedostupný. "
                    "Zkus to prosím za chvíli znovu."
                )
            elif "429" in error_message:
                print(
                    "Byl dosažen limit API nebo je požadavků příliš mnoho. "
                    "Zkontroluj limity svého bezplatného tarifu."
                )
            else:
                print(f"Podrobnosti chyby: {error_message}")


if __name__ == "__main__":
    main()
