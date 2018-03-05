#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
python "$DIR/update_status.py" "$DIR/config.ini"
