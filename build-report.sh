#!/bin/bash

PACKAGE_NAME=""
REPO_NAME=""
REPORT_PATH="report"

# Handle arguments
while [[ $# > 0 ]]; do
    key="$1"

    case $key in
        -h|--help)
            echo "build-report --package package --repo repo"
            exit 0
        ;;
        --package)
            shift
            readonly PACKAGE_NAME="$1"
        ;;
        --repo)
            shift
            readonly REPO_NAME="$1"
        ;;
        *)
            echo "Unknown option $1"
            exit 1
        ;;
    esac
    shift
done

# Validate arguments
if [[ -z ${PACKAGE_NAME} ]]; then
    echo "package is empty or invalid."
    exit 1
elif [[ -z ${REPO_NAME} ]]; then
    echo "repo is empty or invalid."
    exit 1
fi

mkdir "$REPORT_PATH"

echo "Copy unit tests report"
cp app/build/reports/tests/testDebugUnitTest/index.html "$REPORT_PATH/unittests.html"

echo "Fetching build_report.py"
curl https://raw.githubusercontent.com/blacklane/zulu-scripts/master/buildreport/build_report.py -o "$REPORT_PATH/build_report.py"

echo "Building report"
python "$REPORT_PATH/build_report.py" --report=$REPORT_PATH --package=$PACKAGE_NAME --githubtoken=$GITHUB_TOKEN --repo=$REPO_NAME --branch=$BRANCH_NAME --phraseapptoken=$PHRASEAPP_TOKEN
