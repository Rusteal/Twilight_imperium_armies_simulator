import numpy as np
from scipy.stats import binom, norm, truncnorm
from Ships import *  # assuming Ships module is present with the Default classes

# Function to calculate statistics using a Simulation-based approach
def get_statistics_simulation(army: list[Ship], num_simulations=10000):
    # Initialize statistics
    hits = []
    sustain_damage_ships = 0
    movement_values = []
    total_capacity = 0
    
    # List to store the simulated total hits for the entire army
    simulated_hits = []
    
    for _ in range(num_simulations):  # Repeat simulation multiple times
        total_hits_in_simulation = 0
        
        for ship in army:
            p_hit = (11 - ship.combat) / 10  # Probability of success (hit)
            n_trials = ship.hits  # Number of trials (hits per ship)
            
            # Simulate the number of hits for this ship using binomial distribution
            hits_for_ship = binom.rvs(n_trials, p_hit)
            total_hits_in_simulation += hits_for_ship
        
        # Store the total hits from this simulation
        simulated_hits.append(total_hits_in_simulation)
    
    # Calculate mean and variance of total hits from the simulation
    mean_total_hits = sum([ship.hits * (11 - ship.combat) / 10 for ship in army])
    variance_total_hits = sum([
        ship.hits * ((11 - ship.combat) / 10) * (1 - (11 - ship.combat) / 10)
        for ship in army
    ])
    std_dev_total_hits = np.sqrt(variance_total_hits)
    
    # Calculate quantiles (1%, 10%, 25%, 50%, 75%, 90%, 99%)
    quantiles_hits = np.percentile(simulated_hits, [1, 10, 25, 33, 50, 66, 75, 90, 99])
    
    # Clamp negative quantiles to zero
    quantiles_hits = [max(0, q) for q in quantiles_hits]  # Ensuring no negative quantiles
    
    # Calculate army health (number of ships + sustain damage ships)
    sustain_damage_ships = sum([1 for ship in army if ship.sustain_damage])
    army_health = len(army) + sustain_damage_ships
    
    # Calculate the lowest movement value in the army
    movement_values = [ship.move for ship in army]
    lowest_movement = min(movement_values)
    
    # Calculate the total capacity
    total_capacity = sum([ship.capacity for ship in army])
    total_cost = sum([ship.cost for ship in army])
    
    # Return the statistics as a formatted string
    statistics = f"""
    Army Statistics (Simulation-based):
    ----------------
    Mean Hits: {mean_total_hits:.2f}
    Variance of Hits: {variance_total_hits:.2f}
    Standard Deviation of Hits: {std_dev_total_hits:.2f}
    1% Quantile of Hits: {quantiles_hits[0]:.2f}
    10% Quantile of Hits: {quantiles_hits[1]:.2f}
    25% Quantile of Hits: {quantiles_hits[2]:.2f}
    33% Quantile of Hits: {quantiles_hits[3]:.2f}
    50% Quantile of Hits (Median): {quantiles_hits[4]:.2f}
    66% Quantile of Hits: {quantiles_hits[5]:.2f}
    75% Quantile of Hits: {quantiles_hits[6]:.2f}
    90% Quantile of Hits: {quantiles_hits[7]:.2f}
    99% Quantile of Hits: {quantiles_hits[8]:.2f}
    
    Army Cost: {total_cost}
    Army Health (Number of Ships + Sustain Damage): {army_health}
    Army Movement (Lowest Movement Value): {lowest_movement}
    Army Capacity (Total Capacity of Ships): {total_capacity}
    """
    
    return statistics


# Function to calculate statistics using a Normal Approximation approach
def get_statistics_normal(army: list[Ship], use_truncated_normal=False):
    # Initialize statistics
    hits = []
    sustain_damage_ships = 0
    movement_values = []
    total_capacity = 0
    
    # Calculate the mean and variance for the army based on normal approximation
    total_mean_hits = sum([ship.hits * (11 - ship.combat) / 10 for ship in army])  # Sum of individual means
    total_variance_hits = sum([ship.hits * (11 - ship.combat) / 10 * (1 - (11 - ship.combat) / 10) for ship in army])  # Sum of individual variances
    
    # Calculate standard deviation from the variance
    total_std_dev_hits = np.sqrt(total_variance_hits)
    
    # Calculate quantiles using the normal distribution (approximating with mean and variance)
    if use_truncated_normal:
        # Use truncated normal distribution (to avoid negative hits)
        a, b = (0 - total_mean_hits) / total_std_dev_hits, np.inf  # Truncate at zero
        quantiles_hits = truncnorm.ppf([0.01, 0.10, 0.25, 0.33, 0.50, 0.66, 0.75, 0.90, 0.99], a, b, loc=total_mean_hits, scale=total_std_dev_hits)
    else:
        # Use regular normal distribution
        quantiles_hits = norm.ppf([0.01, 0.10, 0.25, 0.33, 0.50, 0.66, 0.75, 0.90, 0.99], loc=total_mean_hits, scale=total_std_dev_hits)
    
    # Ensure quantiles don't go below zero if using normal distribution
    quantiles_hits = [max(0, q) for q in quantiles_hits]  # Ensuring no negative quantiles
    
    # Calculate army health (number of ships + sustain damage ships)
    sustain_damage_ships = sum([1 for ship in army if ship.sustain_damage])
    army_health = len(army) + sustain_damage_ships
    
    # Calculate the lowest movement value in the army
    movement_values = [ship.move for ship in army]
    lowest_movement = min(movement_values)
    
    # Calculate the total capacity
    total_capacity = sum([ship.capacity for ship in army])
    total_cost = sum([ship.cost for ship in army])

    # Return the statistics as a formatted string
    statistics = f"""
    Army Statistics (Normal Approximation):
    ----------------
    Mean Hits: {total_mean_hits:.2f}
    Variance of Hits: {total_variance_hits:.2f}
    Standard Deviation of Hits: {total_std_dev_hits:.2f}
    1% Quantile of Hits: {quantiles_hits[0]:.2f}
    10% Quantile of Hits: {quantiles_hits[1]:.2f}
    25% Quantile of Hits: {quantiles_hits[2]:.2f}
    33% Quantile of Hits: {quantiles_hits[3]:.2f}
    50% Quantile of Hits (Median): {quantiles_hits[4]:.2f}
    66% Quantile of Hits: {quantiles_hits[5]:.2f}
    75% Quantile of Hits: {quantiles_hits[6]:.2f}
    90% Quantile of Hits: {quantiles_hits[7]:.2f}
    99% Quantile of Hits: {quantiles_hits[8]:.2f}
    
    Army Cost: {total_cost}
    Army Health (Number of Ships + Sustain Damage): {army_health}
    Army Movement (Lowest Movement Value): {lowest_movement}
    Army Capacity (Total Capacity of Ships): {total_capacity}
    """
    
    return statistics


if __name__ == "__main__":
    army = [DefaultCruiser(), DefaultCruiser()]
    
    # Simulation-based approach
    print(get_statistics_simulation(army))
    
    # Normal approximation approach with truncated normal (no negative hits)
    print(get_statistics_normal(army, use_truncated_normal=True))
    
    # Normal approximation approach with regular normal distribution
    print(get_statistics_normal(army, use_truncated_normal=False))
