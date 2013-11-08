#!/bin/bash

ARCHIVE=$1
if [[ ! -e $ARCHIVE ]]; then
  echo $ARCHIVE not found.
  exit 1
fi

CODE=$(cd $(dirname $0) && pwd -P )
PROCESSOR=$CODE/googlevoice_to_sqlite.py
SQL=$CODE/queries.sql

if [[ ${ARCHIVE##*.} == "zip" ]]; then
  CMD=unzip
  ARG=
elif [[ ${ARCHIVE##*.} == "tgz" ]]; then
  CMD=tar
  ARG=xvzf
else
  echo Unknown archive type.
  exit 1
fi

DIR=$(mktemp -d)
pushd $DIR

$CMD $ARG $ARCHIVE > /dev/null

# generate sqlite
python $PROCESSOR */Voice/Calls < /dev/null
cd output
sqlite3 gvoice.sqlite < $SQL

# process people/year
for f in *.csv; do
  $CODE/smsgraph.py $f > ~/public_html/sms/$(basename $f .csv).html
done

# clean up
popd
rm -rf $DIR
