"""
Generate architecture and flow diagrams for the presentation
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

def create_architecture_diagram():
    """Create system architecture diagram"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Title
    ax.text(7, 9.5, 'Provider Directory Validation System - Architecture',
            ha='center', fontsize=16, fontweight='bold')

    # Color scheme
    colors = {
        'agent': '#667eea',
        'data': '#48bb78',
        'api': '#ed8936',
        'ui': '#4299e1'
    }

    # Data Layer (Bottom)
    data_y = 1.5
    boxes_data = [
        ('Provider\nData\n(JSON)', 1.5, colors['data']),
        ('NPI Registry\nAPI', 4.5, colors['api']),
        ('State License\nBoards', 7.5, colors['api']),
        ('Web Sources\n(Scraping)', 10.5, colors['api'])
    ]

    for label, x, color in boxes_data:
        box = FancyBboxPatch((x-0.7, data_y-0.4), 1.4, 0.8,
                            boxstyle="round,pad=0.05",
                            facecolor=color, edgecolor='black', linewidth=2, alpha=0.7)
        ax.add_patch(box)
        ax.text(x, data_y, label, ha='center', va='center', fontsize=9,
                fontweight='bold', color='white')

    # Agent Layer (Middle)
    agent_y = 4.5
    agents = [
        ('Data Validation\nAgent', 2, colors['agent']),
        ('Information\nEnrichment\nAgent', 5, colors['agent']),
        ('Quality\nAssurance\nAgent', 8, colors['agent']),
        ('Directory\nManagement\nAgent', 11, colors['agent'])
    ]

    for label, x, color in agents:
        box = FancyBboxPatch((x-0.9, agent_y-0.6), 1.8, 1.2,
                            boxstyle="round,pad=0.1",
                            facecolor=color, edgecolor='black', linewidth=2, alpha=0.8)
        ax.add_patch(box)
        ax.text(x, agent_y, label, ha='center', va='center', fontsize=10,
                fontweight='bold', color='white')

    # Orchestrator (Center)
    orch_y = 6.5
    box = FancyBboxPatch((5-1.5, orch_y-0.5), 4, 1,
                        boxstyle="round,pad=0.1",
                        facecolor='#2d3748', edgecolor='black', linewidth=3, alpha=0.9)
    ax.add_patch(box)
    ax.text(7, orch_y, 'Orchestrator\n(Multi-Agent Coordination)', ha='center', va='center',
            fontsize=12, fontweight='bold', color='white')

    # UI Layer (Top)
    ui_y = 8.5
    box = FancyBboxPatch((3-1, ui_y-0.4), 8, 0.8,
                        boxstyle="round,pad=0.1",
                        facecolor=colors['ui'], edgecolor='black', linewidth=2, alpha=0.8)
    ax.add_patch(box)
    ax.text(7, ui_y, 'Flask Web Dashboard (UI/API)', ha='center', va='center',
            fontsize=12, fontweight='bold', color='white')

    # Draw arrows (skipping for simplicity to avoid matplotlib issues)
    # Data to Agents connections shown conceptually

    # Add connection lines using plot instead of FancyArrowPatch
    # Orchestrator to UI
    ax.plot([7, 7], [orch_y + 0.6, ui_y - 0.5], 'k-', linewidth=3, alpha=0.8)
    ax.plot([7], [ui_y - 0.5], 'kv', markersize=15, alpha=0.8)

    # Agent connections to orchestrator
    for agent_x, _, _ in agents:
        ax.plot([agent_x, 7], [agent_y + 0.7, orch_y - 0.6], 'k-', linewidth=2, alpha=0.6)
        ax.plot([7], [orch_y - 0.6], 'kv', markersize=10, alpha=0.6)

    # Add legend
    legend_elements = [
        mpatches.Patch(facecolor=colors['agent'], label='AI Agents'),
        mpatches.Patch(facecolor=colors['data'], label='Data Sources'),
        mpatches.Patch(facecolor=colors['api'], label='External APIs'),
        mpatches.Patch(facecolor=colors['ui'], label='User Interface')
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=10)

    plt.tight_layout()
    plt.savefig('docs/architecture_diagram.png', dpi=300, bbox_inches='tight',
                facecolor='white')
    print("Architecture diagram saved: docs/architecture_diagram.png")

