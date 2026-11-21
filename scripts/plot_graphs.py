import pandas as pd
import matplotlib.pyplot as plt
import os

base_dir = os.path.expanduser('~/assignment4/results')
raw_dir = os.path.join(base_dir, 'm4_raw')

# Graph 1 (Waise hi rahega)
try:
    summary_path = os.path.join(base_dir, 'summary.csv')
    df_sum = pd.read_csv(summary_path)
    plt.figure(figsize=(10, 6))
    for replicas in [1, 2, 3]:
        subset = df_sum[df_sum['Replicas'] == replicas]
        plt.plot(subset['Target_Rate'], subset['Avg_Response_Time_ms'], marker='o', label=f'{replicas} Replica(s)')
    plt.title('Average Response Time vs Target Request Rate')
    plt.xlabel('Target Request Rate (req/s)')
    plt.ylabel('Average Response Time (ms)')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(base_dir, 'graph1_response_time.png'))
    plt.close()
    print("Graph 1 saved successfully.")
except Exception as e:
    print(f"Error creating Graph 1: {e}")

# Graph 2 (Bina kisi filter ke, jaisa aap chahti hain)
try:
    metrics_path = os.path.join(raw_dir, 'cpu_memory_metrics.csv')
    df_metrics = pd.read_csv(metrics_path)
    start_time = df_metrics['timestamp'].min()
    df_metrics['time_min'] = (df_metrics['timestamp'] - start_time) / 60.0
    
    df_metrics['cpu_val'] = df_metrics['cpu'].str.replace('m', '').astype(float)
    df_metrics['cpu_pct'] = (df_metrics['cpu_val'] / 100.0) * 100 
    
    plt.figure(figsize=(10, 6))
    for pod in df_metrics['pod_name'].unique():
        pod_data = df_metrics[df_metrics['pod_name'] == pod]
        plt.plot(pod_data['time_min'], pod_data['cpu_pct'], label=pod)
    plt.title('CPU Utilization (%) per Pod over Time')
    plt.xlabel('Time (minutes)')
    plt.ylabel('CPU Utilization (%)')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(base_dir, 'graph2_cpu_utilization.png'))
    plt.close()
    print("Graph 2 saved successfully.")
except Exception as e:
    print(f"Error creating Graph 2: {e}")

# Graph 3 (Sirf isme Request Rate ki line add ki gayi hai)
try:
    hpa_path = os.path.join(raw_dir, 'hpa_metrics.csv')
    df_hpa = pd.read_csv(hpa_path)
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Request Rate Data (2 min 10 req, 5 min 100 req, 3 min 10 req)
    time_axis = [0, 2, 2, 7, 7, 10]
    req_line = [10, 10, 100, 100, 10, 10]
    
    color = 'tab:red'
    ax1.set_xlabel('Time (minutes)')
    ax1.set_ylabel('CPU Utilization (%)', color=color)
    ax1.plot(df_hpa['time_min'], df_hpa['cpu_pct'], color=color, label='CPU %')
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  
    color = 'tab:blue'
    ax2.set_ylabel('Number of Replicas', color=color)  
    ax2.step(df_hpa['time_min'], df_hpa['replicas'], color=color, label='Replicas', where='post')
    ax2.tick_params(axis='y', labelcolor=color)
    
    ax3 = ax1.twinx()
    ax3.spines["right"].set_position(("axes", 1.1))
    ax3.set_ylabel('Request Rate (req/s)', color='tab:green')
    ax3.plot(time_axis, req_line, color='tab:green', linestyle='--', label='Request Rate')
    ax3.tick_params(axis='y', labelcolor='tab:green')
    
    plt.title('Autoscaling: CPU, Replicas, and Request Rate over Time')
    fig.tight_layout()
    plt.savefig(os.path.join(base_dir, 'graph3_autoscaling.png'))
    plt.close()
    print("Graph 3 saved successfully.")
except Exception as e:
    print(f"Error creating Graph 3: {e}")
