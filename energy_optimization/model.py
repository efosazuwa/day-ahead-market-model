import os
from typing import List, Optional

import numpy as np
from numpy.typing import NDArray
import pandas as pd 
import plotly.graph_objects as go
import pyomo.environ as pyo


from sample_data_generator import generate_sample_data, load_sample_data

class EnergyArbitrageModel:
    """
    A class for scenario based stochastic optimization of energy arbitrage.
    """

    def __init__(self, scenario_data: NDArray, target_names: List[str]):
        self.scenario_data: NDArray = scenario_data
        self.target_names: List[str] = target_names

        self.num_time_periods: int = self.scenario_data.shape[1]
        self.num_scenarios: int = self.scenario_data.shape[0]

        self.DA_prices: NDArray = self.scenario_data[:, :, 0]
        self.RT_prices: NDArray = self.scenario_data[:, :, 1]
        self.wind_gen: NDArray = self.scenario_data[:, :, 2]

        self.model: Optional[pyo.ConcreteModel] = None

    def build_model(self):
        """
        Build stochastic arbitrage model.
        """

        model = pyo.ConcreteModel()

        # Sets
        model.T = pyo.Set(initialize=range(0, self.num_time_periods)) # Time periods
        model.S = pyo.Set(initialize=range(0, self.num_scenarios)) # Scenarios

        # Parameters
        model.DA_price = pyo.Param(model.S, model.T, initialize=lambda m, s, t: float(self.DA_prices[s, t]))
        model.RT_price = pyo.Param(model.S, model.T, initialize=lambda m, s, t: float(self.RT_prices[s, t]))
        model.wind_gen = pyo.Param(model.S, model.T, initialize=lambda m, s, t: float(self.wind_gen[s, t]))

        # Decision Variables
        model.offer_quantity = pyo.Var(model.T, domain=pyo.NonNegativeReals)
        model.offer_price = pyo.Var(model.T, domain=pyo.Reals)
        model.bid_quantity = pyo.Var(model.T, domain=pyo.NonNegativeReals)
        model.bid_price = pyo.Var(model.T, domain=pyo.Reals)

        # Objective: Maximize Revenue
        def objective(m):
            revenue = sum(
                m.offer_quantity[t]*(model.DA_price[s, t] - model.RT_price[s, t]) +
                m.bid_quantity[t]*(model.RT_price[s, t] - model.DA_price[s, t])  +
                m.wind_gen[s, t] * model.RT_price[s, t]
                for s in m.S for t in m.T
            )
            return revenue/self.num_scenarios
        
        model.obj = pyo.Objective(rule=objective, sense=pyo.maximize)

        
        # Constraints
        def offer_quantity_constraint(m, s, t):
            return m.offer_quantity[t] <= m.wind_gen[s, t]
        model.offer_quantity_constraint = pyo.Constraint(model.S, model.T, rule=offer_quantity_constraint)

        def bid_quantity_constraint(m, t):
            return m.bid_quantity[t] <= m.offer_quantity[t]
        model.bid_quantity_constraint = pyo.Constraint(model.T, rule=bid_quantity_constraint)

        def offer_market_clearing_constraint(m, s, t):
            return m.offer_price[t] >= model.DA_price[s, t]
        model.offer_clearing_constraint = pyo.Constraint(model.S, model.T, rule=offer_market_clearing_constraint)

        def bid_market_clearing_constraint(m, s, t):
            return m.bid_price[t] <= model.DA_price[s, t]
        model.bid_clearing_constraint = pyo.Constraint(model.S, model.T, rule=bid_market_clearing_constraint)

        

        self.model = model

    def solve(self, solver_name='glpk'):
        """
        Solve the energy arbitrage model
        """
        solver = pyo.SolverFactory(solver_name)
        result = solver.solve(self.model, tee=True)

        return result

    def get_results(self)-> dict[str, NDArray]:
        """
        Retrieve results from the solved model.
        """
        if self.model is None:
            raise Exception("Model has not been solved yet. Please call solve() method first.")
        
        results = {
            "offer_quantity": np.array([self.model.offer_quantity[t].value for t in self.model.T]),
            "offer_price": np.array([self.model.offer_price[t].value for t in self.model.T]),
            "bid_quantity": np.array([self.model.bid_quantity[t].value for t in self.model.T]),
            "bid_price": np.array([self.model.bid_price[t].value for t in self.model.T])
        }
        
        return results
    def plot_energy_trading(self, results):
        """
        Plots the energy bid (buy) and offer (sell) quantities over time.
        """
        q_offer = results['offer_quantity']
        q_bid = results['bid_quantity']

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=list(range(self.num_time_periods)),
                y=q_offer,
                name='Offer Quantity',
                marker_color='orange'
            )
        )
        fig.add_trace(
            go.Bar(
                x=list(range(self.num_time_periods)),
                y=q_bid,
                name='Bid Quantity',
                marker_color='blue'
            )
        )
        fig.update_layout(
            title='Energy Trading: Offer and Bid Quantities',
            xaxis_title='Time Periods',
            yaxis_title='Quantity',
            barmode='group'
        )   
        fig.show()


if __name__ == "__main__":
    fname = "energy_market_samples.npz"
    base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    # Check for sample data file
    if not os.path.exists(os.path.join(base_dir, fname)): 
        generate_sample_data()

    data, target_names= load_sample_data()
    optimizer = EnergyArbitrageModel(
        scenario_data=data,
        target_names=target_names
    )
    optimizer.build_model()
    optimizer.solve()
    results = optimizer.get_results()
    optimizer.plot_energy_trading(results)