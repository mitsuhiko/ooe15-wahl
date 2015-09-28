#!/bin/bash

CODES="40000 40100 40200 40300 40400 40500 40600 40700 40800 40900 41000 41100 41200 41300 41400 41500 41600 41700 41800"

for code in $CODES; do
  curl "http://wahltube.orf.at/ltwgrwooe15/$code.json?_cache=28-0-5" -H 'Pragma: no-cache' -H 'Origin: http://orf.at' -H 'Accept-Encoding: gzip, deflate, sdch' -H 'Accept-Language: en-US,en;q=0.8,de;q=0.6,fr;q=0.4' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.99 Safari/537.36' -H 'Accept: application/json, text/javascript, */*; q=0.01' -H 'Referer: http://orf.at/wahl/ooe15/' -H 'Connection: keep-alive' -H 'Cache-Control: no-cache' --compressed > $code.json
done
