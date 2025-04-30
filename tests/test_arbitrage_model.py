import pytest 

import numpy as np

from energy_optimization_challenge.model import EnergyArbitrageModel
from sample_data_generator import load_sample_data


def test_get_results_with_empty_model():
    data, target_names = load_sample_data()
    optimizer = EnergyArbitrageModel(scenario_data=data, target_names=target_names)
    
    # Expecting an exception when trying to get results without solving the model
    with pytest.raises(Exception) as excinfo:
        optimizer.get_results()
    
    assert str(excinfo.value) == "Model has not been solved yet. Please call solve() method first."

def test_valid_keys_when_retrieving_results():
     valid_keys = ['offer_quantity', 'offer_price', 'bid_quantity', 'bid_price']
     data, target_names = load_sample_data()
     optimizer = EnergyArbitrageModel(scenario_data=data, target_names=target_names)
     optimizer.build_model()
     optimizer.solve()
     results = optimizer.get_results()
     assert all(key in results for key in valid_keys)

