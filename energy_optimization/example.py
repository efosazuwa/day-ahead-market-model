"""Run the stored wind-market example and plot its net day-ahead schedule."""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pyomo.environ as pyo

from energy_optimization.model import EnergyArbitrageModel, load_sample_data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("docs/images/bidding-schedule.png"))
    args = parser.parse_args()

    data, target_names = load_sample_data()
    optimizer = EnergyArbitrageModel(data, target_names)
    optimizer.build_model()
    pyo.assert_optimal_termination(optimizer.solve(tee=False))
    schedule = optimizer.get_results()

    baseline = np.mean(np.sum(optimizer.wind_gen * optimizer.RT_prices, axis=1))
    optimized = pyo.value(optimizer.model.obj)
    print(f"Real-time only:    ${baseline:,.2f}")
    print(f"Optimized:         ${optimized:,.2f}")
    print(f"Modeled increase:  ${optimized - baseline:,.2f} ({(optimized / baseline - 1):.2%})")

    hours = np.arange(optimizer.num_time_periods)
    net_offers = schedule["offer_quantity"] - schedule["bid_quantity"]
    min_wind = optimizer.wind_gen.min(axis=0)
    mean_spread = (optimizer.DA_prices - optimizer.RT_prices).mean(axis=0)

    fig, (quantity_ax, spread_ax) = plt.subplots(
        2, 1, sharex=True, figsize=(9, 5.6), layout="constrained"
    )
    fig.suptitle("Day-ahead wind schedule across the synthetic scenarios", fontweight="bold")
    quantity_ax.bar(hours, net_offers, color="#196E8A", label="Net day-ahead offer")
    quantity_ax.step(hours, min_wind, where="mid", color="#4F5865", label="Minimum scenario wind")
    quantity_ax.set_ylabel("Quantity (MW)")
    quantity_ax.legend(loc="upper right", frameon=False)

    spread_ax.bar(hours, mean_spread, color=np.where(mean_spread >= 0, "#196E8A", "#B85038"))
    spread_ax.axhline(0, color="#4F5865", linewidth=0.8)
    spread_ax.set_ylabel("Mean DA − RT\nprice ($/MWh)")
    spread_ax.set_xlabel("Hour of day")
    spread_ax.set_xticks(hours[::2])

    for ax in (quantity_ax, spread_ax):
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color="#E2E6EA")
        ax.set_axisbelow(True)
        ax.set_xlim(-0.6, hours[-1] + 0.6)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=160, facecolor="white")
    plt.close(fig)
    print(f"Chart: {args.output}")


if __name__ == "__main__":
    main()
