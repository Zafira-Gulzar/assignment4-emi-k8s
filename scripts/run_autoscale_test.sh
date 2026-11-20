#!/bin/bash

echo "timestamp,replicas,cpu_target" > ~/assignment4/results/m4_raw/hpa_metrics.csv

# Background process to monitor HPA every 15 seconds
(
  while true; do
    ts=$(date +%s)
    hpa_info=$(kubectl get hpa emi-web -n emi --no-headers)
    replicas=$(echo $hpa_info | awk '{print $6}') 
    cpu=$(echo $hpa_info | awk '{print $3}')
    echo "$ts,$replicas,$cpu" >> ~/assignment4/results/m4_raw/hpa_metrics.csv
    sleep 15
  done
) &
MONITOR_PID=$!

echo "Starting Autoscale Test (10 minutes total)..."

echo "Phase 1: 2 minutes at ~10 req/s"
ab -t 120 -c 2 -p ~/assignment4/scripts/post_data.txt -T "application/x-www-form-urlencoded" http://emi.local/api/emi > /dev/null

echo "Phase 2: 5 minutes at ~100 req/s"
ab -t 300 -c 15 -p ~/assignment4/scripts/post_data.txt -T "application/x-www-form-urlencoded" http://emi.local/api/emi > /dev/null

echo "Phase 3: 3 minutes at ~10 req/s"
ab -t 180 -c 2 -p ~/assignment4/scripts/post_data.txt -T "application/x-www-form-urlencoded" http://emi.local/api/emi > /dev/null

echo "Test complete. Stopping HPA monitor..."
kill $MONITOR_PID
echo "Done!"
