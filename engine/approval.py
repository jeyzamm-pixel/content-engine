"""Zgoda przywiązana do treści: odcisk sha256 pary obraz + tekst."""
import hashlib


def odcisk(obraz: str, tresc: str) -> str:
    """Zgoda dotyczy dokładnie tej pary obraz + tekst. Zmiana czegokolwiek = brak zgody."""
    return hashlib.sha256(f"{obraz}\n{tresc.strip()}".encode("utf-8")).hexdigest()


def mozna_publikowac(wpis: dict, zgody: dict) -> bool:
    zgoda = zgody.get(wpis["id"])
    return bool(zgoda) and zgoda.get("werdykt") != "odrzucony" \
        and zgoda.get("odcisk") == odcisk(wpis["obraz"], wpis["tresc"])


def zatwierdz(wpis: dict, zgody: dict, kto: str) -> None:
    """Zapisuje zgodę na bieżącą treść wpisu."""
    zgody[wpis["id"]] = {"werdykt": "przyjety", "kto": kto,
                         "odcisk": odcisk(wpis["obraz"], wpis["tresc"])}


def weto(wpis_id: str, zgody: dict, kto: str) -> None:
    """Sprzeciw jednym kliknięciem: wpis nie wyjdzie, dopóki ktoś go nie przywróci."""
    stara = zgody.get(wpis_id, {})
    zgody[wpis_id] = {**stara, "werdykt": "odrzucony", "kto": kto}


def przywroc(wpis: dict, zgody: dict, kto: str) -> None:
    """Przywrócenie liczy się jako nowa zgoda, więc odcisk jest liczony od nowa."""
    zatwierdz(wpis, zgody, kto)
