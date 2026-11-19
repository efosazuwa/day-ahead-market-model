import pyomo.environ as pyo
import pytest

from energy_optimization.model import EnergyArbitrageModel, load_sample_data


def test_get_results_with_empty_model():
    data, target_names = load_sample_data()
    optimizer = EnergyArbitrageModel(scenario_data=data, target_names=target_names)

    with pytest.raises(Exception, match="Model has not been solved yet"):
        optimizer.get_results()


def test_valid_keys_when_retrieving_results():
    data, target_names = load_sample_data()
    optimizer = EnergyArbitrageModel(scenario_data=data, target_names=target_names)
    optimizer.build_model()

    pyo.assert_optimal_termination(optimizer.solve(tee=False))

    expected_keys = {"offer_quantity", "offer_price", "bid_quantity", "bid_price"}
    assert set(optimizer.get_results()) == expected_keys
