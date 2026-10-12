"""Publikator: wychodzi tylko treść z pasującą zgodą; po błędzie najpierw sprawdza, czy post jednak wyszedł."""
from datetime import datetime

from .approval import mozna_publikowac


class SymulowanaPlatforma:
    """Zastępuje Facebook/Instagram. Tryby błędu odtwarzają prawdziwy kłopot:
    API potrafi zgłosić błąd, choć post już wyszedł."""

    def __init__(self, tryb: dict | None = None):
        self.tryb = tryb or {}          # id -> 'ok' | 'blad_ale_wyszlo' | 'blad_raz' | 'blad'
        self.wyszlo = {}                # id -> liczba publikacji (wykrywa duble)
        self._proby = {}

    def publikuj(self, wpis: dict) -> None:
        t = self.tryb.get(wpis["id"], "ok")
        n = self._proby[wpis["id"]] = self._proby.get(wpis["id"], 0) + 1
        if t == "blad":
            raise RuntimeError("platforma niedostępna")
        if t == "blad_raz" and n == 1:
            raise RuntimeError("chwilowy błąd platformy")
        self.wyszlo[wpis["id"]] = self.wyszlo.get(wpis["id"], 0) + 1
        if t == "blad_ale_wyszlo":
            raise TimeoutError("limit czasu po stronie platformy")

    def czy_jest(self, wpis_id: str) -> bool:
        return self.wyszlo.get(wpis_id, 0) > 0


def publikuj_zaplanowane(kolejka: list, zgody: dict, platforma, chwila: datetime, decyzje: list) -> list:
    """Zwraca listę zdarzeń. Zmienia status wpisów w miejscu."""
    zdarzenia = []
    for w in kolejka:
        if w["status"] != "zaplanowany" or datetime.fromisoformat(w["kiedy"]) > chwila:
            continue
        if not mozna_publikowac(w, zgody):
            w["status"] = "wstrzymany"
            zdarzenia.append((w["id"], "wstrzymany", "brak zgody dla tej treści"))
            continue
        for proba in (1, 2):
            try:
                platforma.publikuj(w)
                w["status"] = "opublikowany"
                zdarzenia.append((w["id"], "opublikowany", f"próba {proba}"))
                break
            except Exception as e:  # noqa: BLE001  (celowo szeroko: każda awaria wymaga weryfikacji)
                if platforma.czy_jest(w["id"]):
                    # błąd był fałszywy: post wyszedł, więc NIE ponawiamy (żadnych dubli)
                    w["status"] = "opublikowany"
                    zdarzenia.append((w["id"], "opublikowany", f"po błędzie ({e}), potwierdzone w platformie"))
                    break
                if proba == 2:
                    w["status"] = "blad"
                    decyzje.append({"typ": "brak_publikacji", "wpis": w["id"], "powod": str(e)})
                    zdarzenia.append((w["id"], "blad", f"nie wyszło po 2 próbach: {e}"))
    return zdarzenia
