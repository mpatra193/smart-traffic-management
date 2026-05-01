import pandas as pd
import numpy as np
import os

def generate_synthetic_data(num_samples=2000):
    np.random.seed(42)
    
    # Features
    ns_vehicles = np.random.randint(0, 50, size=num_samples)
    ew_vehicles = np.random.randint(0, 50, size=num_samples)
    time_of_day = np.random.randint(0, 24, size=num_samples)
    is_emergency = np.random.choice([0, 1], size=num_samples, p=[0.95, 0.05])
    
    # Target variable generation (mathematical logic mimicking Webster's equation / sensible heuristics)
    optimal_green_ns = []
    optimal_green_ew = []
    
    for i in range(num_samples):
        ns = ns_vehicles[i]
        ew = ew_vehicles[i]
        emerg = is_emergency[i]
        
        if emerg:
            # Assume emergency is randomly coming from NS 50% of the time, EW 50% of the time
            if np.random.rand() > 0.5:
                optimal_green_ns.append(60)
                optimal_green_ew.append(10)
            else:
                optimal_green_ns.append(10)
                optimal_green_ew.append(60)
        else:
            total = ns + ew
            if total == 0:
                optimal_green_ns.append(30)
                optimal_green_ew.append(30)
            else:
                # Cycle time between 40s and 120s based on total traffic
                cycle_length = min(120, max(40, total * 1.5))
                
                # Split based on ratio
                ns_ratio = ns / total
                ew_ratio = ew / total
                
                # Calculate times with min green 15s
                g_ns = max(15, int(cycle_length * ns_ratio))
                g_ew = max(15, int(cycle_length * ew_ratio))
                
                optimal_green_ns.append(g_ns)
                optimal_green_ew.append(g_ew)

    df = pd.DataFrame({
        'ns_vehicles': ns_vehicles,
        'ew_vehicles': ew_vehicles,
        'time_of_day': time_of_day,
        'is_emergency': is_emergency,
        'optimal_green_ns': optimal_green_ns,
        'optimal_green_ew': optimal_green_ew
    })
    
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    csv_path = os.path.join(data_dir, 'synthetic_traffic_data.csv')
    df.to_csv(csv_path, index=False)
    print(f"Generated {num_samples} records of synthetic traffic data at {csv_path}")

if __name__ == '__main__':
    generate_synthetic_data()
