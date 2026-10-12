"""Sędzia: ocena tekstu innym modelem niż autor.

W repozytorium sędzia jest regułowy (bez wywołania API), żeby przykład działał offline.
Kontrakt jest ten sam co w produkcji: sędzia zwraca werdykt i listę powodów, a jego
model musi być inny niż model autora.
"""

ZAKAZANE_ZNAKI = {"\N{EM DASH}": "myślnik", "\N{EN DASH}": "półpauza"}
OBIETNICE = ("gwarantujemy", "100%", "najlepsza w polsce", "zero ryzyka")
MAX_DLUGOSC = 400
MAX_HASZTAGOW = 5


class TenSamModel(ValueError):
    """Sędzia i autor nie mogą być tym samym modelem."""


def sedzia(wpis: dict, model_sedziego: str) -> dict:
    if model_sedziego == wpis.get("model_autora"):
        raise TenSamModel(f"sędzia i autor używają {model_sedziego}")
    tekst = wpis["tresc"]
    powody = []
    for znak, opis in ZAKAZANE_ZNAKI.items():
        if znak in tekst:
            powody.append(f"zakazany znak: {opis}")
    for fraza in OBIETNICE:
        if fraza in tekst.lower():
            powody.append(f"obietnica efektu: {fraza}")
    if len(tekst) > MAX_DLUGOSC:
        powody.append("za długi tekst")
    if tekst.count("#") > MAX_HASZTAGOW:
        powody.append("za dużo hasztagów")
    if not wpis.get("obraz"):
        powody.append("brak obrazu")
    return {"werdykt": "odrzucony" if powody else "przyjety", "powody": powody,
            "sedzia": model_sedziego}
