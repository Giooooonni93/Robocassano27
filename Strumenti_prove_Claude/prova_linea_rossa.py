"""Prova dell'ARRIVO SULLA LINEA ROSSA (FIX 127 e FIX 128, richiesta del prof del 16/11).

Il regolamento vuole il robot fermo SOPRA la linea rossa. Lo script misura dove si ferma il robot: quanti cm la striscia
rossa è davanti al CENTRO del robot quando YOLO la vede e quando il robot è fermo (muso a +10,75 cm, retro a -10,75 cm:
fra questi due numeri la striscia è sotto il robot).
Con "lop" lo switch si spegne 3 s dopo l'uscita dall'arena e si riaccende dopo 7 s (una LoP dopo l'arena): prima del
FIX 128 la LoP azzerava "arena fatta" e il robot non restava fermo sulla rossa.
Il simulatore non si tocca: tutto dentro questo script.

Uso: python3 prova_linea_rossa.py <cartella versione> [scenario] [seme] [lop]   es.  ../ClaudeRob_V54 scuola 1 lop
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
import mondo, esegui, campo
if sys.argv[6] == "lop":
    passo_vero = mondo.Mondo.passo
    def passo(self, dt):
        passo_vero(self, dt)
        if "uscita" in self.traguardi and not hasattr(self, "_lop_t"):
            self._lop_t = self.t + 3.0
            self.evento("info", "PROVA: fra 3 s switch spento per 7 s (LoP dopo l'arena)")
        t0 = getattr(self, "_lop_t", None)
        if t0 is not None:
            if t0 <= self.t < t0 + 7.0:
                self.switch_avvio = False
            elif t0 + 7.0 <= self.t < t0 + 7.2:
                self.switch_avvio = True
    mondo.Mondo.passo = passo
r = esegui.esegui(sys.argv[2], sys.argv[3], 600, {"seme": int(sys.argv[5])}, sys.argv[4])
C = campo.crea_campo(campo.SCENARI[sys.argv[4]].get("campo", "normale"))
R = C["rosso"]
rx, ry = R["x"] + R["w"] / 2, R["y"] + R["h"] / 2
def davanti(c):
    dx, dy = math.sin(math.radians(c[3])), -math.cos(math.radians(c[3]))
    return round((rx - c[1]) * dx + (ry - c[2]) * dy, 1)
out = {"fine": r["fine"], "durata": r["durata"]}
t_rossa = [t for t, m in r["log"] if "RO RO RO" in m]
if t_rossa:
    cs = [c for c in r["campioni"] if c[0] >= t_rossa[0]]
    out["vista"] = davanti(cs[0])
    for i, c in enumerate(cs):
        j = [d for d in cs[i:i + 80] if d[0] - c[0] <= 3.0]
        if len(j) > 10 and max(math.hypot(d[1] - c[1], d[2] - c[2]) for d in j) < 0.3:
            out["ferma"] = davanti(c)
            break
out["righe"] = [f"{t:6.1f} {m[:100]}" for t, m in r["log"]
                if any(k in m for k in ("NUOVA RUN", "LoP", "RO RO", "Sopra la linea", "Fermo sulla", "FESTA!", "GARA FINITA"))][-10:]
print("RISULTATO " + json.dumps(out))
'''


def main():
    cartella = os.path.abspath(sys.argv[1])
    scenario = sys.argv[2] if len(sys.argv) > 2 else "scuola"
    seme = sys.argv[3] if len(sys.argv) > 3 else "1"
    lop = sys.argv[4] if len(sys.argv) > 4 else "-"
    nome = f"linea_rossa_{os.path.basename(cartella)}"
    out = subprocess.run([sys.executable, "-c", GARA, SIM, cartella, nome, scenario, seme, lop],
                         capture_output=True, text=True, cwd=QUI, timeout=900)
    f = os.path.join(SIM, f"replay_{nome}.json")
    if os.path.exists(f):
        os.remove(f)
    r = [x for x in out.stdout.splitlines() if x.startswith("RISULTATO ")]
    if not r:
        print("il simulatore non è partito\n" + out.stderr[-1500:])
        return
    r = json.loads(r[0][10:])
    print(f"{os.path.basename(cartella)} ({scenario} {seme}{', LoP dopo l arena' if lop == 'lop' else ''}): {r['fine']} dopo {r['durata']:.0f} s; "
          f"rossa davanti al centro del robot: {r.get('vista')} cm quando la vede, {r.get('ferma')} cm da fermo")
    for x in r["righe"]:
        print("     ", x)


if __name__ == "__main__":
    main()