def create_flow_chart():
    """Create validation workflow flowchart"""
    fig, ax = plt.subplots(figsize=(12, 14))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 16)
    ax.axis('off')

    # Title
    ax.text(5, 15.5, 'Provider Validation Workflow',
            ha='center', fontsize=16, fontweight='bold')

    steps = [
        (5, 14, 'Start:\nLoad Provider Data', '#4299e1'),
        (5, 12.5, 'Data Validation Agent:\n- Validate Phone\n- Validate Address\n- Validate NPI\n- Validate License', '#667eea'),
        (5, 10.5, 'Information Enrichment Agent:\n- Search Provider Website\n- Check Online Profiles\n- Verify Hospital Affiliations\n- Analyze Network Coverage', '#667eea'),
        (5, 8.5, 'Quality Assurance Agent:\n- Compare Data Sources\n- Flag Suspicious Data\n- Calculate Quality Score\n- Prioritize for Review', '#667eea'),
        (5, 6.5, 'Directory Management Agent:\n- Generate Provider Report\n- Create Summary Reports\n- Build Review Queue\n- Generate Communications', '#667eea'),
        (2.5, 4.5, 'Quality Score\n>= 70?', '#ed8936'),
        (7.5, 4.5, 'Auto-Update\nDirectory', '#48bb78'),
        (2.5, 2.5, 'Manual Review\nQueue', '#f56565'),
        (5, 1, 'Update Dashboard\n& Generate Reports', '#4299e1'),
    ]

    for x, y, text, color in steps:
        if 'Quality Score' in text:
            # Diamond for decision
            diamond = mpatches.FancyBboxPatch((x-0.8, y-0.5), 1.6, 1,
                                             boxstyle="round,pad=0.1",
                                             facecolor=color, edgecolor='black',
                                             linewidth=2, alpha=0.8)
            ax.add_patch(diamond)
        else:
            # Rectangle for process
            rect = FancyBboxPatch((x-1.2, y-0.6), 2.4, 1.2,
                                 boxstyle="round,pad=0.1",
                                 facecolor=color, edgecolor='black',
                                 linewidth=2, alpha=0.8)
            ax.add_patch(rect)

        ax.text(x, y, text, ha='center', va='center',
                fontsize=9, fontweight='bold', color='white')

    # Draw connection lines between steps using plot
    connections = [
        ([5, 5], [13.4, 13.1]),  # Start to validation
        ([5, 5], [11.9, 11.1]),  # Validation to enrichment
        ([5, 5], [9.9, 9.1]),    # Enrichment to QA
        ([5, 5], [7.9, 7.1]),    # QA to directory
        ([5, 3.7], [5.9, 5.1]),  # Directory to decision (left)
        ([5, 6.3], [5.9, 5.1]),  # Directory to decision (right)
        ([7.5, 7.5], [3.9, 2]),  # Auto-update to dashboard
        ([7.5, 5.5], [2, 1.6]),  # Curve to dashboard
        ([2.5, 2.5], [3.9, 3.1]),  # Manual review down
        ([2.5, 4.5], [3.1, 1.6]),  # Manual review to dashboard
    ]

    for x_coords, y_coords in connections:
        ax.plot(x_coords, y_coords, 'k-', linewidth=2.5, alpha=0.7)
        ax.plot(x_coords[-1], y_coords[-1], 'kv', markersize=10, alpha=0.7)

    # Add labels on decision paths
    ax.text(6.5, 4.8, 'Yes', fontsize=10, fontweight='bold', color='#48bb78')
    ax.text(3.5, 4.8, 'No', fontsize=10, fontweight='bold', color='#f56565')

    # Add timing annotations
    ax.text(9, 12.5, '~1-2s', fontsize=8, style='italic', color='gray')
    ax.text(9, 10.5, '~2-3s', fontsize=8, style='italic', color='gray')
    ax.text(9, 8.5, '~0.5s', fontsize=8, style='italic', color='gray')
    ax.text(9, 6.5, '~0.5s', fontsize=8, style='italic', color='gray')

    plt.tight_layout()
    plt.savefig('docs/flow_chart.png', dpi=300, bbox_inches='tight',
                facecolor='white')
    print("Flow chart saved: docs/flow_chart.png")

def create_metrics_dashboard():
    """Create sample metrics visualization"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Provider Validation Metrics Dashboard', fontsize=16, fontweight='bold')

    # Status Distribution (Pie Chart)
    statuses = ['Excellent', 'Good', 'Fair', 'Poor', 'Critical']
    values = [45, 78, 52, 18, 7]
    colors_pie = ['#48bb78', '#4299e1', '#ed8936', '#f56565', '#742a2a']

    ax1.pie(values, labels=statuses, autopct='%1.1f%%', colors=colors_pie, startangle=90)
    ax1.set_title('Status Distribution (200 Providers)', fontweight='bold')

    # Quality Score Distribution (Histogram)
    scores = np.random.normal(75, 15, 200)
    scores = np.clip(scores, 0, 100)

    ax2.hist(scores, bins=20, color='#667eea', edgecolor='black', alpha=0.7)
    ax2.set_xlabel('Quality Score', fontweight='bold')
    ax2.set_ylabel('Number of Providers', fontweight='bold')
    ax2.set_title('Quality Score Distribution', fontweight='bold')
    ax2.axvline(70, color='red', linestyle='--', linewidth=2, label='Review Threshold')
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)

    # Top Issues (Bar Chart)
    issues = ['Placeholder\nPhone', 'Outdated\nAddress', 'Unknown\nLicense',
              'Stale Data', 'NPI\nMismatch']
    issue_counts = [78, 52, 38, 95, 12]

    bars = ax3.barh(issues, issue_counts, color='#ed8936', edgecolor='black')
    ax3.set_xlabel('Number of Providers', fontweight='bold')
    ax3.set_title('Top Issues Found', fontweight='bold')
    ax3.grid(axis='x', alpha=0.3)

    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax3.text(width + 2, bar.get_y() + bar.get_height()/2,
                str(issue_counts[i]), ha='left', va='center', fontweight='bold')

    # Processing Performance (Line Chart)
    time_points = [0, 0.5, 1, 1.5, 2, 2.5, 3]
    providers_processed = [0, 35, 70, 105, 140, 175, 200]

    ax4.plot(time_points, providers_processed, marker='o', linewidth=3,
            markersize=8, color='#667eea')
    ax4.fill_between(time_points, providers_processed, alpha=0.3, color='#667eea')
    ax4.set_xlabel('Time (minutes)', fontweight='bold')
    ax4.set_ylabel('Providers Processed', fontweight='bold')
    ax4.set_title('Processing Performance (66 providers/min)', fontweight='bold')
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('docs/metrics_dashboard.png', dpi=300, bbox_inches='tight',
                facecolor='white')
    print("Metrics dashboard saved: docs/metrics_dashboard.png")

if __name__ == "__main__":
    import os
    os.makedirs('docs', exist_ok=True)

    print("Generating diagrams for presentation...")
    create_architecture_diagram()
    create_flow_chart()
    create_metrics_dashboard()
    print("\nAll diagrams generated successfully in docs/ folder!")
