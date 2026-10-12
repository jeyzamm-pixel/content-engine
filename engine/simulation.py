"""Scenariusz demo: dwa tygodnie kolejki firmy fikcyjnej, ze wszystkimi trudnymi przypadkami naraz."""
from datetime import date, datetime

from .approval import odcisk, przywroc, weto, zatwierdz  # noqa: F401
from .editor import uzupelnij
from .judge import sedzia
from .publisher import SymulowanaPlatforma, publikuj_zaplanowane

MODEL_SEDZIEGO = "<model-sedzia>"


def symuluj():
    kolejka, zgody, decyzje = [], {}, []
    uzupelnij(kolejka, date(2026, 10, 12), dni=17)

    # sędzia ocenia każdy wpis; przyjęte dostają zgodę z odciskiem treści
    kolejka[5]["tresc"] += " Nasza piekarnia \N{EM DASH} najlepsza w Polsce, gwarantujemy!"
    for w in kolejka:
        ocena = sedzia(w, MODEL_SEDZIEGO)
        w["ocena"] = ocena
        if ocena["werdykt"] == "przyjety":
            zatwierdz(w, zgody, kto=MODEL_SEDZIEGO)
        else:
            zgody[w["id"]] = {"werdykt": "odrzucony", "kto": MODEL_SEDZIEGO, "odcisk": ""}

    # człowiek: sprzeciw jednym kliknięciem wobec jednego wpisu
    weto(kolejka[3]["id"], zgody, kto="wlasciciel")
    # ktoś poprawia tekst już po zatwierdzeniu: zgoda przestaje pasować
    kolejka[4]["tresc"] = kolejka[4]["tresc"].replace("Zamów", "Zamawiaj")
    kolejka[4]["tresc"] += " Dodane po zatwierdzeniu."

    platforma = SymulowanaPlatforma({
        kolejka[1]["id"]: "blad_ale_wyszlo",   # API krzyczy, post wyszedł: nie wolno dublować
        kolejka[2]["id"]: "blad_raz",          # chwilowy błąd: druga próba przechodzi
        kolejka[6]["id"]: "blad",              # platforma leży: decyzja w panelu
    })
    zdarzenia = publikuj_zaplanowane(kolejka, zgody, platforma, datetime(2026, 10, 29, 12, 0), decyzje)
    return kolejka, zgody, zdarzenia, decyzje, platforma
