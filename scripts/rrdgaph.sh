#!/bin/bash

DBs="LAT:Lat:G:A:° LON:Lon:G:A:° HGHT:Hght:G:A:m FLTSX:FloatX:G:A:m FLTSY:FloatY:G:A:m FLTSZ:FloatZ:G:A:m RSAT:RovSats:G:A: BSAT:BasSats:G:A: VSAT:ValSats:G:A: ARR:ARratio:G:A: BLINE:Baseline:G:A:m DAGE:DiffAge:G:X:s RTIME:Runtime:C:N:s"

DURATIONS="30m 1d 2w 2y"
export TMPDIR="/tmp"
export DBDIR="/var/lib/rrdcached/db"

RRD_GRAPH='rrdtool graph ${TMPDIR}/rtkrcv_${DBl}_${DUR}.png -a PNG --end now --start end-${DUR} --alt-autoscale "DEF:${DB}=${DBDIR}/rtkrcv_${DBl}.rrd:${DESC}:${AGGR}:step=1" "LINE1:${DB}#ff0000:${DESC}" "GPRINT:${DB}:AVERAGE:Average\: %9.6lf${UNIT}"'

echo FLUSHALL | socat - UNIX-CONNECT:/var/run/rrdcached.sock
sleep 10

for ENTRY in ${DBs} ; do
  DB="`echo ${ENTRY} | cut -d ':' -f 1`"
  DBl="`echo ${DB} | tr '[:upper:]' '[:lower:]'`"

  DESC="`echo ${ENTRY} | cut -d ':' -f 2`"

  TEMP="`echo ${ENTRY} | cut -d ':' -f 3`"
  case TEMP in
    A) TYPE="ABSOLUTE" ;;
    C) TYPE="COUNTER" ;;
    D) TYPE="DERIVE" ;;
    G) TYPE="GAUGE" ;;
    *) TYPE="GAUGE" ;;
  esac

  TEMP="`echo ${ENTRY} | cut -d ':' -f 4`"
  case TEMP in
    A) AGGR="AVERAGE" ;;
    L) AGGR="LAST" ;;
    N) AGGR="MIN" ;;
    X) AGGR="MAX" ;;
    *) AGGR="AVERAGE" ;;
  esac

  UNIT="`echo ${ENTRY} | cut -d ':' -f 5`"

  export DB DBl DESC TYPE AGGR UNIT

  for DUR in ${DURATIONS} ; do
    export DUR
    COMMAND="`echo ${RRD_GRAPH} | envsubst`"
    echo ${COMMAND}
    eval ${COMMAND}
    done
  done


