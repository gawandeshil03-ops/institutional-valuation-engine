import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
from typing import Dict, List

def plot_football_field(
    valuation_ranges: Dict[str, List[float]], 
    current_share_price: float,
    ticker: str,
    filename: str = "valuation_football_field.png"
):
  
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Extract data
    labels = list(valuation_ranges.keys())
    lows = [v[0] for v in valuation_ranges.values()]
    highs = [v[1] for v in valuation_ranges.values()]
    diffs = np.array(highs) - np.array(lows)
    
    # Plot bars (Floating bars are created by drawing a bar with 'left' offset)
    y_pos = np.arange(len(labels))
    ax.barh(y_pos, diffs, left=lows, height=0.5, color='#2E5A88', alpha=0.9, edgecolor='black')
    
    # Add Current Price Line
    ax.axvline(current_share_price, color='#D9534F', linestyle='--', linewidth=2)
    
    # Label the current price at the top
    ax.text(current_share_price, len(labels) - 0.5, f' Current: ${current_share_price:.2f}', 
            color='#D9534F', ha='center', va='bottom', fontweight='bold')

    # Formatting
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=11, fontweight='bold')
    
    # Format X-axis as currency
    fmt = '${x:,.0f}'
    tick = mtick.StrMethodFormatter(fmt)
    ax.xaxis.set_major_formatter(tick)
    
    ax.set_title(f"Valuation Summary: {ticker}", fontsize=16, fontweight='bold', pad=20)
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    
    # Add data labels on bars
    for i, (low, high) in enumerate(zip(lows, highs)):
        # Low label
        ax.text(low - (high-low)*0.02, i, f"${low:.2f}", va='center', ha='right', fontsize=10)
        # High label
        ax.text(high + (high-low)*0.02, i, f"${high:.2f}", va='center', ha='left', fontsize=10)

    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    print(f"✅ Football field chart saved to {filename}")