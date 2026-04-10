#!/bin/bash
# Check if a /lop sample is overdue
# Used as a SessionStart hook reminder

CALIBRATION_FILE="data/calibration.yaml"
if [ ! -f "$CALIBRATION_FILE" ]; then
  exit 0
fi

# Get the last calibration date
LAST_DATE=$(grep '  - date:' "$CALIBRATION_FILE" | tail -1 | sed 's/.*date: *"//' | sed 's/"//')
if [ -z "$LAST_DATE" ]; then
  exit 0
fi

# Calculate days since last sample
LAST_EPOCH=$(date -j -f "%Y-%m-%d" "$LAST_DATE" "+%s" 2>/dev/null)
NOW_EPOCH=$(date "+%s")
if [ -z "$LAST_EPOCH" ]; then
  exit 0
fi

DAYS_AGO=$(( (NOW_EPOCH - LAST_EPOCH) / 86400 ))

if [ "$DAYS_AGO" -ge 5 ]; then
  echo "📊 Calibration reminder: last /lop sample was ${DAYS_AGO} days ago (${LAST_DATE}). Consider running one to keep the calibration delta in check."
fi
