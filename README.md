
# Energy Market Arbitrage

## Summary
The formulation below provides a structured optimization approach for determining a bidding and offering strategy in the electricity market while considering uncertainty in wind generation and market prices. The objective function accounts for expected revenue across 100 different price scenarios by using the several scenarios and assuming they are all equally likely.  


**Note:**
For the data analysis notebook an additionally library, Plotly, is needed to properly view. That package is included in the `pyproject.toml`


## Sets & Indices
- $T$  : Set of time periods (hours in a single day)
-  $S$  : Set of scenarios

## Parameters
-  ${DA\_price}_{s,t}$  : Day-ahead market price at time $t$, scenario $s$  ($/MWh)
-  $\texttt{RT\_price}_{s,t}$  : Real-time market price at time $t$, scenario $s$ ($/MWh)
-  $\text{wind\_gen}_{s,t}$  : Wind power generation at time $t$, scenario $s$ (MW)

## Decision Variables
- $\text{offer\_quantity}_{t}$ : Energy offered in the market at time $t$
- $\text{bid\_quantity}_{t}$ : Energy bid in the market at time $t$
- $\text{offer\_price}_{t}$ : Offer price at time $t$ ($/MWh)
- $\text{bid\_price}_{t}$ : Bid price at time $t$ ($/MWh)



## Objective
Maximize total expected revenue:
$$
\max \frac{1}{\text{num\_scenarios}} \sum_{s \in S} \sum_{t \in T} \Big( \text{offer\_quantity}_t \cdot (\text{DA\_price}_{s,t} - \text{RT\_price}_{s,t}) + \text{bid\_quantity}_t \cdot (\text{RT\_price}_{s,t} - \text{DA\_price}_{s,t}) + \text{wind\_generation}_{s,t} \cdot \text{RT\_price}_{s,t} \Big)
$$


## Constraints

1. **Offer Quantity Constraint:**
   $$
   \text{offer\_quantity}_{t} \leq \text{wind\_gen}_{s, t} \quad \forall t \in T, s \in S
   $$

2. **Bid Quantity Constraint:**
   $$
    \text{bid\_quantity}_{t} \leq \text{offer\_quantity}_{t}, \quad \forall t \in T
   $$

3. **Offer(Sell) Market Participation Constraint:**
   $$
   \text{offer\_price}_{t} \geq \text{DA\_price}_{s,t}, \quad \forall t \in T, s \in S
   $$

4. **Bid(Buy) Market Participation Constraint:**
   $$
   \text{bid\_price}_{t} \leq \text{DA\_price}_{s,t}, \quad \forall t \in T, s \in S
   $$


