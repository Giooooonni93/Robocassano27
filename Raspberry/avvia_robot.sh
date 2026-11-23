#!/bin/bash
# =====================================================================================================================
#  AVVIO SEMPLICE DEL ROBOT (23/11). Un solo comando dal terminale del Raspberry (anche da SSH):
#
#      ~/avvia_robot.sh          parte l'ULTIMA versione (come all'accensione: avvia_ultima_versione.sh)
#      ~/avvia_robot.sh 55       parte la ClaudeRob_V55 (per provare una versione vecchia)
#
#  Cosa fa:
#  1) se il programma del robot sta già girando lo ferma (ne può girare uno solo: FIX 110) e aspetta che si chiuda;
#  2) apre sullo SCHERMO DEL ROBOT (anche se lo lanciate da SSH) una finestra grande 120 x 40 in UTF-8: la cabina con le
#     due camere si vede (serve almeno 100 x 38, e senza UTF-8 è illeggibile);
#  3) se il programma si chiude (errore, Ctrl+C) la finestra RESTA APERTA con le ultime scritte, finché premete Invio.
#  Non cancella niente.
# =====================================================================================================================
CASA=${CASA_ROBOT:-/home/pi}

if [ -n "$1" ]; then
    NOME="$1"
    case "$NOME" in ClaudeRob_V*) ;; *) NOME="ClaudeRob_V${NOME#V}" ;; esac
    if [ ! -f "$CASA/$NOME/RwdFoto.py" ]; then
        echo "Non trovo $CASA/$NOME/RwdFoto.py: la versione non è sul robot."
        exit 1
    fi
    chmod +x "$CASA/$NOME/avvia.sh" 2>/dev/null
    COMANDO="cd '$CASA/$NOME' && ./avvia.sh"
    echo "Parto con $NOME"
else
    COMANDO="'$CASA/avvia_ultima_versione.sh'"
    echo "Parto con l'ultima versione"
fi

# 1) un solo programma alla volta: solo "python3 ... RwdFoto.py" (non un editor che ha il file aperto)
ROBOT='^python[0-9.]* ([^ ]*/)?RwdFoto\.py'
if pgrep -f "$ROBOT" >/dev/null; then
    echo "Il programma del robot sta già girando: lo fermo..."
    pkill -f "$ROBOT"
    for i in $(seq 1 20); do
        sleep 0.25
        pgrep -f "$ROBOT" >/dev/null || break
    done
    if pgrep -f "$ROBOT" >/dev/null; then
        pkill -9 -f "$ROBOT"
        sleep 0.5
    fi
fi

# 2) la finestra va sullo schermo del robot, anche se questo comando arriva da SSH
export DISPLAY=${DISPLAY:-:0}
export XDG_RUNTIME_DIR=${XDG_RUNTIME_DIR:-/run/user/$(id -u)}
if [ -z "$WAYLAND_DISPLAY" ]; then
    for sock in "$XDG_RUNTIME_DIR"/wayland-[0-9]; do        # labwc: di solito wayland-0 (a volte wayland-1)
        if [ -S "$sock" ]; then export WAYLAND_DISPLAY=$(basename "$sock"); break; fi
    done
fi

# 3) finestra grande in UTF-8; quando il programma finisce la finestra resta aperta
env LANG=C.UTF-8 LC_ALL=C.UTF-8 lxterminal --geometry=120x40 \
    -e bash -c "$COMANDO; echo; read -r -p 'Programma del robot finito. Premi Invio per chiudere la finestra' _" &
echo "Fatto: guardate lo schermo del robot (o VNC). Per fermarlo: Ctrl+C nella sua finestra."
