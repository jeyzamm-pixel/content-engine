"""Redaktor: utrzymuje obsadzone najbliższe dni.

W produkcji tekst pisze model językowy, a obraz generator z referencjami stylu marki.
Tu redaktor składa tekst z banku pomysłów (szablony), żeby przykład działał bez kluczy.
"""
from datetime import date, datetime, timedelta

RYTM = {0: "09:00", 2: "09:00", 4: "09:00"}  # poniedziałek, środa, piątek

BANK = [
    ("zakwas", "Zakwas żyje od 2011 roku i co rano dostaje świeżą mąkę. Dlatego chleb pachnie tak, a nie inaczej."),
    ("tort", "Tort na zamówienie przyjmujemy z trzydniowym wyprzedzeniem. Napisz, na ile osób, a my dobierzemy blachę."),
    ("poranek", "Pierwsza blacha wychodzi o 5:40. Jeśli czujesz zapach na ulicy, to właśnie ona."),
    ("bulki", "Bułki pszenne, grahamki i kajzerki. Zamów wieczorem, odbierz rano, jeszcze ciepłe."),
    ("drozdzowka", "Drożdżówka z serem robiona według przepisu babci założycielki. Bez ulepszaczy."),
    ("chleb-zytni", "Żytni na zakwasie dojrzewa 18 godzin. Dłużej niż większość ludzi śpi."),
]


def brakujace_sloty(kolejka: list, od: date, dni: int = 7) -> list:
    """Wykrywa z wyprzedzeniem dni z rytmu tygodnia, na które nic nie zaplanowano."""
    zajete = {w["kiedy"][:10] for w in kolejka if w["status"] != "wycofany"}
    wynik = []
    for i in range(dni):
        d = od + timedelta(days=i)
        if d.weekday() in RYTM and d.isoformat() not in zajete:
            wynik.append(datetime.fromisoformat(f"{d.isoformat()}T{RYTM[d.weekday()]}"))
    return wynik


def uzupelnij(kolejka: list, od: date, model_autora: str = "<model-autor>", dni: int = 7) -> list:
    """Dokłada wpisy na puste sloty. Zwraca nowe wpisy."""
    uzyte = {w.get("temat") for w in kolejka}
    wolne = [b for b in BANK if b[0] not in uzyte] or BANK
    nowe = []
    for i, slot in enumerate(brakujace_sloty(kolejka, od, dni)):
        temat, tresc = wolne[i % len(wolne)]
        wpis = {"id": f"p-{slot:%Y%m%d}", "kiedy": slot.isoformat(), "temat": temat,
                "obraz": f"grafiki/{temat}.png", "tresc": tresc, "status": "zaplanowany",
                "model_autora": model_autora}
        nowe.append(wpis)
    kolejka.extend(nowe)
    return nowe
