"""
CryptoMAKA Lab - Vector Figures Generator for Review 3 & IEEE Paper
Generates publication-quality editable vector figures (SVG, PDF, PNG)
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Publication style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.titlesize'] = 13

OUTPUT_DIRS = [
    Path("Review_3_Submission/4_Supplementary_Files/02_Editable_Figure_Source_Files/figures_vector"),
    Path("Review_3_Submission/2_Research_Paper/Source/figures")
]

for d in OUTPUT_DIRS:
    d.mkdir(parents=True, exist_ok=True)

def save_fig(fig, name):
    for d in OUTPUT_DIRS:
        fig.savefig(d / f"{name}.svg", bbox_inches='tight', format='svg')
        fig.savefig(d / f"{name}.pdf", bbox_inches='tight', format='pdf')
        fig.savefig(d / f"{name}.png", bbox_inches='tight', dpi=300)
    plt.close(fig)
    print(f"[+] Saved {name} (SVG, PDF, PNG)")

# Figure 1: Computation Time vs Communication Overhead
def make_fig_comp_comm():
    fig, ax1 = plt.subplots(figsize=(7, 4))
    
    protocols = ['Ju-Park 2023\n(Reference)', 'ECC P-256\n(Baseline)', 'Proposed Ext.\n(Reduced-RTT)', 'ML-KEM-768\n(Post-Quantum)']
    comp_times = [0.82, 4.15, 0.61, 2.38] # ms
    comm_bytes = [384, 192, 288, 2240]    # bytes
    
    x = np.arange(len(protocols))
    width = 0.35
    
    color1 = '#1E3A8A' # Deep Blue
    color2 = '#059669' # Emerald Green
    
    rects1 = ax1.bar(x - width/2, comp_times, width, label='Computation Time (ms)', color=color1, edgecolor='black', linewidth=0.8)
    ax1.set_ylabel('Mean Execution Time (ms)', color=color1, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_ylim(0, 5.0)
    
    ax2 = ax1.twinx()
    rects2 = ax2.bar(x + width/2, comm_bytes, width, label='Communication Overhead (Bytes)', color=color2, edgecolor='black', linewidth=0.8)
    ax2.set_ylabel('Total Payload Size (Bytes)', color=color2, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.set_ylim(0, 2600)
    
    # Value annotations
    for rect in rects1:
        h = rect.get_height()
        ax1.annotate(f'{h:.2f} ms', xy=(rect.get_x() + rect.get_width()/2, h),
                     xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold')
        
    for rect in rects2:
        h = rect.get_height()
        ax2.annotate(f'{int(h)} B', xy=(rect.get_x() + rect.get_width()/2, h),
                     xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold')
        
    ax1.set_xticks(x)
    ax1.set_xticklabels(protocols, fontweight='bold')
    plt.title('Computation Latency vs. Communication Overhead Across Protocols', pad=15, fontweight='bold')
    fig.tight_layout()
    save_fig(fig, 'fig_comp_comm_tradeoff')

# Figure 2: Wireless Channel Transmission Latency (ms)
def make_fig_wireless_latency():
    fig, ax = plt.subplots(figsize=(8, 4.2))
    
    protocols = ['Ju-Park 2023', 'ECC P-256', 'Proposed Ext.', 'ML-KEM-768']
    # Latencies in milliseconds across wireless IoT physical layers
    lorawan = [307.2, 153.6, 230.4, 1792.0] # 10 kbps
    nbiot   = [61.4,  30.7,  46.1,  358.4]  # 50 kbps
    ltem    = [10.2,  5.1,   7.7,   59.7]   # 300 kbps
    five_g  = [0.6,   0.3,   0.5,   3.6]    # 5 Mbps
    
    x = np.arange(len(protocols))
    width = 0.2
    
    ax.bar(x - 1.5*width, lorawan, width, label='LoRaWAN EU868 (10 kbps)', color='#DC2626', edgecolor='black')
    ax.bar(x - 0.5*width, nbiot,   width, label='NB-IoT Band 20 (50 kbps)', color='#F59E0B', edgecolor='black')
    ax.bar(x + 0.5*width, ltem,    width, label='LTE-M Cat-M1 (300 kbps)',  color='#2563EB', edgecolor='black')
    ax.bar(x + 1.5*width, five_g,  width, label='5G URLLC IoT (5 Mbps)',    color='#10B981', edgecolor='black')
    
    ax.set_ylabel('Wireless Airtime Latency (ms) [Log Scale]', fontweight='bold')
    ax.set_yscale('log')
    ax.set_xticks(x)
    ax.set_xticklabels(protocols, fontweight='bold')
    ax.legend(frameon=True, facecolor='white', framealpha=0.9, loc='upper left')
    ax.set_title('IoT Wireless Transmission Airtime Latency by Radio Standard', pad=12, fontweight='bold')
    ax.grid(True, which="both", ls="--", alpha=0.5)
    fig.tight_layout()
    save_fig(fig, 'fig_wireless_latency')

# Figure 3: MCU Microjoule Energy Consumption (ARM Cortex-M4 @ 64MHz)
def make_fig_energy_consumption():
    fig, ax = plt.subplots(figsize=(7.5, 4))
    
    protocols = ['Ju-Park 2023', 'ECC P-256', 'Proposed Ext.', 'ML-KEM-768']
    
    # Energy in microjoules (uJ) = E_comp + E_tx
    e_comp = [24.6, 124.5, 18.3, 71.4]  # Computation on Cortex-M4
    e_tx   = [46.1,  23.0, 34.6, 268.8] # Wireless Tx energy on NB-IoT
    
    x = np.arange(len(protocols))
    width = 0.45
    
    p1 = ax.bar(x, e_comp, width, label='Cryptographic Computation Energy', color='#4F46E5', edgecolor='black')
    p2 = ax.bar(x, e_tx,   width, bottom=e_comp, label='NB-IoT Wireless Tx Energy', color='#F97316', edgecolor='black')
    
    ax.set_ylabel('Total Device Energy Consumption (uJ)', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(protocols, fontweight='bold')
    ax.legend(frameon=True, loc='upper left')
    ax.set_title('Energy Budget per Handshake on Constrained IoT MCU (uJ)', pad=12, fontweight='bold')
    
    # Label totals
    for i in range(len(protocols)):
        total = e_comp[i] + e_tx[i]
        ax.annotate(f'{total:.1f} uJ', xy=(x[i], total), xytext=(0, 4),
                    textcoords="offset points", ha='center', va='bottom', fontweight='bold', fontsize=9)
        
    fig.tight_layout()
    save_fig(fig, 'fig_mcu_energy_consumption')

# Figure 4: Formal Verification & Threat Defense Scorecard
def make_fig_security_matrix():
    fig, ax = plt.subplots(figsize=(8, 4))
    
    attacks = ['Replay Resistance', 'Message Tampering', 'User Impersonation', 'Server Impersonation', 'MitM Attack', 'KCI Secrecy', 'Post-Quantum Res.']
    
    # Scores: 1.0 = Guaranteed Secure, 0.5 = Partial / Non-quantum, 0.0 = Vulnerable
    ju_park  = [1, 1, 1, 1, 1, 1, 0]
    ecc      = [1, 1, 1, 1, 1, 1, 0]
    proposed = [1, 1, 1, 1, 1, 1, 0]
    ml_kem   = [1, 1, 1, 1, 1, 1, 1]
    
    matrix = np.array([ju_park, ecc, proposed, ml_kem])
    
    cax = ax.imshow(matrix, cmap='Blues', aspect='auto', vmin=0, vmax=1)
    
    ax.set_xticks(np.arange(len(attacks)))
    ax.set_yticks(np.arange(4))
    ax.set_xticklabels(attacks, rotation=30, ha='right', fontweight='bold')
    ax.set_yticklabels(['Ju-Park 2023', 'ECC P-256', 'Proposed Ext.', 'ML-KEM-768'], fontweight='bold')
    
    # Text labels in cells
    for i in range(4):
        for j in range(len(attacks)):
            val = matrix[i, j]
            text = "PROVEN" if val == 1 else "VULNERABLE (Shor)"
            color = "white" if val == 1 else "black"
            ax.text(j, i, text, ha="center", va="center", color=color, fontweight='bold', fontsize=8)
            
    ax.set_title('Formal Security Proofs & Threat Model Defense Matrix', pad=15, fontweight='bold')
    fig.tight_layout()
    save_fig(fig, 'fig_security_formal_matrix')

if __name__ == '__main__':
    print("Generating Academic Vector Figures...")
    make_fig_comp_comm()
    make_fig_wireless_latency()
    make_fig_energy_consumption()
    make_fig_security_matrix()
    print("[+] All Figures generated successfully.")
