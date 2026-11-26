#!/bin/bash
# =====================================================================================================================
#  AVVIO DEL ROBOT CON L'ULTIMA VERSIONE (12/11). Lo lancia l'avvio automatico all'accensione (~/.config/labwc/autostart).
#  1) sceglie la cartella ~/ClaudeRob_V<n> con il numero PIÙ ALTO che contiene RwdFoto.py
#     (oppure quella scritta nel file ~/ClaudeRob_FISSA, per restare su una versione: echo ClaudeRob_V43 > ~/ClaudeRob_FISSA;
#      per tornare all'ultima: rm ~/ClaudeRob_FISSA);
#  2) se mancano o sono vuoti (26/11), ci copia i 4 modelli YOLO da /home/pi o dall'ultima versione che li ha buoni;
#  3) rende eseguibile avvia.sh;
#  4) sposta ~/ClaudeRob_GARA su quella cartella e fa partire il programma.
#  Così, per una versione nuova, basta copiare la cartella sul robot (scp o FileZilla, come cartella) e riavviare.
#  Non cancella niente. Quello che fa lo scrive anche in ~/avvio_robot.log.
# =====================================================================================================================
CASA=${CASA_ROBOT:-/home/pi}      # (CASA_ROBOT solo per le prove)
LOG="$CASA/avvio_robot.log"
MODELLI="best_ncnn_model_Cross3 best_ncnn_model_PalCol3 best_ncnn_model_TrianFull3 best_ncnn_model_Exit3"
dici() { echo "$1"; echo "$(date '+%d/%m %H:%M:%S') $1" >> "$LOG"; }
cd "$CASA" || exit 1

SCELTA=""
if [ -f "$CASA/ClaudeRob_FISSA" ]; then
    SCELTA=$(head -n 1 "$CASA/ClaudeRob_FISSA" | tr -d '[:space:]')
    if [ -f "$CASA/$SCELTA/RwdFoto.py" ]; then
        dici "Versione FISSATA nel file ClaudeRob_FISSA: $SCELTA"
    else
        dici "ATTENZIONE: ClaudeRob_FISSA dice '$SCELTA' ma la cartella non c'è (o è senza RwdFoto.py): uso l'ultima"
        SCELTA=""
    fi
fi
if [ -z "$SCELTA" ]; then
    # le cartelle ClaudeRob_V<numero> in ordine di numero, dalla più alta: la prima con RwdFoto.py
    for d in $(ls -d ClaudeRob_V[0-9]* 2>/dev/null | grep -E '^ClaudeRob_V[0-9]+$' | sed 's/^ClaudeRob_V//' | sort -n -r); do
        if [ -f "$CASA/ClaudeRob_V$d/RwdFoto.py" ]; then SCELTA="ClaudeRob_V$d"; break; fi
    done
fi
if [ -z "$SCELTA" ]; then
    dici "ERRORE: nessuna cartella ClaudeRob_V<n> con RwdFoto.py in $CASA"
    read -r -p "Premi Invio per chiudere" _
    exit 1
fi

# (26/11) un modello è BUONO se model.ncnn.bin pesa più di 1 MB e model.ncnn.param più di 1 kB. Il 26/11 nella
# ClaudeRob_V60 c'erano le cartelle dei modelli ma con i file a 0 byte (copia interrotta): YOLO dava
# "IndexError: list index out of range" e prima lo script non se ne accorgeva (guardava solo se la cartella c'era).
buono() { [ "$(stat -c %s "$1/model.ncnn.bin" 2>/dev/null || echo 0)" -gt 1000000 ] && \
          [ "$(stat -c %s "$1/model.ncnn.param" 2>/dev/null || echo 0)" -gt 1000 ]; }
for m in $MODELLI; do
    if buono "$CASA/$SCELTA/$m"; then continue; fi
    # da dove copiarlo: /home/pi, oppure la versione più recente che lo ha buono
    SORGENTE=""
    if buono "$CASA/$m"; then SORGENTE="$CASA/$m"; fi
    if [ -z "$SORGENTE" ]; then
        for d in $(ls -d ClaudeRob_V[0-9]* 2>/dev/null | grep -E '^ClaudeRob_V[0-9]+$' | sed 's/^ClaudeRob_V//' | sort -n -r); do
            if [ "ClaudeRob_V$d" != "$SCELTA" ] && buono "$CASA/ClaudeRob_V$d/$m"; then SORGENTE="$CASA/ClaudeRob_V$d/$m"; break; fi
        done
    fi
    if [ -z "$SORGENTE" ]; then
        dici "ATTENZIONE: il modello $m manca o è vuoto in $SCELTA e non ne trovo uno buono da copiare"
        continue
    fi
    if [ -e "$CASA/$SCELTA/$m" ]; then           # quello rotto si sposta da parte (non si cancella niente)
        ROTTI="$CASA/modelli_rotti_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$ROTTI" && mv "$CASA/$SCELTA/$m" "$ROTTI/${SCELTA}_$m"
        dici "Il modello $m in $SCELTA era VUOTO o incompleto: spostato in $ROTTI"
    fi
    cp -r "$SORGENTE" "$CASA/$SCELTA/" && dici "Copiato il modello $m in $SCELTA (da $SORGENTE)"
done
chmod +x "$CASA/$SCELTA/avvia.sh" 2>/dev/null

PRIMA=$(readlink "$CASA/ClaudeRob_GARA")
ln -sfn "$CASA/$SCELTA" "$CASA/ClaudeRob_GARA"
IMPRONTA=$(cd "$CASA/$SCELTA" && for f in $(LC_ALL=C ls *.py); do echo -n "$f"; cat "$f"; done | sha256sum | cut -c1-16)
if [ "$PRIMA" != "$CASA/$SCELTA" ]; then
    dici "ClaudeRob_GARA spostato: ${PRIMA:-(nessuno)} -> $CASA/$SCELTA"
fi
dici "Parte $SCELTA (impronta $IMPRONTA)"
cd "$CASA/ClaudeRob_GARA" && exec ./avvia.sh
