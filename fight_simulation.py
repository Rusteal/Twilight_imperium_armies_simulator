from Ships import *  # assuming Ships module is present with the Default classes
import random
from collections import Counter
import numpy as np

def roll_hits(army: list[Ship]) -> int:
    if not army:
        return 0
    dice = np.random.randint(1, 11, size=len(army))  # Roll once for all ships
    thresholds = np.array([ship.combat for ship in army])
    return int(np.sum(dice >= thresholds))  # Count how many passed the combat value


# Function to simulate a fight between two armies
def simulate_fight(armies: list[list[Ship]], n_fights=10000):
    results = {"Army 1 Wins": 0, "Army 2 Wins": 0}
    remaining_ships = {"Army 1": [], "Army 2": []}
    full_survival = {"Army 1": 0, "Army 2": 0}

    
    for _ in range(n_fights):
        army_1, army_2 = armies
        
        # Create copies of the armies for each simulation
        army_1_ships = [ship.copy() for ship in army_1]
        army_2_ships = [ship.copy() for ship in army_2]
        
        # Apply precombat effects and return armies
        army1_post, army2_post = precombat_phase(army_1_ships, army_2_ships)
        army_1_ships, army_2_ships = army1_post, army2_post  # override once
        
        while army_1_ships and army_2_ships:
            # Roll a die for each ship and assign hits to the opposing army
            # NEW CODE – fast
            army_1_hits = roll_hits(army_1_ships)
            army_2_hits = roll_hits(army_2_ships)

            
            # Assign damage to the opposing army (first use sustain damage, then weakest combat ships)
            # Remove destroyed ships, do that in the assign damage function
            army_2_ships = assign_damage(army_2_ships, army_1_hits)
            army_1_ships = assign_damage(army_1_ships, army_2_hits)
            #repeat untill one of the lists is empty
            #print(f"Hits: A1={army_1_hits}, A2={army_2_hits}, A1 size={len(army_1_ships)}, A2 size={len(army_2_ships)}")


        # Check who won and log the result
        if army_1_ships and not army_2_ships:
            results["Army 1 Wins"] += 1
            if len(army_1_ships) == len(army_1):
                full_survival["Army 1"] += 1
            remaining_ships["Army 1"].append(tuple(str(ship.name) for ship in army_1_ships))

        elif army_2_ships and not army_1_ships:
            results["Army 2 Wins"] += 1
            if len(army_2_ships) == len(army_2):
                full_survival["Army 2"] += 1
            remaining_ships["Army 2"].append(tuple(str(ship.name) for ship in army_2_ships))

        else:
            results["Draws"] = results.get("Draws", 0) + 1

    # Calculate the probability of each army winning
    prob_army_1_win = results["Army 1 Wins"] / n_fights
    prob_army_2_win = results["Army 2 Wins"] / n_fights
    draw_rate = results.get("Draws", 0) / n_fights

    # Find the most frequent remaining ship combination
    most_frequent_army_1 = Counter(remaining_ships["Army 1"]).most_common(1)
    most_frequent_army_2 = Counter(remaining_ships["Army 2"]).most_common(1)

    # Calculate the percentage of times the most frequent remaining ship combination occurred
    army_1_mode_percentage = most_frequent_army_1[0][1] / results["Army 1 Wins"] * 100 if results["Army 1 Wins"] > 0 else 0
    army_2_mode_percentage = most_frequent_army_2[0][1] / results["Army 2 Wins"] * 100 if results["Army 2 Wins"] > 0 else 0
    army_1_full_survival_rate = full_survival["Army 1"] / results["Army 1 Wins"] * 100 if results["Army 1 Wins"] > 0 else 0
    army_2_full_survival_rate = full_survival["Army 2"] / results["Army 2 Wins"] * 100 if results["Army 2 Wins"] > 0 else 0

    # Return the results
    statistics = f"""
    Fight Simulation Results:
    --------------------------
    Army 1 Wins Probability: {prob_army_1_win}
    Army 2 Wins Probability: {prob_army_2_win}
    Draw Probability: {draw_rate}

    Army 1 Most Frequent Remaining Ships: {" ".join(most_frequent_army_1[0][0])} with {army_1_mode_percentage:.2f}% occurrence
    Army 1 Full Survival Rate: {army_1_full_survival_rate:.2f}%
    Army 2 Most Frequent Remaining Ships: {" ".join(most_frequent_army_2[0][0])} with {army_2_mode_percentage:.2f}% occurrence
    Army 2 Full Survival Rate: {army_2_full_survival_rate:.2f}%

    """
    
    return statistics


