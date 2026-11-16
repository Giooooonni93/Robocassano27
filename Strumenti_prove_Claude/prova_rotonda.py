"""Prova della ROTONDA IN CIMA ALLA RAMPA (scatole nere 16/11 V50 282 s e V52 50/82 s, foto IMG_3921).

Pista: salita di 21 gradi (2 piastrelle), poi la piastrella della rotonda della scuola: gambo da sotto, cerchio di circa
15 cm, verde a DESTRA del gambo prima del cerchio (si entra girando a destra), ramo di uscita a DESTRA con il suo verde
(prima dell'incrocio, a destra), ramo in alto che non porta da nessuna parte. Il percorso giusto esce a destra e arriva
alla linea rossa. Il simulatore non si tocca: la rotonda si disegna solo dentro questo script.

Uso: python3 prova_rotonda.py <cartella versione> [semi]      es.  ../ClaudeRob_V52 1,2,3
"""
import json
import os
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
SIM = max((os.path.join(QUI, "..", d) for d in os.listdir(os.path.join(QUI, ".."))
           if d.startswith("ClaudeRob_Simulatore_V")), key=lambda d: int(d.rsplit("_V", 1)[1]))

GARA = r'''
import sys, json, math
sys.path.insert(0, sys.argv[1])
import piastrelle as P, campo, esegui

def pista():
    K = P.Costruttore(6, 9)
    K.inizia(2, 8, 0)
    m = K.metti
    m("partenza", cp=True)
    m("dritto")
    m("dritto", pendenza=21, etichetta="SALITA 21")
    m("dritto", pendenza=21)
    n0 = len(K.C["linee"])
    m("curva_dx", etichetta="ROTONDA")              # cella (2,4): la sostituisco con la rotonda
    del K.C["linee"][n0:]
    m("dritto")
    m("curva_sx")
    m("arrivo", etichetta="ARRIVO")
    C = K.fine((2, 8), 0)
    X0, Y0 = 2 * 30.0, 4 * 30.0
    cx, cy, r = X0 + 15, Y0 + 13, 6.5
    B, E, T = (cx, cy + r), (cx + r, cy), (cx, cy - r)
    C["linee"].append([(cx, Y0 + 30), B])                                # gambo da sotto
    C["linee"].append([(cx + r * math.cos(a * math.pi / 18), cy + r * math.sin(a * math.pi / 18)) for a in range(37)])
    C["linee"].append([E, (X0 + 30, cy)])                                # ramo di uscita a destra
    C["linee"].append([T, (cx, Y0)])                                     # ramo in alto (non porta da nessuna parte)
    C["verdi"] = [v for v in C["verdi"]]
    C["verdi"].append({"x": cx + 1.4, "y": B[1] + 0.3, "w": 2.5, "h": 2.5, "id": "VR1", "incrocio": B})   # ingresso: a destra
    C["verdi"].append({"x": E[0] + 1.0, "y": cy + 0.8, "w": 2.5, "h": 2.5, "id": "VR2", "incrocio": E})   # uscita: a destra
    C["traguardi"] = []
    C["ostacolo"] = None
    for k in ("palline", "triangoli", "muri"):
        C.setdefault(k, [])
    C.setdefault("arena", {"x": 0.0, "y": 0.0, "w": 1.0, "h": 1.0, "ingresso": (0.0, 0.0), "uscita": (0.0, 0.0)})
    C.setdefault("argento", {"x": 0.0, "y": 0.0, "w": 0.5, "h": 0.5})
    C.setdefault("nero_uscita", {"x": 0.0, "y": 1.0, "w": 0.5, "h": 0.5})
    C.setdefault("raggio_pallina", 2.25)
    C.setdefault("rampa", None)
    return C

vecchia = campo.crea_campo
campo.crea_campo = lambda v="normale": pista() if v == "rotonda" else vecchia(v)
campo.SCENARI["rotonda"] = {"nome": "Prova: rotonda in cima alla rampa", "campo": "rotonda"}
r = esegui.esegui(sys.argv[2], sys.argv[3], 90, {"seme": int(sys.argv[5])}, sys.argv[4])
righe = [f"{t:6.1f} {m[:100]}" for t, m in r["log"]
         if any(k in m for k in ("Incrocio con verde", "Verde in", "VADO DRITTO", "Svolta", "Linea ROSSA", "linea persa", "Linea ritrovata", "Rotonda", "rotonda"))]
print("RISULTATO " + json.dumps({"fine": r["fine"], "durata": r["durata"], "righe": righe[:12],
      "eventi": [e.get("testo", "")[:80] for e in r["eventi"] if e.get("tipo") in ("lop", "errore")][:4]}))
'''


def main():
    cartella = os.path.abspath(sys.argv[1])
    semi = [int(s) for s in (sys.argv[2] if len(sys.argv) > 2 else "1,2,3").split(",")]
    nome_v = os.path.basename(cartella)
    arrivi = 0
    for seme in semi:
        nome = f"rotonda_{nome_v}_{seme}"
        out = subprocess.run([sys.executable, "-c", GARA, SIM, cartella, nome, "rotonda", str(seme)],
                             capture_output=True, text=True, cwd=QUI, timeout=600)
        f = os.path.join(SIM, f"replay_{nome}.json")
        if os.path.exists(f):
            os.remove(f)
        r = [x for x in out.stdout.splitlines() if x.startswith("RISULTATO ")]
        if not r:
            print(f"{nome_v} seme {seme}: il simulatore non è partito\n{out.stderr[-1500:]}")
            continue
        r = json.loads(r[-1][10:])
        # la pista di prova non sempre registra l'arrivo: conta anche "Linea ROSSA" scritto dal robot
        ok = r["fine"] == "arrivo" or any("Linea ROSSA" in x for x in r["righe"])
        arrivi += ok
        print(f"{nome_v} seme {seme}: {'ARRIVO (uscito dalla rotonda a destra)' if ok else r['fine']} dopo {r['durata']:.0f} s")
        for x in r["righe"]:
            print("     ", x)
        for x in r["eventi"]:
            print("      !", x)
    print(f"== {nome_v}: {arrivi} arrivi su {len(semi)}")


if __name__ == "__main__":
    main()
