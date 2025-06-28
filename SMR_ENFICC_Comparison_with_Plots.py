
import numpy as np
import matplotlib.pyplot as plt

# Reactor parameters
P_n = 300  # MW
hours_per_year = 8760
maintenance_days = 25
scram_rate = 0.5
scram_duration_min = 36
scram_duration_max = 60
iterations = 10000
monthly_hours = [31*24,28*24,31*24,30*24,31*24,30*24,31*24,31*24,30*24,31*24,30*24,31*24]
months = [f'M{m+1}' for m in range(12)]

# Hydrological derating factors for A1
F_H = np.array([0.95, 0.92, 0.88, 0.90, 0.87, 0.85, 0.86, 0.89, 0.91, 0.94, 0.96, 0.97])
F_T = 0.97  # Thermal adjustment for A2

def simulate_group(apply_fh=False, apply_ft=False):
    results = np.zeros((iterations, 12))
    for i in range(iterations):
        availability = np.ones(hours_per_year)

        # Scheduled maintenance
        maint_start = np.random.randint(0, hours_per_year - maintenance_days * 24)
        availability[maint_start:maint_start + maintenance_days * 24] = 0

        # SCRAM events
        n_scrams = np.random.poisson(scram_rate)
        for _ in range(n_scrams):
            scram_start = np.random.randint(0, hours_per_year)
            scram_duration = np.random.randint(scram_duration_min, scram_duration_max + 1)
            scram_end = min(scram_start + scram_duration, hours_per_year)
            availability[scram_start:scram_end] = 0

        # Monthly energy calculation
        hour_index = 0
        for m in range(12):
            month_hours = monthly_hours[m]
            effective_hours = np.sum(availability[hour_index:hour_index + month_hours])
            energy = effective_hours * P_n
            if apply_fh:
                energy *= F_H[m]
            results[i, m] = energy
            hour_index += month_hours
    return results

# Run simulations
results_a1 = simulate_group(apply_fh=True)
results_a2 = simulate_group()
results_b  = simulate_group()

# Compute P5% and ENFICC
p5_a1 = np.percentile(results_a1, 5, axis=0)
p5_a2 = np.percentile(results_a2, 5, axis=0) * F_T
p5_b  = np.percentile(results_b, 5, axis=0)

enficc_a1 = np.min(p5_a1)
enficc_a2 = np.min(p5_a2)
enficc_b  = np.min(p5_b)

# Plotting
def plot_group(p5, enficc, title, color):
    plt.figure(figsize=(8, 5))
    plt.bar(months, p5 / 1000, color=color)
    plt.axhline(enficc / 1000, color='red', linestyle='--', label=f'ENFICC: {enficc/1000:.1f} GWh')
    plt.ylabel('Monthly Firm Energy (GWh)')
    plt.title(title)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()

plot_group(p5_a1, enficc_a1, 'Group A1 – 300 MW freshwater-cooled SMR', 'steelblue')
plot_group(p5_a2, enficc_a2, 'Group A2 – 300 MW seawater-cooled SMR', 'seagreen')
plot_group(p5_b, enficc_b, 'Group B – 300 MW non-water-cooled SMR', 'darkorange')

# Print ENFICC values
print("ENFICC values (GWh):")
print("Group A1:", round(enficc_a1 / 1000, 2))
print("Group A2:", round(enficc_a2 / 1000, 2))
print("Group B :", round(enficc_b / 1000, 2))
