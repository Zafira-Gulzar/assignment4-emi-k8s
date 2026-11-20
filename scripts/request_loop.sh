#!/bin/bash
echo "Starting continuous request loop for 60 seconds..."
failures=0
successes=0
for i in {1..60}; do
    response=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://emi.local/api/emi \
      -H "Content-Type: application/json" \
      -d '{"principal": 50000, "rate": 8, "months": 6}')
    
    if [ "$response" -eq 200 ]; then
        successes=$((successes+1))
        echo "Request $i: SUCCESS (200)"
    else
        failures=$((failures+1))
        echo "Request $i: FAILED (HTTP $response)"
    fi
    sleep 1
done
echo "--- Request Loop Finished ---"
echo "Total Successes: $successes"
echo "Total Failures: $failures"
