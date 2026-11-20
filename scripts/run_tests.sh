#!/bin/bash

# Define concurrency levels for rates (Approx 10, 25, 50, 100, 200 req/s based on 140ms latency)
CONCURRENCIES=(2 4 8 15 30) 
RATES=(10 25 50 100 200)

for REPLICAS in 1 2 3; do
    echo "=================================================="
    echo "SCALING TO $REPLICAS REPLICAS..."
    kubectl scale deployment emi-web --replicas=$REPLICAS -n emi
    echo "Waiting 20 seconds for pods to be ready..."
    sleep 20

    for i in "${!CONCURRENCIES[@]}"; do
        C=${CONCURRENCIES[$i]}
        R=${RATES[$i]}
        echo "Running test: $REPLICAS Replicas | Target: ~$R req/s (Concurrency: $C)"
        
        # Run ab for 60 seconds (-t 60) and save raw output
        ab -t 60 -c $C -p ~/assignment4/scripts/post_data.txt -T "application/x-www-form-urlencoded" http://emi.local/api/emi > ~/assignment4/results/m4_raw/rep${REPLICAS}_rate${R}.txt
        
        # Extract Key Metrics and append to summary CSV
        REQ_SEC=$(grep "Requests per second:" ~/assignment4/results/m4_raw/rep${REPLICAS}_rate${R}.txt | awk '{print $4}')
        TIME_MEAN=$(grep "Time per request:" ~/assignment4/results/m4_raw/rep${REPLICAS}_rate${R}.txt | head -n 1 | awk '{print $4}')
        FAILED=$(grep "Failed requests:" ~/assignment4/results/m4_raw/rep${REPLICAS}_rate${R}.txt | awk '{print $3}')
        
        # If failed is empty (0 failures), set to 0
        if [ -z "$FAILED" ]; then FAILED=0; fi
        
        echo "$REPLICAS,$R,$REQ_SEC,$TIME_MEAN,$FAILED" >> ~/assignment4/results/summary.csv
    done
done
echo "All tests completed! Check summary.csv"
