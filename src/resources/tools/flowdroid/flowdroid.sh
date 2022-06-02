#!/bin/bash
java -Xmx${1}g -javaagent:/AndroidTA_FaultLocalization/instrumentation/MultiPhaseInstrumenter/target/MultiPhaseInstrumenter-1.0.0-jar-with-dependencies.jar -jar %FLOWDROID_HOME%/soot-infoflow-cmd/target/soot-infoflow-cmd-jar-with-dependencies.jar -a ${2} -p ${3} -s %SOURCE_SINK_LOCATION% %CONFIG% > ${4} 2>&1
