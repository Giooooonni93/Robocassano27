"""Prova del VERDE IN FONDO ALLA DISCESA (FIX 115, scatola nera 13/11 V48, 75-125 s).

Pista piccola: salita 21 gradi, piano, discesa 21 gradi e in fondo un incrocio a + con i due verdi in DIAGONALE
(valido a sinistra prima dell'incrocio, falso a destra dopo), come la piastrella della scuola. Il percorso giusto
va a SINISTRA e finisce sulla linea rossa; il ramo dritto finisce nel nulla.
Il simulatore non si tocca: la pista si aggiunge solo dentro questo script.

Uso: python3 prova_verde_discesa.py <cartella versione> [semi] [discesa|salita]   es.  ../ClaudeRob_V50 1,2,3 salita
Con "salita" l'incrocio è in CIMA a una salita di 21 gradi (V51, FIX 118: la rotonda in cima alla rampa).
"""
import json
import os
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
SIM = max((os.path.join(QUI, "..", d) for d in os.listdir(os.path.join(QUI, ".."))
           if d.startswith("ClaudeRob_Simulatore_V")), key=lambda d: int(d.rsplit("_V", 1)[1]))

GARA = r'''
import sys, json
sys.path.insert(0, sys.argv[1])
import piastrelle as P, campo, esegui
MODO = sys.argv[6] if len(sys.argv) > 6 else "discesa"
CENTRO_Y = 105

def pista():
    K = P.Costruttore(6, 11)
    K.inizia(3, 10, 0)
    m = K.metti
    m("partenza", cp=True)
    m("dritto")
    if MODO == "salita":                       # [V51] + coi verdi in diagonale in CIMA alla salita (la rotonda della scuola)
        m("dritto")
        m("dritto", pendenza=21, etichetta="SALITA 21")
        m("dritto", pendenza=21)
    else:
        m("dritto", pendenza=21, etichetta="SALITA 21")
        m("dritto", pendenza=21)
        m("dritto")
        m("dritto", pendenza=-21, etichetta="DISCESA 21")
        m("dritto", pendenza=-21)
    m("incrocio", forma="+", verdi="diagonale_sx", etichetta="+ VERDI IN DIAGONALE")
    m("dritto")
    m("curva_dx")
    m("dritto")
    m("arrivo", etichetta="ARRIVO")
    C = K.fine((3, 10), 0)
    C["traguardi"] = []
    C["ostacolo"] = None
    for k in ("palline", "triangoli", "muri"):     # niente arena in questa pista: pezzi finti
        C.setdefault(k, [])
    C.setdefault("arena", {"x": 0.0, "y": 0.0, "w": 1.0, "h": 1.0, "ingresso": (0.0, 0.0), "uscita": (0.0, 0.0)})
    C.setdefault("argento", {"x": 0.0, "y": 0.0, "w": 0.5, "h": 0.5})          # un puntino nell'angolo vuoto
    C.setdefault("nero_uscita", {"x": 0.0, "y": 1.0, "w": 0.5, "h": 0.5})
    C.setdefault("raggio_pallina", 2.25)
    C.setdefault("rampa", None)
    global CENTRO_Y
    CENTRO_Y = [p["cella"][1] * 30 + 15 for p in C["percorso"] if p["tipo"] == "incrocio"][0]
    return C

vecchia = campo.crea_campo
campo.crea_campo = lambda v="normale": pista() if v == "verde_discesa" else vecchia(v)
campo.SCENARI["verde_discesa"] = {"nome": "Prova: + coi verdi in diagonale in fondo alla discesa", "campo": "verde_discesa"}
r = esegui.esegui(sys.argv[2], sys.argv[3], 120, {"seme": int(sys.argv[5])}, sys.argv[4])
righe = [f"{t:6.1f} {m[:110]}" for t, m in r["log"]
         if any(k in m for k in ("Incrocio con verde", "Verde in discesa", "Verde in salita", "VADO DRITTO", "Svolta completata", "Svolta:", "Incrocio: velocità", "INDIETRO DRITTO", "Linea ROSSA", "ARRIVO", "Linea interrotta", "Interruzione", "linea persa", "Linea ritrovata"))]
# dove sono le ruote quando il robot comincia a girare all'incrocio (centro dell'incrocio: CENTRO_Y)
giro = None
for c in r["campioni"]:
    t, x, y, h, pitch = c[0], c[1], c[2], c[3], c[11]
    if CENTRO_Y - 25 < y < CENTRO_Y + 65 and min(abs(h - 0), abs(h - 360)) > 8 and t > 10:
        giro = {"t": t, "prima_cm": round(y - CENTRO_Y, 1), "beccheggio": pitch}
        break
print("RISULTATO " + json.dumps({"fine": r["fine"], "durata": r["durata"], "righe": righe[:14], "giro": giro}))
'''


def main():
    cartella = os.path.abspath(sys.argv[1])
    semi = [int(s) for s in (sys.argv[2] if len(sys.argv) > 2 else "1,2,3").split(",")]
    modo = sys.argv[3] if len(sys.argv) > 3 else "discesa"
    nome_v = os.path.basename(cartella)
    arrivi = 0
    for seme in semi:
        nome = f"verde_{modo}_{nome_v}_{seme}"
        out = subprocess.run([sys.executable, "-c", GARA, SIM, cartella, nome, "verde_discesa", str(seme), modo],
                             capture_output=True, text=True, cwd=QUI, timeout=600)
        for f in (os.path.join(SIM, f"replay_{nome}.json"),):
            if os.path.exists(f):
                os.remove(f)
        r = [x for x in out.stdout.splitlines() if x.startswith("RISULTATO ")]
        if not r:
            print(f"{nome_v} seme {seme}: il simulatore non è partito\n{out.stderr[-1500:]}")
            continue
        r = json.loads(r[-1][10:])
        ok = r["fine"] == "arrivo"
        arrivi += ok
        g = r.get("giro") or {}
        print(f"{nome_v} seme {seme}: {'ARRIVO (ha girato a sinistra)' if ok else r['fine']} dopo {r['durata']:.0f} s; "
              f"comincia a girare con le ruote {g.get('prima_cm')} cm prima del centro dell'incrocio (beccheggio {g.get('beccheggio')})")
        for x in r["righe"]:
            print("     ", x)
    print(f"== {nome_v}: {arrivi} arrivi su {len(semi)}")


if __name__ == "__main__":
    main()
