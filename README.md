# Day-Ahead Bidding for Wind Power

How much wind generation should you schedule day-ahead when both prices and production are uncertain? This Pyomo model chooses one schedule for a 24-hour day and maximizes expected revenue across 100 equally weighted synthetic scenarios.

## Worked example

The model averages **$46,781** per scenario day, compared with **$39,899** for selling all wind generation at real-time prices. That is a **17.25% increase in modeled revenue** across the scenarios used to solve the schedule.

![Hourly net day-ahead offers and minimum scenario wind above, with mean day-ahead minus real-time prices below](docs/images/bidding-schedule.png)

The teal bars show the net day-ahead offer, equal to the offer minus the buyback quantity. The model schedules a net offer when the average day-ahead price exceeds the average real-time price and every scenario has wind available. The lowest wind forecast caps the offer for that hour.

## Run the example

From the repository root, use Python 3.11, [uv](https://docs.astral.sh/uv/), and [GLPK](https://pyomo.readthedocs.io/en/stable/getting_started/solvers.html). Install GLPK with `brew install glpk` on macOS or `sudo apt install glpk-utils` on Debian and Ubuntu. Confirm that `glpsol` is on your `PATH`.

```sh
uv run --locked --python 3.11 -m energy_optimization.example
```

The command reads the [tracked scenario data](data/energy_market_samples.npz), prints both revenue figures, and regenerates the chart. Pass `--output path/to/chart.png` to save it elsewhere. The [analysis notebook](data_analysis.ipynb) shows the individual wind and price scenarios.

```sh
uv run --locked --extra dev --python 3.11 -m pytest -q
```

## Model formulation

For each hour $t$, the model chooses nonnegative offer and buyback quantities $q^{offer}_t$ and $q^{bid}_t$, along with offer and bid prices. Each scenario $s$ supplies wind generation $W_{s,t}$, a day-ahead price $P^{DA}_{s,t}$, and a real-time price $P^{RT}_{s,t}$. Each interval is one hour, so the numeric MW quantity corresponds to the same number of MWh in settlement.

```math
\max \frac{1}{|S|} \sum_{s\in S}\sum_{t\in T}
\left[
W_{s,t}P^{RT}_{s,t}
+ \left(q^{offer}_t-q^{bid}_t\right)\left(P^{DA}_{s,t}-P^{RT}_{s,t}\right)
\right]
```

The offer is capped by wind generation in every scenario. The buyback is capped by the offer. The original price constraints place the offer price at or above every scenario's day-ahead price and the bid price at or below it.

The revenue expression applies the scheduled quantities in every scenario. It has no scenario-specific cleared volumes, and the bid and offer prices enter only the constraints. The reported increase is an in-sample comparison of expected revenue.
