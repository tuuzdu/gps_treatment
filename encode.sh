#!/bin/bash
#enter input encoding here
FROM_ENCODING="cp1251"
#output encoding(UTF-8)
TO_ENCODING="UTF-8"
#convert
CONVERT=" iconv  -f   $FROM_ENCODING  -t   $TO_ENCODING"
#loop to convert multiple files 
for  file  in  *.log; do
     $CONVERT   "$file"   -o  "utf-${file%.log}.log"
done
exit 0