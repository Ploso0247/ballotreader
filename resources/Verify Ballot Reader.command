#!/bin/bash
# verify_ballot_reader.command

# Determine the directory of the script
PERSIOSDIR="$(cd "$(dirname "$0")" && pwd)"

# Path to your application (assuming it's in the same directory as the script)
BR_PATH="$PERSIOSDIR/Ballot Reader v1.0.app"
CHROME_PATH="$PERSIOSDIR/chrome-mac/Chromium.app"


# Remove the quarantine attribute
xattr -d com.apple.quarantine "$BR_PATH"
xattr -d com.apple.quarantine "$CHROME_PATH"

echo "Quarantine attribute removed from $BR_PATH"
echo "Quarantine attribute removed from $CHROME_PATH"

Osascript -e 'tell application "Terminal" to close first window' &