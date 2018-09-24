#!/bin/bash

REPORT_PATH="report"

mkdir "$REPORT_PATH"

echo "Copy unit tests report"
cp app/build/reports/tests/testDebugUnitTest/index.html "$REPORT_PATH/unittests.html"

echo "Fetching build_report.py"
curl https://raw.githubusercontent.com/elgendyLanes/BuildReports/master/build_report.py -o "$REPORT_PATH/build_report.py"

echo "Building report"
python "$REPORT_PATH/build_report.py" --report=$REPORT_PATH
