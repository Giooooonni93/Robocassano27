"""Prova dell'OSTACOLO VICINO AL BORDO DELLA PISTA (FIX 148, il prof il 26/11: "se si aggira da un lato c'è la
possibilità che il robot cada dalla pista").

Pista `gara` (l'unica del simulatore con l'ostacolo). Quando il robot arriva vicino all'ostacolo, il simulatore si segna
la direzione della linea e mette un BORDO DELLA PISTA parallelo alla linea, a BORDO_CM dal centro dell'ostacolo, dal lato
scelto ("destra" o "sinistra"). Oltre il bordo la camera linea vede il pavimento marrone della stanza (come nelle scatole
nere vere del 05/11 15:12 e 13/11 09:54). Se il centro del robot passa il bordo il robot è CADUTO.
Il simulatore non si tocca: tutto dentro questo script.

Uso: python3 prova_ostacolo_bordo.py <cartella versione> [lato del bordo: destra/sinistra] [semi, es. 1,2]
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
import numpy as np
import mondo, esegui
LATO = 1 if sys.argv[4] == "destra" else -1      # +1 = a destra della linea (rotte crescono a destra)
BORDO_CM = 16.0
st = {"h0": None, "o": None, "max": -99.0, "caduto": None}

def laterale(self, x, y):
    # cm verso il bordo (positivo = dal lato del bordo); il bordo è lungo 90 cm (45 prima e dopo l'ostacolo):
    # fuori da quel tratto la pista continua (-99 = niente bordo)
    ox, oy = st["o"]
    rx, ry = mondo._dir(st["h0"] + 90)              # vettore verso destra della linea
    ax, ay = mondo._dir(st["h0"])                   # vettore lungo la linea
    if abs((x - ox) * ax + (y - oy) * ay) > 45:
        return -99.0
    return LATO * ((x - ox) * rx + (y - oy) * ry)

sens_vero = mondo.Mondo.aggiorna_sensori_robot
def aggiorna(self):
    sens_vero(self)
    o = self.C.get("ostacolo")
    if not o:
        return
    cx, cy = o["x"] + o["w"] / 2, o["y"] + o["h"] / 2
    if st["h0"] is None and math.hypot(self.x - cx, self.y - cy) < 35:
        st["h0"], st["o"] = self.h, (cx, cy)
        self.evento("info", f"PROVA: bordo della pista a {BORDO_CM:.0f} cm dall'ostacolo, a {sys.argv[4]}")
    if st["h0"] is not None:
        d = laterale(self, self.x, self.y)
        st["max"] = max(st["max"], d)
        if d > BORDO_CM and st["caduto"] is None:          # il centro del robot oltre il bordo: si ribalta
            st["caduto"] = round(self.t, 1)
            self.evento("info", f"PROVA: CADUTO dal bordo a {self.t:.1f} s")
            self.fine = "caduto dal bordo"
mondo.Mondo.aggiorna_sensori_robot = aggiorna

img_vera = mondo.Mondo.immagine_linea
def immagine(self, pose=None):
    img = img_vera(self, pose)
    if st["h0"] is None:
        return img
    x, y, h = pose or (self.x, self.y, self.h)
    dx, dy = mondo._dir(h)
    d = laterale(self, x + 10 * dx, y + 10 * dy)     # la camera linea è circa 10 cm davanti al centro
    fuori = min(1.0, max(0.0, (d - BORDO_CM + 4) / 8.0))
    if fuori > 0:
        img = img.copy()
        n = int(round(img.shape[0] * fuori))
        img[:n] = (60, 95, 125, 255)[:img.shape[2]]   # pavimento della stanza (marrone, BGR), dall'alto dell'immagine
    return img
mondo.Mondo.immagine_linea = immagine

r = esegui.esegui(sys.argv[2], sys.argv[3], 480, {"seme": int(sys.argv[5])}, "gara")
righe = [f"{t:6.1f} {m[:110]}" for t, m in r["log"] if any(k in m for k in ("OSTACOLO", "Ostacolo", "BORDO", "Error:"))]
print("RISULTATO " + json.dumps({"fine": r["fine"], "durata": r["durata"], "righe": righe[:12],
                                 "caduto": st["caduto"], "max": round(st["max"], 1)}))
'''


def main():
    cartella = os.path.abspath(sys.argv[1])
    lato = sys.argv[2] if len(sys.argv) > 2 else "destra"
    semi = [int(s) for s in (sys.argv[3] if len(sys.argv) > 3 else "1").split(",")]
    nome_v = os.path.basename(cartella)
    for seme in semi:
        nome = f"ostacolo_bordo_{nome_v}_{lato}_{seme}"
        out = subprocess.run([sys.executable, "-c", GARA, SIM, cartella, nome, lato, str(seme)],
                             capture_output=True, text=True, cwd=QUI, timeout=900)
        f = os.path.join(SIM, f"replay_{nome}.json")
        if os.path.exists(f):
            os.remove(f)
        r = [x for x in out.stdout.splitlines() if x.startswith("RISULTATO ")]
        if not r:
            print(f"{nome_v} seme {seme}: il simulatore non è partito\n{out.stderr[-1500:]}")
            continue
        r = json.loads(r[-1][10:])
        cad = f"CADUTO a {r['caduto']} s" if r["caduto"] else f"non caduto (al massimo {r['max']} cm verso il bordo, bordo a 16)"
        print(f"{nome_v} (bordo a {lato}, seme {seme}): {r['fine']} dopo {r['durata']:.0f} s, {cad}")
        for x in r["righe"]:
            print("     ", x)


if __name__ == "__main__":
    main()
