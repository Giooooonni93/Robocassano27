"""Prova dell'OSTACOLO CHE FA ALZARE IL MUSO (FIX 142, scatola nera 24/11 11:05, 127 s, pista nuova).

Quando il robot tocca l'ostacolo il muso si alza di 7-11 gradi: prima il programma diceva "è una RAMPA" e non lo
aggirava. Qui, appena il laser davanti legge meno di 14 cm vicino all'ostacolo della pista, il simulatore fa alzare il
muso di 9 gradi (come il robot vero). Si guarda se il robot aggira l'ostacolo e arriva.
Il simulatore non si tocca: tutto dentro questo script.

Uso: python3 prova_ostacolo_muso.py <cartella versione> [semi] [scenario]   es.  ../ClaudeRob_V59 1,2 scuola
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
import mondo, esegui
sens_vero = mondo.Mondo.aggiorna_sensori_robot
def aggiorna(self):
    sens_vero(self)
    o = self.C.get("ostacolo")
    if not o:
        return
    cx, cy = o["x"] + o["w"] / 2, o["y"] + o["h"] / 2
    if math.hypot(self.x - cx, self.y - cy) < 25 and 0 < self.tof_val[1] < 14:
        for rob in [getattr(self, "robot", None), getattr(self, "_robot", None)]:
            if rob is not None:
                with rob._lock:
                    _, roll, hd = rob._last_imu
                    rob._last_imu = (9, roll, hd)         # il muso si alza toccando l'ostacolo
mondo.Mondo.aggiorna_sensori_robot = aggiorna
r = esegui.esegui(sys.argv[2], sys.argv[3], 480, {"seme": int(sys.argv[5])}, sys.argv[4])
righe = [f"{t:6.1f} {m[:100]}" for t, m in r["log"] if any(k in m for k in ("RAMPA", "Ostacolo confermato", "OSTACOLO", "FINE OSTACOLO", "non riesco"))]
print("RISULTATO " + json.dumps({"fine": r["fine"], "durata": r["durata"], "righe": righe[:10],
                                 "eventi": [e.get("testo", "")[:80] for e in r["eventi"] if "stacolo" in e.get("testo", "")][:4]}))
'''


def main():
    cartella = os.path.abspath(sys.argv[1])
    semi = [int(s) for s in (sys.argv[2] if len(sys.argv) > 2 else "1").split(",")]
    scenario = sys.argv[3] if len(sys.argv) > 3 else "scuola"
    nome_v = os.path.basename(cartella)
    for seme in semi:
        nome = f"ostacolo_muso_{nome_v}_{seme}"
        out = subprocess.run([sys.executable, "-c", GARA, SIM, cartella, nome, scenario, str(seme)],
                             capture_output=True, text=True, cwd=QUI, timeout=900)
        f = os.path.join(SIM, f"replay_{nome}.json")
        if os.path.exists(f):
            os.remove(f)
        r = [x for x in out.stdout.splitlines() if x.startswith("RISULTATO ")]
        if not r:
            print(f"{nome_v} seme {seme}: il simulatore non è partito\n{out.stderr[-1500:]}")
            continue
        r = json.loads(r[-1][10:])
        print(f"{nome_v} ({scenario} {seme}): {r['fine']} dopo {r['durata']:.0f} s")
        for x in r["righe"]:
            print("     ", x)
        for x in r["eventi"]:
            print("      !", x)


if __name__ == "__main__":
    main()
