#!/bin/bash

ZIP=$1
if [[ ! -e $ZIP ]]; then
  echo $ZIP not found.
  exit 1
fi

CODE=$(dirname $0)
PROCESSOR=$CODE/googlevoice_to_sqlite.py
SQL=$CODE/queries.sql

DIR=$(mktemp -d)
pushd $DIR
unzip $ZIP > /dev/null

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
