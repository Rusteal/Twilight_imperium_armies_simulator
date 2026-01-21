# Monte Carlo Fleet Combat Simulator for Twilight Imperium 4

## Overview

This project implements a **Monte Carlo simulation framework** for analyzing fleet combat outcomes in *Twilight Imperium 4 (TI4)*.  
It is designed primarily as a **statistical and computational tool**, while remaining fully usable for TI4 players.

The simulator repeatedly samples combat outcomes under TI4 combat rules and produces **empirical distributions, win probabilities, and survivor statistics** that are difficult or impractical to compute analytically.

The core motivation is statistical: fleet combat in TI4 involves **heterogeneous binomial processes with multiple interacting mechanics**, making closed-form probability calculations infeasible for realistic scenarios. Monte Carlo simulation provides a natural and scalable alternative.

---

## Key Features

### Statistical & Computational
- Monte Carlo simulation with **10,000+ independent combat trials**
- Empirical estimation of:
  - win probabilities
  - outcome distributions
  - quantiles (1%, 10%, 25%, median, 75%, 90%, 99%)
  - survivor composition modes
- Support for **heterogeneous hit probabilities and dice counts**
- Validation against:
  - analytical binomial moments (mean, variance)
  - normal and truncated-normal approximations (for comparison only)

### Game Mechanics Coverage
- Full TI4 combat flow, including:
  - anti-fighter barrage
  - space cannon fire
  - sustain damage
  - ship removal order
- Custom ship creation with arbitrary parameters
- Upgraded and non-upgradeable units handled explicitly

### User Interface
- GUI-based workflow (no coding required)
- Per-ship copy and delete controls
- Clipboard-style replication for rapid fleet construction
- Army-level analysis and head-to-head battle simulation

---

## What Twilight Imperium 4 Combat Looks Like (Briefly)

In TI4, each ship rolls one or more dice during combat rounds.  
A hit occurs if a die roll exceeds a ship-specific **combat threshold**.

From a statistical perspective:
- each die roll is a **Bernoulli trial**
- different ships have **different probabilities of success**
- fleets consist of **non-identical collections of Bernoulli processes**
- additional mechanics (sustain damage, pre-combat effects) introduce state dependence

As a result, the total number of hits is **not binomial** in general, but a sum of non-identical Bernoulli trials with complex conditional logic.

---

## Why Monte Carlo?

For simple fleets, analytical results are possible.  
For realistic fleets with:
- mixed unit types,
- different hit probabilities,
- multiple dice per unit,
- pre-combat effects,
- sustain damage logic,

the exact outcome distribution becomes a **Poisson-binomial-like process with path dependence**.

Rather than forcing fragile approximations, this project uses:

**Monte Carlo simulation** — repeated random sampling of the combat process — to estimate outcome distributions directly.

This approach:
- scales naturally with fleet size,
- accommodates arbitrary rule extensions,
- produces full empirical distributions rather than just point estimates.

---

## What the Simulator Produces

### Army Analysis Mode
- Expected hits (mean)
- Variance and standard deviation
- Empirical quantiles of total hits
- Army health, movement constraints, capacity, and cost
- Comparison to normal and truncated-normal approximations

### Battle Simulation Mode
- Win probabilities for each army
- Draw frequency
- Most likely survivor compositions (modes)
- Full-survival rates conditional on winning

All statistics are derived from simulation outcomes, not assumed distributions.

---

## Installation (Recommended: Executable)

If you only want to **use the simulator**, no Python installation is required.

Download the Windows executable here:

[Download Windows executable](https://github.com/Rusteal/Twilight_imperium_armies_simulator/raw/main/TI_calculator_installer.exe)


Steps:
1. Download the executable
2. Run it (no setup required)
3. Build fleets and simulate outcomes via the GUI

---

## Running from Source (Optional)

If you want to inspect or modify the code:

```bash
pip install numpy scipy PyQt6
python ui.py
