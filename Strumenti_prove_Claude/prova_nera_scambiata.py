"""Prova della PALLINA NERA PRESA PER ARGENTO (FIX 130-132, scatola nera 19/11 11:33, V54, Battista).

"scambio": YOLO vede la pallina NERA sempre come ARGENTO (classe 0), come la nera rovinata del 19/11. La foto della
camera arena resta vera (nera scura, argento chiara). Prima (V54) il robot la portava nel triangolo verde, poi cercava
solo la nera (che YOLO non vede più) e restava in arena per sempre.
"lop": come "scambio", e in più 15 s dopo la seconda pallina il capitano dichiara una LoP (dentro l'arena): il robot
riparte dall'ultimo checkpoint (solo piste a piastrelle, es. rcj2026).
Alla fine: dove sono finite le palline e se il robot è uscito dall'arena.
Il simulatore non si tocca: tutto dentro questo script.

Uso: python3 prova_nera_scambiata.py <cartella versione> [semi] [scenario] [scambio|lop]   es.  ../ClaudeRob_V55 1,2 arena scambio
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
MODO = sys.argv[6]
vera = mondo.Mondo.oggetti_arena
def oggetti_arena(self, cosa):
    out = vera(self, cosa)
    if cosa == "palline" and not getattr(self, "_foto_vera", False):
        out = [(0, c, b) for _, c, b in out]          # la nera la vede ARGENTO
    return out
mondo.Mondo.oggetti_arena = oggetti_arena
img_vera = mondo.Mondo.immagine_arena
def immagine_arena(self):
    self._foto_vera = True                              # la foto resta vera: la nera è scura
    try:
        return img_vera(self)
    finally:
        self._foto_vera = False
mondo.Mondo.immagine_arena = immagine_arena
if MODO == "lop":
    # LoP vera del simulatore (solo piste a piastrelle, es. rcj2026): 15 s dopo la seconda pallina il capitano
    # dichiara la LoP e il robot viene rimesso all'ultimo checkpoint, prima dell'arena
    passo_vero = mondo.Mondo.passo
    def passo(self, dt):
        passo_vero(self, dt)
        prese = sum(1 for b in self.palline if b["stato"] != "libera")
        if prese >= 2 and not hasattr(self, "_lop_t"):
            self._lop_t = self.t + 15.0
        if getattr(self, "_lop_t", None) and self.t >= self._lop_t and not getattr(self, "_lop_fatta", False):
            self._lop_fatta = True
            self._richiedi_lop("PROVA: LoP dentro l'arena")
    mondo.Mondo.passo = passo
r = esegui.esegui(sys.argv[2], sys.argv[3], 480, {"seme": int(sys.argv[5])}, sys.argv[4])
log = [m for t, m in r["log"]]
righe = [f"{t:6.1f} {m[:105]}" for t, m in r["log"] if any(k in m for k in (
    "Scarica", "RICERCA LIBERA", "Arena: da", "non confermata", "il colore dice", "LoP dentro", "LoP:", "E' l'USCITA", "Uscito"))]
eventi = [e.get("testo", "")[:70] for e in r["eventi"] if "✓" in e.get("testo", "") or "✗" in e.get("testo", "")]
print("RISULTATO " + json.dumps({"fine": r["fine"], "durata": r["durata"], "righe": righe[:16], "palline": eventi,
                                 "uscito": any("USCITA" in m for m in log)}))
'''


def main():
    cartella = os.path.abspath(sys.argv[1])
    semi = [int(s) for s in (sys.argv[2] if len(sys.argv) > 2 else "1").split(",")]
    scenario = sys.argv[3] if len(sys.argv) > 3 else "arena"
    modo = sys.argv[4] if len(sys.argv) > 4 else "scambio"
    nome_v = os.path.basename(cartella)
    for seme in semi:
        nome = f"nera_scambiata_{nome_v}_{seme}"
        out = subprocess.run([sys.executable, "-c", GARA, SIM, cartella, nome, scenario, str(seme), modo],
                             capture_output=True, text=True, cwd=QUI, timeout=900)
        f = os.path.join(SIM, f"replay_{nome}.json")
        if os.path.exists(f):
            os.remove(f)
        r = [x for x in out.stdout.splitlines() if x.startswith("RISULTATO ")]
        if not r:
            print(f"{nome_v} seme {seme}: il simulatore non è partito\n{out.stderr[-1500:]}")
            continue
        r = json.loads(r[-1][10:])
        print(f"{nome_v} ({scenario} {seme}, {modo}): {r['fine']} dopo {r['durata']:.0f} s; uscito dall'arena: "
              f"{'sì' if r['uscito'] else 'NO'}")
        for x in r["palline"]:
            print("      *", x)
        for x in r["righe"]:
            print("       ", x)


if __name__ == "__main__":
    main()
