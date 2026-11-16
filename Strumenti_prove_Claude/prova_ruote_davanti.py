"""Prova del ROBOT SULLE RUOTE DAVANTI (FIX 125, scatole nere 16/11 V50 779 s, V51 385 s, V52 297 e 317 s).

A un certo istante del seguilinea il simulatore mette il robot "in bilico sul muso": beccheggio -65 gradi e laser
davanti a 5 cm (come nelle scatole nere vere dopo l'altalena), e ce lo lascia finché il robot non dà un colpetto di
retromarcia forte (ruote indietro a più del 70%). Il simulatore non si tocca: tutto dentro questo script.

Uso: python3 prova_ruote_davanti.py <cartella versione> [istante, es. 20] [scenario, es. scuola]
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
T0 = float(sys.argv[5])
sens_vero = mondo.Mondo.aggiorna_sensori_robot
def aggiorna(self):
    sens_vero(self)
    st = getattr(self, "_muso", "attesa")
    if st == "attesa" and self.t >= T0 and self.switch_avvio:
        self._muso = st = "giu"
        self._muso_t = self.t
        self._n_log = len(self.log)
        self.evento("info", "PROVA: robot sulle ruote davanti (-65 gradi, laser 5 cm)")
    if st == "giu":
        # il robot ha dato il colpetto di retromarcia? (lo scrive nel log)
        if any("colpetto di retromarcia" in m for _, m in self.log[self._n_log:]):
            self._muso = "su"
            self.evento("info", f"PROVA: colpetto dopo {self.t - self._muso_t:.1f} s: di nuovo su quattro ruote")
            return
        if self.t - self._muso_t > 15:
            self._muso = "fine"
            self.evento("info", "PROVA: dopo 15 s ancora sul muso (nessun colpetto)")
            return
        r = self.robot if hasattr(self, "robot") else None
        for rob in [getattr(self, "robot", None), getattr(self, "_robot", None)]:
            if rob is not None:
                with rob._lock:
                    _, roll, hd = rob._last_imu
                    rob._last_imu = (-65, roll, hd)
                    d = rob._last_distances
                    rob._last_distances = (d[0], 5, d[2])
mondo.Mondo.aggiorna_sensori_robot = aggiorna
r = esegui.esegui(sys.argv[2], sys.argv[3], 480, {"seme": 1}, sys.argv[4])
righe = [f"{t:6.1f} {m[:100]}" for t, m in r["log"] if any(k in m for k in ("ruote davanti", "quattro ruote", "colpetto"))]
prova = [f"{e.get('t', 0):6.1f} {e.get('testo', '')[:90]}" for e in r["eventi"] if "PROVA" in e.get("testo", "")]
print("RISULTATO " + json.dumps({"fine": r["fine"], "durata": r["durata"], "righe": righe[:8], "prova": prova}))
'''


def main():
    cartella = os.path.abspath(sys.argv[1])
    t0 = sys.argv[2] if len(sys.argv) > 2 else "20"
    scenario = sys.argv[3] if len(sys.argv) > 3 else "scuola"
    nome = f"ruote_davanti_{os.path.basename(cartella)}"
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
    print(f"{os.path.basename(cartella)} ({scenario}, sul muso a {t0} s): {r['fine']} dopo {r['durata']:.0f} s")
    for x in r["prova"] + r["righe"]:
        print("     ", x)


if __name__ == "__main__":
    main()
