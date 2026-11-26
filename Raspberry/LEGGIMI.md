# Avvio semplice del robot: `avvia_robot.sh` (23/11)

Un solo comando, dal terminale del robot, da VNC **o anche da SSH** (la finestra si apre comunque sullo schermo del robot):

```
~/avvia_robot.sh          # parte l'ULTIMA versione (come all'accensione)
~/avvia_robot.sh 55       # parte la ClaudeRob_V55
```

Fa tutto da solo: ferma il programma del robot se sta già girando, apre la finestra grande 120 x 40 in UTF-8 (cabina con
le due camere) e, se il programma si chiude per un errore, la finestra **resta aperta** con le ultime scritte finché
premete Invio. Non cancella niente.

## Metterlo sul robot (una volta sola)

```
curl -L -o ~/avvia_robot.sh https://raw.githubusercontent.com/Giooooonni93/Robocassano27/main/Raspberry/avvia_robot.sh
curl -L -o ~/avvia_ultima_versione.sh https://raw.githubusercontent.com/Giooooonni93/Robocassano27/main/Raspberry/avvia_ultima_versione.sh
chmod +x ~/avvia_robot.sh ~/avvia_ultima_versione.sh
```

## Scritte della cabina più grandi (24/11)

La grandezza delle scritte la decide il terminale, non il programma. Una volta sola, dal terminale del robot:
```
sed -i 's/^fontname=.*/fontname=Monospace 13/' ~/.config/lxterminal/lxterminal.conf
```
(oppure, in una finestra di lxterminal: Modifica > Preferenze > Carattere). Poi `~/avvia_robot.sh`. Controllate che la
cabina stia ancora nello schermo: nella finestra `tput cols; tput lines` deve dare almeno 100 e 38. Se è più piccola provate
12; se c'è spazio 14. Per tornare come prima: `Monospace 10`.

---

# Avvio del robot con l'ultima versione

`avvia_ultima_versione.sh` (12/11) fa partire il robot **sempre con l'ultima versione** copiata sul Raspberry. Così non
serve più il comando `ln -sfn ... ~/ClaudeRob_GARA` a ogni versione nuova.

A ogni accensione:
1. sceglie la cartella `~/ClaudeRob_V<n>` con il **numero più alto** che contiene `RwdFoto.py` (una cartella vuota o
   copiata a metà viene saltata; nomi come `ClaudeRob_V46_copia` vengono ignorati);
2. se mancano **o sono vuoti** (26/11: copia interrotta, file a 0 byte, YOLO dava `IndexError: list index out of range`), ci copia
   i **4 modelli YOLO** da `/home/pi` o dall'ultima versione che li ha buoni; quelli vuoti li sposta in `~/modelli_rotti_<data>`;
3. rende eseguibile `avvia.sh`;
4. sposta `~/ClaudeRob_GARA` su quella cartella, scrive quale versione parte (con l'impronta) e la fa partire.

Quello che fa lo scrive anche in `~/avvio_robot.log`. Non cancella niente.

## Restare su una versione (per esempio per tornare indietro)

```
echo ClaudeRob_V43 > ~/ClaudeRob_FISSA
```
Finché c'è questo file parte quella versione. Per tornare all'ultima: `rm ~/ClaudeRob_FISSA`.

## Metterlo sul robot (una volta sola)

Dal terminale del robot (`pi@master:~ $`):
```
curl -L -o ~/avvia_ultima_versione.sh https://raw.githubusercontent.com/Giooooonni93/Robocassano27/main/Raspberry/avvia_ultima_versione.sh
chmod +x ~/avvia_ultima_versione.sh
cp ~/.config/labwc/autostart ~/.config/labwc/autostart.prima_del_12nov_ultima
echo 'env LANG=C.UTF-8 LC_ALL=C.UTF-8 lxterminal --geometry=120x40 -e /home/pi/avvia_ultima_versione.sh &' > ~/.config/labwc/autostart
```
Poi `sudo reboot`. Per tornare all'avvio di prima:
`cp ~/.config/labwc/autostart.prima_del_12nov_ultima ~/.config/labwc/autostart`.

## Avviarlo a mano dal terminale del robot (in VNC, non da SSH)

```
env LANG=C.UTF-8 LC_ALL=C.UTF-8 ~/avvia_ultima_versione.sh
```
Prima controllate che non stia già girando: `pgrep -af RwdFoto`.
