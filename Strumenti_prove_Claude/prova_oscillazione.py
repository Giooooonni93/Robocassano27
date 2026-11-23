"""Prova del DESTRA-SINISTRA SENZA FINE (FIX 141, scatola nera 23/11 12:25, 176-187 s, piastrella col quadrato).

Nel simulatore la piastrella col quadrato non fa oscillare il robot (YOLO e la camera sono "perfetti"). Allora, da un
certo istante e per 15 s, si fa credere al seguilinea di vedere quello che vedeva il robot vero nell'angolo: una volta
"spinta a destra" (BusterDx), una volta "correggi a sinistra" (errore -145), come alle 12:25. Il robot vero restava lì
11 s e poi LoP. Si guarda se il programma se ne accorge e quanto ci mette.
Il simulatore non si tocca: tutto dentro questo script.

Uso: python3 prova_oscillazione.py <cartella versione> [istante, es. 20] [scenario]
"""
import json
import os
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
SIM = max((os.path.join(QUI, "..", d) for d in os.listdir(os.path.join(QUI, ".."))
           if d.startswith("ClaudeRob_Simulatore_V")), key=lambda d: int(d.rsplit("_V", 1)[1]))

GARA = r'''
import sys, json, threading, time
sys.path.insert(0, sys.argv[1])
import mondo, esegui
T0 = float(sys.argv[5])
STATO = {"t": 0.0, "n": 0}
passo_vero = mondo.Mondo.passo
def passo(self, dt):
    passo_vero(self, dt)
    STATO["t"] = self.t
    W = sys.modules.get("ViennaClsWebCam")             # il codice del robot è già caricato: aggancio una volta
    if W is not None and hasattr(W, "CalcolaErrore") and not getattr(W, "_finta", False):
        vera = W.CalcolaErrore
        def finta(frame):
            if T0 <= STATO["t"] < T0 + 15:
                STATO["n"] += 1
                return ("BusterDx", 0) if STATO["n"] % 2 else (None, -145)
            return vera(frame)
        W.CalcolaErrore = finta
        W._finta = True
mondo.Mondo.passo = passo
r = esegui.esegui(sys.argv[2], sys.argv[3], 480, {"seme": 1}, sys.argv[4])
righe = [f"{t:6.1f} {m[:100]}" for t, m in r["log"] if any(k in m for k in ("sterzo a destra e a sinistra", "Nessun verde: passo", "Vedo un verde"))]
print("RISULTATO " + json.dumps({"fine": r["fine"], "durata": r["durata"], "righe": righe[:6], "n": STATO["n"], "rotte": [round(c[3]) for c in r["campioni"] if T0 <= c[0] < T0 + 15][::10]}))
'''


def main():
    cartella = os.path.abspath(sys.argv[1])
    t0 = sys.argv[2] if len(sys.argv) > 2 else "20"
    scenario = sys.argv[3] if len(sys.argv) > 3 else "scuola"
    nome = f"oscillazione_{os.path.basename(cartella)}"
    out = subprocess.run([sys.executable, "-c", GARA, SIM, cartella, nome, scenario, t0],
                         capture_output=True, text=True, cwd=QUI, timeout=900)
    f = os.path.join(SIM, f"replay_{nome}.json")
    if os.path.exists(f):
        os.remove(f)
    r = [x for x in out.stdout.splitlines() if x.startswith("RISULTATO ")]
    if not r:
        print("il simulatore non è partito\n" + out.stderr[-1500:])
        return
    r = json.loads(r[0][10:])
    print(f"{os.path.basename(cartella)} ({scenario}, destra-sinistra finto da {t0} s per 15 s): {r['fine']} dopo {r['durata']:.0f} s")
    print('      chiamate finte', r.get('n'), 'rotte', r.get('rotte'))
    for x in r["righe"] or ["(nessuna reazione)"]:
        print("     ", x)


if __name__ == "__main__":
    main()
