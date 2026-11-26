"""Prova dei SALTI DELLA BUSSOLA (FIX 149, scatole nere V61 26/11 15:17 a 24,7 s, 15:29 a 24,6 s, 15:39 a 22,8 s).

Sul robot vero, a metà della svolta a sinistra dopo l'altalena, la rotta del BNO055 salta di +52 gradi in un pacchetto e
poi continua regolare (il robot non ha girato davvero). Qui, a ogni svolta a sinistra al verde ("Incrocio con verde a
SINISTRA"), quando il robot ha già girato di 22 gradi il simulatore aggiunge +52 gradi alla rotta che legge il robot, e
ce li lascia (come il sensore vero). Dalla V62 la rotta passa da Robot._togli_salto (come nel thread che legge l'Arduino).
Il simulatore non si tocca: tutto dentro questo script.

Uso: python3 prova_salto_bussola.py <cartella versione> [scenario, es. rcj2026] [semi, es. 1,2]
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
st = {"salto": 0, "attesa": None, "n_log": 0, "salti": 0}
sens_vero = mondo.Mondo.aggiorna_sensori_robot
def aggiorna(self):
    sens_vero(self)
    r = getattr(self, "robot", None)
    if r is None:
        return
    nuovi = self.log[st["n_log"]:]
    st["n_log"] = len(self.log)
    if any("Incrocio con verde a SINISTRA" in m for _, m in nuovi):
        st["attesa"] = self.h                      # svolta a sinistra cominciata: aspetto 22 gradi
    if st["attesa"] is not None and abs((self.h - st["attesa"] + 540) % 360 - 180) >= 22:
        st["attesa"] = None
        st["salto"] += 52
        st["salti"] += 1
        self.evento("info", f"PROVA: salto della bussola di +52 gradi (n. {st['salti']})")
    with r._lock:
        pt, rl, hd = r._last_imu
    if (pt, rl, hd) == (-2, -2, 0):
        return
    hd = int(round(hd + st["salto"])) % 360
    if hasattr(r, "_togli_salto"):                 # V62: come il thread che legge l'Arduino
        hd = r._togli_salto(hd, pt, rl)
    with r._lock:
        r._last_imu = (pt, rl, hd)
mondo.Mondo.aggiorna_sensori_robot = aggiorna
r = esegui.esegui(sys.argv[2], sys.argv[3], 480, {"seme": int(sys.argv[5])}, sys.argv[4])
p = r.get("punteggio") if isinstance(r.get("punteggio"), dict) else {}
righe = [f"{t:6.1f} {m[:100]}" for t, m in r["log"] if "BUSSOLA" in m][:4]
print("RISULTATO " + json.dumps({"fine": r["fine"], "durata": r["durata"], "lop": p.get("lop"), "salti": st["salti"],
                                 "righe": righe}))
'''


def main():
    cartella = os.path.abspath(sys.argv[1])
    scenario = sys.argv[2] if len(sys.argv) > 2 else "rcj2026"
    semi = [int(s) for s in (sys.argv[3] if len(sys.argv) > 3 else "1").split(",")]
    nome_v = os.path.basename(cartella)
    for seme in semi:
        nome = f"salto_bussola_{nome_v}_{scenario}_{seme}"
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
        print(f"{nome_v} ({scenario}, seme {seme}): {r['fine']} dopo {r['durata']:.0f} s, LoP {r['lop']}, "
              f"salti messi {r['salti']}")
        for x in r["righe"]:
            print("     ", x)


if __name__ == "__main__":
    main()
