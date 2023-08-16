#!/usr/bin/env bash

# Send a notification using ntfy

PROGRAM_NAME=$0

function usage {
    echo ""
    echo "Publish a message to an ntfy server."
    echo ""
    echo "usage: $PROGRAM_NAME -s string -t string -m string -a string -h string"
    echo ""
    echo "  -s string     URL of the ntfy server, must start with http(s)://"
    echo "                  (example: https://ntfy.sh)"
    echo "  -t string     topic to publish to"
    echo "                  (example: mytopic)"
    echo "  -m string     message to publish"
    echo "                  (example: \"Hello World\")"
    echo "  -a string     authentication pair (optional)"
    echo "                  (example: username:password)"
    echo "  -h string...  headers to add to the request (optional), must be semicolon-separated"
    echo "                  (example: \"Priority: low\",\"Title: my title\")"
    echo ""
}

function die {
    printf "Script failed: %s\n\n" "$1"
    exit 1
}

while getopts s:t:m:a:h: flag
do
    case "${flag}" in
        s) server=${OPTARG};;
        t) topic=${OPTARG};;
        m) message=${OPTARG};;
        a) auth=${OPTARG};;
        h) headers=${OPTARG};;
        *) usage
           exit 1;;
    esac
done

# Check if all required parameters are set
if [[ -z $server ]]; then
    usage
    die "Missing parameter '-s server_url'"
elif [[ -z $topic ]]; then
    usage
    die "Missing parameter '-t topic'"
elif [[ -z $message ]]; then
    usage
    die "Missing parameter '-m message'"
fi

# If headers is set, add it to the curl command
headers_string=""
# If headers is set, parse it
if [[ -n $headers ]]; then
    # Split the headers string by comma into an array
    IFS=';' read -ra HEADERS <<< "$headers"
    # Loop through the headers array
    for header in "${HEADERS[@]}"; do
        headers_string="$headers_string -H $header"
    done
fi


# If auth is set, add it to the curl command
auth_string=""
if [[ -n $auth ]]; then
    auth_string="-u $auth"
fi

url="$server/$topic"

command="curl -X POST $headers_string $auth_string -d \"$message\" \"$url\""
echo "$command"
eval "$command"
