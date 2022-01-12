#!/bin/zsh
set -x
java -jar -Xms3g -Xmx6g AQL-System-1.1.0-SNAPSHOT.jar -t 1m -reset -c ${1} -q "Flows IN App('${2}') ?" -o ${3}
