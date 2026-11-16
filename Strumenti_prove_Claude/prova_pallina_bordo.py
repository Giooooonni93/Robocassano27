"""Prova della PALLINA SUL BORDO DELL'IMMAGINE (FIX 119, scatola nera 16/11 V50, 506 s).

Nell'arena, la prima volta che il robot arriva vicino a una pallina (riquadro YOLO grande), il simulatore lo ruota
di colpo di ROTAZIONE gradi a destra, come se fosse scivolato: la pallina finisce davvero sul bordo sinistro
dell'immagine, tagliata (come alle 10:40 del 16/11, centro x=30 su 224). Una volta per pallina.
Il simulatore non si tocca: la rotazione si aggiunge solo dentro questo script.

Uso: python3 prova_pallina_bordo.py <cartella versione> [semi] [scenario] [gradi]   es.  ../ClaudeRob_V51 1,2,3 arena 25
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
import mondo, esegui
GRADI = float(sys.argv[6])
vera = mondo.Mondo.oggetti_arena
def oggetti_arena(self, cosa):
    trovati = vera(self, cosa)
    if cosa != "palline" or self.tenuta is not None:
        return trovati
    for c, p, b in trovati:
        if b and (b[2] - b[0]) * (b[3] - b[1]) >= 5500 and self.t - getattr(self, "_ultima_spinta", -99) > 20:
            self._ultima_spinta = self.t
            self.h = (self.h + GRADI) % 360                 # "scivolato": la pallina va sul bordo sinistro
            ax, ay, ah = self.arena_pose                    # anche la posa della foto della camera arena
            self.arena_pose = (ax, ay, (ah + GRADI) % 360)
            nuovi = vera(self, cosa)
            self.evento("info", f"PROVA: robot ruotato di {GRADI:.0f} gradi, riquadri {[x[2] for x in nuovi]}")
            return nuovi
    return trovati
mondo.Mondo.oggetti_arena = oggetti_arena
r = esegui.esegui(sys.argv[2], sys.argv[3], 480, {"seme": int(sys.argv[5])}, sys.argv[4])
log = [m for t, m in r["log"]]
print("RISULTATO " + json.dumps({
    "fine": r["fine"], "durata": r["durata"],
    "prese": sum("PALLINA CATTURATA" in m for m in log), "mancate": sum("PALLINA NON CATTURATA" in m for m in log),
    "bordo": sum("tagliata dal bordo" in m for m in log), "spinte": sum(1 for e in r["eventi"] if "PROVA:" in json.dumps(e))}))
'''


def main():
    cartella = os.path.abspath(sys.argv[1])
    semi = [int(s) for s in (sys.argv[2] if len(sys.argv) > 2 else "1,2,3").split(",")]
    scenario = sys.argv[3] if len(sys.argv) > 3 else "arena"
    gradi = sys.argv[4] if len(sys.argv) > 4 else "25"
    nome_v = os.path.basename(cartella)
    tot = {"prese": 0, "mancate": 0, "arrivi": 0}
    for seme in semi:
        nome = f"pallina_bordo_{nome_v}_{seme}"
        out = subprocess.run([sys.executable, "-c", GARA, SIM, cartella, nome, scenario, str(seme), gradi],
                             capture_output=True, text=True, cwd=QUI, timeout=900)
        f = os.path.join(SIM, f"replay_{nome}.json")
        if os.path.exists(f):
            os.remove(f)
        r = [x for x in out.stdout.splitlines() if x.startswith("RISULTATO ")]
        if not r:
            print(f"{nome_v} seme {seme}: il simulatore non è partito\n{out.stderr[-1500:]}")
            continue
        r = json.loads(r[0][10:])
        tot["prese"] += r["prese"]
        tot["mancate"] += r["mancate"]
        tot["arrivi"] += r["fine"] == "arrivo"
        print(f"{nome_v} seme {seme}: {r['fine']} dopo {r['durata']:.0f} s; robot ruotato {r['spinte']} volte; "
              f"prese {r['prese']}, MANCATE {r['mancate']}; 'tagliata dal bordo' {r['bordo']} volte")
    print(f"== {nome_v} ({scenario}): prese {tot['prese']}, mancate {tot['mancate']}, arrivi {tot['arrivi']} su {len(semi)}")


if __name__ == "__main__":
    main()
