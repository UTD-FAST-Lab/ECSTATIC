#!/bin/bash
if [ -z "$4" ]; then
  java -jar AQL-System-1.1.0-SNAPSHOT.jar -reset -c "${1}" -q "Flows IN App('${2}') ?" -o "${3}"
else
  java -jar AQL-System-1.1.0-SNAPSHOT.jar -t "${4}"m -reset -c "${1}" -q "Flows IN App('${2}') ?" -o "${3}"
fi
