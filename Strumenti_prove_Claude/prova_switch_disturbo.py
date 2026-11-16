"""Prova del DISTURBO SULLO SWITCH (FIX 117, scatola nera 16/11 V50, 227 s).

Durante il seguilinea lo switch si spegne per un attimo (0,15 s) e si riaccende: come quando l'Arduino riprende a parlare
a scatti o il contatto dello switch rimbalza. Prima il seguilinea si fermava e il programma passava all'ARENA in mezzo
alla pista. Il simulatore non si tocca: il disturbo si aggiunge solo dentro questo script.

Uso: python3 prova_switch_disturbo.py <cartella versione> [secondi del disturbo, es. 20,45,70] [scenario]
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
disturbi = [float(x) for x in sys.argv[5].split(",")]
passo_vero = mondo.Mondo.passo
def passo(self, dt):
    passo_vero(self, dt)
    for t0 in disturbi:
        if t0 <= self.t < t0 + 0.15 and self.switch_avvio and not getattr(self, "lop_fase", None):
            self.switch_avvio = False
            self._disturbo = True
        elif getattr(self, "_disturbo", False) and self.t >= t0 + 0.15 and t0 <= self.t < t0 + 0.4:
            self.switch_avvio = True
            self._disturbo = False
mondo.Mondo.passo = passo
r = esegui.esegui(sys.argv[2], sys.argv[3], 480, {"seme": 1}, sys.argv[4])
righe = [f"{t:6.1f} {m[:100]}" for t, m in r["log"]
         if any(k in m for k in ("AVVIO ARENA", "Switch spento solo", "Seguilinea finito senza", "Sono entrato", "Verificata entrata"))]
print("RISULTATO " + json.dumps({"fine": r["fine"], "durata": r["durata"], "righe": righe[:12]}))
'''


def main():
    cartella = os.path.abspath(sys.argv[1])
    disturbi = sys.argv[2] if len(sys.argv) > 2 else "20,45,70"
    scenario = sys.argv[3] if len(sys.argv) > 3 else "scuola"
    nome = f"switch_disturbo_{os.path.basename(cartella)}"
    out = subprocess.run([sys.executable, "-c", GARA, SIM, cartella, nome, scenario, disturbi],
                         capture_output=True, text=True, cwd=QUI, timeout=900)
    f = os.path.join(SIM, f"replay_{nome}.json")
    if os.path.exists(f):
        os.remove(f)
    r = [x for x in out.stdout.splitlines() if x.startswith("RISULTATO ")]
    if not r:
        print("il simulatore non è partito\n" + out.stderr[-1500:])
        return
    r = json.loads(r[0][10:])
    print(f"{os.path.basename(cartella)} ({scenario}, disturbi a {disturbi} s): {r['fine']} dopo {r['durata']:.0f} s")
    for x in r["righe"]:
        print("     ", x)


if __name__ == "__main__":
    main()
