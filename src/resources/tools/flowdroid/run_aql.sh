#!/bin/bash
if [ -z "$4" ]; then
  java -jar AQL-System-1.1.1.jar -reset -c "${1}" -q "Flows IN App('${2}') ?" -o "${3}"
else
  java -jar AQL-System-1.1.1.jar -t "${4}"m -reset -c "${1}" -q "Flows IN App('${2}') ?" -o "${3}"
fi
