"""Prova della PALLINA NERA PRESA PER ARGENTO (FIX 130-132, scatola nera 19/11 11:33, V54, Battista).

"scambio": YOLO vede la pallina NERA sempre come ARGENTO (classe 0), come la nera rovinata del 19/11. La foto della
camera arena resta vera (nera scura, argento chiara). Prima (V54) il robot la portava nel triangolo verde, poi cercava
solo la nera (che YOLO non vede più) e restava in arena per sempre.
"lop": come "scambio", e in più 15 s dopo la seconda pallina il capitano dichiara una LoP (dentro l'arena): il robot
riparte dall'ultimo checkpoint (solo piste a piastrelle, es. rcj2026).
"inganno_lop": la nera sembra argento anche nella FOTO (inganna anche il controllo del colore del FIX 130), così il robot
la porta davvero nel triangolo verde; 3 s dopo l'uscita dall'arena il capitano dichiara una LoP e il robot riparte
dall'ultimo checkpoint, PRIMA dell'arena (richiesta del prof del 19/11: deve rifare l'arena). Solo piste a piastrelle.
"lop_uscita" (V58, FIX 139): palline normali; 5 s dopo la terza pallina portata (il robot cerca l'uscita) il capitano
dichiara una LoP. Prima il robot rientrato rifaceva la ricerca libera (12:45 del 23/11: 69 s persi).
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
    if MODO == "lop_uscita":
        return out
    if cosa == "palline" and (MODO == "inganno_lop" or not getattr(self, "_foto_vera", False)):
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
if MODO == "lop_uscita":
    passo_vero3 = mondo.Mondo.passo
    def passo3(self, dt):
        passo_vero3(self, dt)
        prese = sum(1 for b in self.palline if b["stato"] in ("salvata", "sbagliata"))
        if prese >= 3 and not hasattr(self, "_lop_t"):
            self._lop_t = self.t + 5.0
        if getattr(self, "_lop_t", None) and self.t >= self._lop_t and not getattr(self, "_lop_fatta", False):
            self._lop_fatta = True
            self._richiedi_lop("PROVA: LoP mentre cerca l'uscita")
    mondo.Mondo.passo = passo3
if MODO == "inganno_lop":
    passo_vero2 = mondo.Mondo.passo
    def passo2(self, dt):
        passo_vero2(self, dt)
        A = self.C["arena"]
        dentro = A["x"] + 5 < self.x < A["x"] + A["w"] - 5 and A["y"] + 5 < self.y < A["y"] + A["h"] - 5
        fuori = not (A["x"] - 10 < self.x < A["x"] + A["w"] + 10 and A["y"] - 10 < self.y < A["y"] + A["h"] + 10)
        if dentro and any("Scarica" in m for _, m in self.log):
            self._stato_arena = "dentro"
        if getattr(self, "_stato_arena", None) == "dentro" and fuori and not hasattr(self, "_lop_t"):
            self._lop_t = self.t + 3.0                  # uscito dall'arena (a più di 10 cm dal muro)
        if getattr(self, "_lop_t", None) and self.t >= self._lop_t and not getattr(self, "_lop_fatta", False):
            self._lop_fatta = True
            self._richiedi_lop("PROVA: LoP poco fuori dall'arena")
    mondo.Mondo.passo = passo2
DURATA = 900 if MODO == "inganno_lop" else 480       # inganno_lop: errore + LoP + arena rifatta non stanno in 8 minuti
r = esegui.esegui(sys.argv[2], sys.argv[3], DURATA, {"seme": int(sys.argv[5]), "tempo_gara": DURATA}, sys.argv[4])
log = [m for t, m in r["log"]]
righe = [f"{t:6.1f} {m[:105]}" for t, m in r["log"] if any(k in m for k in (
    "Scarica", "RICERCA LIBERA", "Arena: da", "non confermata", "il colore dice", "LoP dentro", "LoP:", "E' l'USCITA", "Uscito", "AVVIO ARENA", "Sono entrato", "arena è già fatta", "Striscia argento", "RO RO", "LoP mentre", "Arena già completa"))]
eventi = [f'{e.get("t", 0):6.1f} ' + e.get("testo", "")[:80] for e in r["eventi"] if "✓" in e.get("testo", "") or "✗" in e.get("testo", "") or e.get("tipo") == "lop"]
print("RISULTATO " + json.dumps({"fine": r["fine"], "durata": r["durata"], "righe": righe[:30], "palline": eventi,
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
