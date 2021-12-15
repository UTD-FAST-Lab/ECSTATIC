#!/bin/zsh
set -x
java -Xmx${1}g -jar %FLOWDROID_HOME%/soot-infoflow-cmd/target/soot-infoflow-cmd-jar-with-dependencies.jar -a ${2} -p ${3} -s %SOURCE_SINK_LOCATION% %CONFIG% > ${4} 2>&1