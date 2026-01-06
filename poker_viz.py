"""Visualization and reporting functions for poker analytics."""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict


class RangeVisualizer:
    """Create visualizations for hand range analysis."""

    @staticmethod
    def plot_hand_range_heatmap(
        player_name: str,
        player_range_data: Dict[str, int],
        hand_matrix,
        ranks
    ):
        """
        Create colorful heatmap of player's showdown range.

        Args:
            player_name: Name of the player
            player_range_data: Dictionary mapping hand notations to frequencies
            hand_matrix: 13x13 matrix of hand notations
            ranks: List of rank symbols
        """
        # Create frequency matrix
        freq_matrix = np.zeros((13, 13))

        for i, rank1 in enumerate(ranks):
            for j, rank2 in enumerate(ranks):
                hand = hand_matrix[i][j]
                freq_matrix[i][j] = player_range_data.get(hand, 0)

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 10))

        # Create heatmap with custom colormap
        im = ax.imshow(freq_matrix, cmap='YlOrRd', aspect='auto')

        # Set ticks and labels
        ax.set_xticks(np.arange(13))
        ax.set_yticks(np.arange(13))
        ax.set_xticklabels(ranks, fontsize=11, fontweight='bold')
        ax.set_yticklabels(ranks, fontsize=11, fontweight='bold')

        # Add grid
        ax.set_xticks(np.arange(13) - 0.5, minor=True)
        ax.set_yticks(np.arange(13) - 0.5, minor=True)
        ax.grid(which='minor', color='black', linestyle='-', linewidth=1.5)

        # Add hand labels and frequencies
        for i in range(13):
            for j in range(13):
                hand = hand_matrix[i][j]
                freq = freq_matrix[i][j]

                # Determine text color based on background
                text_color = 'white' if freq > freq_matrix.max() * 0.5 else 'black'

                # Add hand notation
                ax.text(j, i - 0.15, hand, ha='center', va='center',
                       fontsize=9, fontweight='bold', color=text_color)

                # Add frequency if > 0
                if freq > 0:
                    ax.text(j, i + 0.2, f'({int(freq)})', ha='center', va='center',
                           fontsize=7, color=text_color, style='italic')

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('Frequency at Showdown', fontsize=12, fontweight='bold')

        # Title and labels
        total_showdowns = sum(player_range_data.values())
        ax.set_title(
            f'Showdown Hand Range for {player_name}\n({total_showdowns} total showdowns)',
            fontsize=14, fontweight='bold', pad=20
        )

        # Add annotations
        ax.text(12.5, -1.5, 'Suited Hands →', fontsize=10, ha='right',
               style='italic', color='darkgreen')
        ax.text(-1.5, 12.5, '← Offsuit Hands', fontsize=10, ha='left',
               style='italic', color='darkblue')
        ax.text(6, -1.5, 'Pocket Pairs (diagonal)', fontsize=10, ha='center',
               style='italic', color='darkred')

        plt.tight_layout()
        plt.show()

        return freq_matrix


