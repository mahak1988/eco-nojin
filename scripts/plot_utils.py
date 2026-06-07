"""Publication-ready plotting utilities for Economugin research"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Set publication style
sns.set_style("whitegrid")
plt.rcParams.update(
    {
        "font.size": 10,
        "axes.labelsize": 11,
        "axes.titlesize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 9,
        "figure.figsize": (8, 6),
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
    }
)


def plot_scenario_comparison(data: dict, output_path: str):
    """Plot scenario comparison bar chart"""
    df = pd.DataFrame(data).T.reset_index().rename(columns={"index": "Scenario"})
    fig, ax = plt.subplots(figsize=(8, 5))
    df.plot(
        x="Scenario",
        y=["yield_change_pct", "soc_change_t_ha_10yr"],
        kind="bar",
        ax=ax,
        colormap="Set2",
    )
    ax.set_ylabel("Change vs Baseline")
    ax.set_title("Scenario Impact on Yield and Soil Carbon")
    ax.legend(["Yield Change (%)", "SOC Change (t C/ha)"])
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    return output_path


def plot_uncertainty_bands(
    samples: list, output_path: str, xlabel: str = "Simulation", ylabel: str = "Value"
):
    """Plot uncertainty distribution with confidence bands"""
    sorted_samples = sorted(samples)
    n = len(sorted_samples)
    x = np.arange(n)
    ci_lower = sorted_samples[int(n * 0.025)]
    ci_upper = sorted_samples[int(n * 0.975)]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(x, sorted_samples, alpha=0.3, label="Samples")
    ax.axhline(ci_lower, color="red", linestyle="--", label="95% CI lower")
    ax.axhline(ci_upper, color="red", linestyle="--", label="95% CI upper")
    ax.axhline(np.mean(samples), color="blue", linestyle="-", label="Mean")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title("Uncertainty Distribution")
    ax.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    return output_path


def plot_yield_soc_scatter(data: list, output_path: str):
    """Scatter plot of yield vs SOC change"""
    df = pd.DataFrame(data)
    fig, ax = plt.subplots(figsize=(6, 6))
    sns.scatterplot(
        data=df,
        x="yield_kg_ha",
        y="soc_change_t_ha",
        hue="management_code",
        palette="viridis",
        ax=ax,
    )
    ax.set_xlabel("Yield (kg/ha)")
    ax.set_ylabel("SOC Change (t C/ha)")
    ax.set_title("Yield vs Soil Carbon Trade-offs")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    return output_path
