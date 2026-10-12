import sys
from datetime import date, datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine import approval, editor, judge, publisher, simulation  # noqa: E402


def wpis(**kw):
    base = {"id": "p-1", "kiedy": "2026-10-12T09:00", "obraz": "grafiki/a.png",
            "tresc": "Chleb z zakwasem.", "status": "zaplanowany", "model_autora": "A"}
    base.update(kw)
    return base


def test_odcisk_zalezy_od_obrazu_i_tekstu():
    a = approval.odcisk("a.png", "tekst")
    assert a == approval.odcisk("a.png", "  tekst  ")      # białe znaki na brzegach nie liczą się
    assert a != approval.odcisk("b.png", "tekst")
    assert a != approval.odcisk("a.png", "tekst2")


def test_zmiana_tekstu_po_zatwierdzeniu_uniewaznia_zgode():
    w, z = wpis(), {}
    approval.zatwierdz(w, z, "x")
    assert approval.mozna_publikowac(w, z)
    w["tresc"] += " Dopisek."
    assert not approval.mozna_publikowac(w, z)


def test_zmiana_obrazu_uniewaznia_zgode():
    w, z = wpis(), {}
    approval.zatwierdz(w, z, "x")
    w["obraz"] = "grafiki/inny.png"
    assert not approval.mozna_publikowac(w, z)


def test_brak_zgody_blokuje():
    assert not approval.mozna_publikowac(wpis(), {})


def test_weto_blokuje_a_przywrocenie_odblokowuje():
    w, z = wpis(), {}
    approval.zatwierdz(w, z, "x")
    approval.weto(w["id"], z, "wlasciciel")
    assert not approval.mozna_publikowac(w, z)
    approval.przywroc(w, z, "wlasciciel")
    assert approval.mozna_publikowac(w, z)


def test_sedzia_nie_moze_byc_tym_samym_modelem_co_autor():
    with pytest.raises(judge.TenSamModel):
        judge.sedzia(wpis(model_autora="M"), "M")


def test_sedzia_lapie_myslnik_i_obietnice():
    w = wpis(tresc="Najlepszy chleb \N{EM DASH} gwarantujemy smak.")
    o = judge.sedzia(w, "B")
    assert o["werdykt"] == "odrzucony"
    assert any("myślnik" in p for p in o["powody"]) and any("obietnica" in p for p in o["powody"])


def test_sedzia_przepuszcza_czysty_tekst():
    assert judge.sedzia(wpis(), "B")["werdykt"] == "przyjety"


def test_redaktor_wykrywa_puste_sloty_i_je_obsadza():
    k = []
    sloty = editor.brakujace_sloty(k, date(2026, 10, 12), dni=7)
    assert [s.weekday() for s in sloty] == [0, 2, 4]
    editor.uzupelnij(k, date(2026, 10, 12), dni=7)
    assert editor.brakujace_sloty(k, date(2026, 10, 12), dni=7) == []


def test_publikacja_po_falszywym_bledzie_nie_robi_dubla():
    w, z, dec = wpis(), {}, []
    approval.zatwierdz(w, z, "x")
    p = publisher.SymulowanaPlatforma({"p-1": "blad_ale_wyszlo"})
    publisher.publikuj_zaplanowane([w], z, p, datetime(2026, 10, 13), dec)
    assert w["status"] == "opublikowany"
    assert p.wyszlo["p-1"] == 1 and dec == []


def test_chwilowy_blad_jest_ponawiany_raz():
    w, z, dec = wpis(), {}, []
    approval.zatwierdz(w, z, "x")
    p = publisher.SymulowanaPlatforma({"p-1": "blad_raz"})
    publisher.publikuj_zaplanowane([w], z, p, datetime(2026, 10, 13), dec)
    assert w["status"] == "opublikowany" and p.wyszlo["p-1"] == 1


def test_trwala_awaria_zaklada_decyzje():
    w, z, dec = wpis(), {}, []
    approval.zatwierdz(w, z, "x")
    publisher.publikuj_zaplanowane([w], z, publisher.SymulowanaPlatforma({"p-1": "blad"}),
                                   datetime(2026, 10, 13), dec)
    assert w["status"] == "blad" and dec[0]["typ"] == "brak_publikacji"


def test_przyszly_wpis_nie_wychodzi():
    w, z = wpis(kiedy="2026-12-01T09:00"), {}
    approval.zatwierdz(w, z, "x")
    publisher.publikuj_zaplanowane([w], z, publisher.SymulowanaPlatforma(), datetime(2026, 10, 13), [])
    assert w["status"] == "zaplanowany"


def test_scenariusz_demo_daje_oczekiwane_statusy():
    kolejka, _, _, decyzje, platforma = simulation.symuluj()
    st = [w["status"] for w in kolejka]
    assert st == ["opublikowany", "opublikowany", "opublikowany", "wstrzymany",
                  "wstrzymany", "wstrzymany", "blad", "opublikowany"]
    assert max(platforma.wyszlo.values()) == 1          # nigdzie dubla
    assert len(decyzje) == 1