class StatisticsReporter:
    """Generate formatted reports for poker statistics."""

    @staticmethod
    def print_player_summary(player_stats: pd.DataFrame):
        """
        Print comprehensive player performance summary.

        Args:
            player_stats: DataFrame with player statistics
        """
        print("=" * 80)
        print("PLAYER PERFORMANCE SUMMARY")
        print("=" * 80)
        print(f"\n{'Player':<10} {'Net Profit':>12} {'Sessions':>8} {'Wins':>6} "
              f"{'Losses':>6} {'Win%':>7} {'Biggest Win':>12} {'Biggest Loss':>13}")
        print("-" * 80)

        for player, row in player_stats.iterrows():
            print(f"{player:<10} {row['net_profit']:>12,.0f} {int(row['total_sessions']):>8} "
                  f"{int(row['winning_sessions']):>6} {int(row['losing_sessions']):>6} "
                  f"{row['session_win_rate']:>6.1f}% {row['biggest_win']:>12,.0f} "
                  f"{row['biggest_loss']:>13,.0f}")

        best_session_player = player_stats.loc[player_stats['biggest_win'].idxmax()]
        worst_session_player = player_stats.loc[player_stats['biggest_loss'].idxmin()]

        print(f"\n🏆 Biggest Single Win: {player_stats['biggest_win'].idxmax()} "
              f"with ${best_session_player['biggest_win']:,.0f}")
        print(f"💥 Biggest Single Loss: {player_stats['biggest_loss'].idxmin()} "
              f"with ${worst_session_player['biggest_loss']:,.0f}")
        print("=" * 80)

    @staticmethod
    def print_positional_analysis(positional_stats: Dict, player_name: str):
        """
        Print positional analysis for a player.

        Args:
            positional_stats: Dictionary of positional stats
            player_name: Name of player to analyze
        """
        print("\n🎯 POSITIONAL ANALYSIS")
        print("=" * 80)
        print(f"\nPositional Stats for {player_name}:")
        print("-" * 80)

        if player_name in positional_stats:
            pos_data = []
            for position, stats in positional_stats[player_name].items():
                if stats['hands'] > 0:
                    win_rate = (stats['won'] / stats['hands'] * 100)
                    net_profit = stats['won_chips'] - stats['invested']

                    pos_data.append({
                        'Position': position,
                        'Hands': stats['hands'],
                        'Win Rate %': round(win_rate, 1),
                        'Invested': stats['invested'],
                        'Won': stats['won_chips'],
                        'Net': net_profit
                    })

            pos_df = pd.DataFrame(pos_data).sort_values('Hands', ascending=False)
            print(pos_df.to_string(index=False))

            print(f"\n💡 POSITIONAL INSIGHTS for {player_name}:")
            best_position = pos_df.loc[pos_df['Net'].idxmax()]
            worst_position = pos_df.loc[pos_df['Net'].idxmin()]
            print(f"   • Most Profitable Position: {best_position['Position']} "
                  f"(Net: ${best_position['Net']:,.0f})")
            print(f"   • Least Profitable Position: {worst_position['Position']} "
                  f"(Net: ${worst_position['Net']:,.0f})")

    @staticmethod
    def print_allin_analysis(allin_df: pd.DataFrame, total_situations: int, player_name=None):
        """
        Print all-in EV analysis results.

        Args:
            allin_df: DataFrame with all-in statistics
            total_situations: Total number of all-in situations
            player_name: Optional player name to filter results
        """
        print("\n♠️ ALL-IN EV ANALYSIS (Exact Multi-Way Equity)")
        print("=" * 80)
        print(f"Total All-In Situations (2+ players with showdown): {total_situations}")

        # Filter by player if specified
        if player_name and player_name in allin_df.index:
            allin_df = allin_df.loc[[player_name]]
            print(f"Showing results for: {player_name}")
        elif player_name:
            print(f"\n⚠️  Player '{player_name}' not found in all-in data")
            print("Showing all players instead\n")

        print("\n" + "=" * 80)
        print("ALL-IN PERFORMANCE: EV vs ACTUAL RESULTS")
        print("=" * 80)
        print("EV Diff = Actual Result - Expected Value")
        print("  Positive = Ran good (lucky) | Negative = Ran bad (unlucky)")
        print("=" * 80)
        print(allin_df[[
            'total_allin', 'heads_up_count', 'multiway_count',
            'won', 'lost', 'total_ev', 'total_actual', 'ev_diff', 'win_rate'
        ]].round(2))

        if len(allin_df) > 0:
            luckiest = allin_df.iloc[0]
            unluckiest = allin_df.iloc[-1]

            print(f"\n📊 KEY ALL-IN INSIGHTS:")
            print(f"\n   🍀 LUCKIEST (Ran Above EV): {allin_df.index[0]}")
            print(f"      • EV Difference: ${luckiest['ev_diff']:,.0f}")
            print(f"      • Expected: ${luckiest['total_ev']:,.0f}")
            print(f"      • Actual: ${luckiest['total_actual']:,.0f}")
            print(f"      • All-ins: {int(luckiest['total_allin'])} "
                  f"({int(luckiest['heads_up_count'])} HU, "
                  f"{int(luckiest['multiway_count'])} MW)")

            print(f"\n   💀 UNLUCKIEST (Ran Below EV): {allin_df.index[-1]}")
            print(f"      • EV Difference: ${unluckiest['ev_diff']:,.0f}")
            print(f"      • Expected: ${unluckiest['total_ev']:,.0f}")
            print(f"      • Actual: ${unluckiest['total_actual']:,.0f}")
            print(f"      • All-ins: {int(unluckiest['total_allin'])} "
                  f"({int(unluckiest['heads_up_count'])} HU, "
                  f"{int(unluckiest['multiway_count'])} MW)")

            allin_df['abs_ev_diff'] = abs(allin_df['ev_diff'])
            closest_to_ev = allin_df.nsmallest(1, 'abs_ev_diff').iloc[0]
            print(f"\n   🎯 CLOSEST TO EV: {allin_df.nsmallest(1, 'abs_ev_diff').index[0]}")
            print(f"      • EV Difference: ${closest_to_ev['ev_diff']:,.0f}")
            print(f"      • Result matched expectation within "
                  f"${abs(closest_to_ev['ev_diff']):,.0f}")

        print("\n" + "=" * 80)
        print("📝 METHODOLOGY:")
        print("   • Equity calculation: eval7 library (exact enumeration or Monte Carlo)")
        print("   • Supports multi-way all-ins (3+ players)")
        print("   • EV = (Your Equity × Total Pot) - Amount Invested")
        print("   • HU = Heads-up (2 players), MW = Multi-way (3+ players)")
        print("=" * 80)
