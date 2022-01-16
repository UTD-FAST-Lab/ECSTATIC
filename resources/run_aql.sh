#!/bin/zsh
set -x
java -jar AQL-System-1.1.0-SNAPSHOT.jar -t 10m -reset -c ${1} -q "Flows IN App('${2}') ?" -o ${3}
