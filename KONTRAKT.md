# Kontrakt kolejki

Pola wpisu są zamrożone. Zmiana nazwy pola obrazu albo tekstu zmienia odcisk i unieważnia wszystkie zgody.

| Pole | Znaczenie |
|---|---|
| id | stały identyfikator wpisu |
| kiedy | data i godzina publikacji (ISO 8601) |
| temat | etykieta z banku pomysłów |
| obraz | ścieżka grafiki, część odcisku |
| tresc | tekst posta, część odcisku |
| status | zaplanowany, opublikowany, wstrzymany, blad |
| model_autora | etykieta modelu autora (sędzia musi mieć inną) |

Odcisk zgody: `sha256(obraz + "\n" + tresc.strip())`.