# Function to assign damage to ships based on hits (use sustain damage first, then weakest combat ship)
def assign_damage(army_ships: list[Ship], hits: int):
    # First, use sustain damage for ships that have it
    for ship in army_ships:
        if ship.sustain_damage and hits > 0:
            ship.sustain_damage = False  # damage as used
            hits -= 1  # Subtract 1 hit from the totaMark sustain l hits to assign
        if hits == 0:  # If no hits are left, stop
            return army_ships
    

    while hits > 0 and army_ships:  # As long as there are hits and ships left
        # Remove the ship with the highest combat value (last in sorted list)
        # Find ship with max combat (worst)
        worst_ship = max(army_ships, key=lambda x: x.combat)
        army_ships.remove(worst_ship)
        hits -= 1


    return army_ships # return ships which are left after assigning hits

def perform_pre_combat_effects(attacking_army: list[Ship], defending_army: list[Ship]) -> list[Ship]:
    # Collect combat thresholds and number of dice to roll
    thresholds = []
    dice_counts = []

    for ship in attacking_army:
        if ship.anti_fighter_barrage:
            thresholds.extend([ship.anti_fighter_combat] * ship.anti_fighter_hits)
            dice_counts.append(ship.anti_fighter_hits)

    if thresholds:
        rolls = np.random.randint(1, 11, size=len(thresholds))
        thresholds = np.array(thresholds)
        total_barrage_hits = int(np.sum(rolls >= thresholds))
    else:
        total_barrage_hits = 0

    # Apply hits to defending fighters
    new_defenders = []
    fighter_hits_left = total_barrage_hits
    for ship in defending_army:
        if fighter_hits_left > 0 and isinstance(ship, DefaultFighter):
            fighter_hits_left -= 1
            continue  # Remove fighter
        new_defenders.append(ship)

    return new_defenders

def perform_space_cannon_fire(army_with_cannon: list[Ship], target_army: list[Ship]) -> list[Ship]:
    hits = 0
    for ship in army_with_cannon:
        if isinstance(ship, SpaceCannon):
            
            if random.randint(1, 10) >= ship.combat:
                hits += 1
    return assign_damage(target_army, hits)

def prepare_army_for_combat(army: list[Ship]) -> list[Ship]:
    return [ship for ship in army if not isinstance(ship, SpaceCannon)]

def precombat_phase(army1: list[Ship], army2: list[Ship]):
    # Apply anti-fighter barrage
    army2 = perform_pre_combat_effects(army1, army2)
    army1 = perform_pre_combat_effects(army2, army1)

    # Apply space cannon fire
    army2 = perform_space_cannon_fire(army1, army2)
    army1 = perform_space_cannon_fire(army2, army1)

    # Remove space cannons from combat
    army1 = prepare_army_for_combat(army1)
    army2 = prepare_army_for_combat(army2)

    return army1, army2

# Example usage:
if __name__ == "__main__":
    # Example: Creating a simple army with ships
    army_1 = [DefaultCruiser(), DefaultCruiser()]
    army_2 = [DefaultCruiser()]

    # Simulate the fight between two armies
    result = simulate_fight([army_1, army_2], n_fights=10000)
    print(result)