#!/bin/bash
DBs="LAT:Lat:G:A LON:Lon:G:A HGHT:Hght:G:A FLTSX:FloatX:G:A FLTSY:FloatY:G:A FLTSZ:FloatZ:G:A RSAT:RovSats:G:A BSAT:BasSats:G:A VSAT:ValSatsG:A ARR:ARratio:G:A BLINE:Baseline:G:A DAGE:DiffAge:G:X RTIME:Runtime:C:N"

RRD_CREATE='create rtkrcv_${DBl}.rrd -s 1 DS:${DESC}:${TYPE}:2:0:360 RRA:${AGGR}:0.5:1:1800 RRA:${AGGR}:0.5:60:1440 RRA:${AGGR}:0.5:3600:672 RRA:${AGGR}:0.5:86400:730'

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

  export DB DBl DESC TYPE AGGR
  echo "${RRD_CREATE}" | envsubst | socat - UNIX-CONNECT:/var/run/rrdcached.sock
  done

