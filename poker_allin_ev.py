"""All-in EV analysis and comparison tools for poker hand history."""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from poker_utils import extract_hand_info, calculate_exact_equity_multiway


class AllInEVAnalyzer:
    """Analyzes all-in situations and compares EV to actual results."""

    def __init__(self, player_mapper):
        """
        Initialize all-in EV analyzer.

        Args:
            player_mapper: PlayerMapper instance for ID resolution
        """
        self.player_mapper = player_mapper

    def parse_hands_with_allin_tracking(self, raw_data: pd.DataFrame) -> List[Dict]:
        """
        Parse hands and track all-in situations with street information.

        Only tracks situations where:
        - A player goes all-in OR calls an all-in
        - This happens BEFORE the river is dealt (preflop, flop, or turn)
        - At least 2 players show their cards

        Args:
            raw_data: DataFrame containing log entries

        Returns:
            List of hand dictionaries with all-in tracking
        """
        hands = []
        current_hand = None
        current_street = 'preflop'

        for idx, row in raw_data.iterrows():
            entry = row['entry']
            info = extract_hand_info(entry)
            info['timestamp'] = row['at']

            if info['type'] == 'hand_start':
                current_hand = {
                    'hand_number': info['hand_number'],
                    'hand_id': info['hand_id'],
                    'dealer': info.get('dealer'),
                    'start_time': info['timestamp'],
                    'actions': [],
                    'players': {},
                    'board': [],
                    'pot': 0,
                    'winner': None,
                    'winning_hand': None,
                    'allin_street': None,  # Track when all-in happened
                    'board_at_allin': []  # Board cards at time of all-in
                }
                current_street = 'preflop'

            elif info['type'] == 'hand_end':
                if current_hand:
                    current_hand['end_time'] = info['timestamp']

                    # Infer dealer for dead button situations
                    if not current_hand.get('dealer'):
                        sb_player = current_hand.get('small_blind_player')
                        bb_player = current_hand.get('big_blind_player')
                        players = list(current_hand['players'].keys())

                        for player in players:
                            if player != sb_player and player != bb_player:
                                current_hand['dealer'] = player
                                break

                        if not current_hand.get('dealer') and sb_player:
                            current_hand['dealer'] = sb_player

                    hands.append(current_hand)
                    current_hand = None
                    current_street = 'preflop'

            elif current_hand:
                # Track street transitions
                if info['type'] == 'flop':
                    current_street = 'flop'
                    current_hand['board'] = info['cards']
                elif info['type'] == 'turn':
                    current_street = 'turn'
                    current_hand['board'] = info['cards']
                elif info['type'] == 'river':
                    current_street = 'river'
                    current_hand['board'] = info['cards']

                # Track player stacks and actions
                if info['type'] == 'player_stacks':
                    for player, stack in info['stacks'].items():
                        current_hand['players'][player] = {
                            'initial_stack': stack,
                            'invested': 0,
                            'is_allin': False
                        }

                elif info['type'] == 'small_blind':
                    player = info['player']
                    amount = info['amount']
                    current_hand['small_blind_player'] = player
                    if player in current_hand['players']:
                        current_hand['players'][player]['invested'] = \
                            current_hand['players'][player].get('invested', 0) + amount

                elif info['type'] == 'big_blind':
                    player = info['player']
                    amount = info['amount']
                    current_hand['big_blind_player'] = player
                    if player in current_hand['players']:
                        current_hand['players'][player]['invested'] = \
                            current_hand['players'][player].get('invested', 0) + amount

                elif info['type'] in ['call', 'bet', 'raise']:
                    player = info['player']
                    amount = info['amount']
                    if player in current_hand['players']:
                        current_hand['players'][player]['invested'] = \
                            current_hand['players'][player].get('invested', 0) + amount

                        # Check if this player is now all-in (before river)
                        if current_street != 'river':
                            invested = current_hand['players'][player]['invested']
                            initial_stack = current_hand['players'][player]['initial_stack']

                            if invested >= initial_stack:
                                current_hand['players'][player]['is_allin'] = True
                                # Record the street and board when first all-in detected
                                if current_hand['allin_street'] is None:
                                    current_hand['allin_street'] = current_street
                                    current_hand['board_at_allin'] = current_hand['board'].copy()

                elif info['type'] == 'show':
                    player = info['player']
                    if player in current_hand['players']:
                        current_hand['players'][player]['hole_cards'] = info['cards']

                elif info['type'] == 'pot_collected':
                    current_hand['winner'] = info['player']
                    current_hand['pot'] = info['amount']
                    current_hand['winning_hand'] = info.get('winning_hand')

                elif info['type'] == 'uncalled_bet':
                    player = info['player']
                    amount = info['amount']
                    if player in current_hand['players']:
                        current_hand['players'][player]['invested'] = \
                            current_hand['players'][player].get('invested', 0) - amount

        return hands

    def extract_allin_situations(self, hands: List[Dict]) -> List[Dict]:
        """
        Extract all-in situations from parsed hands.

        Only includes hands where:
        - All-in occurred before river (preflop, flop, or turn)
        - At least 2 players are all-in or called all-in
        - Players showed their cards

        Args:
            hands: List of hand dictionaries with all-in tracking

        Returns:
            List of all-in situation dictionaries
        """
        allin_situations = []

        for hand in hands:
            # Skip if no all-in detected or all-in was on river
            if hand['allin_street'] is None or hand['allin_street'] == 'river':
                continue

            # Find all players who are all-in and showed cards
            players_allin = []
            for player, data in hand['players'].items():
                if data.get('is_allin') and data.get('hole_cards'):
                    players_allin.append({
                        'player': player,
                        'hole_cards': data['hole_cards'],
                        'invested': data['invested'],
                        'initial_stack': data['initial_stack']
                    })

            # Only include if at least 2 players are all-in with known cards
            if len(players_allin) >= 2:
                allin_situations.append({
                    'hand': hand,
                    'allin_players': players_allin,
                    'allin_street': hand['allin_street'],
                    'board_at_allin': hand['board_at_allin']
                })

        return allin_situations

    def calculate_allin_ev_by_hand(
        self,
        hands: List[Dict],
        target_player: Optional[str] = None
    ) -> Dict[str, List[Dict]]:
        """
        Calculate EV and actual results for each all-in hand.

        Args:
            hands: List of hand dictionaries
            target_player: Unified player name to track (or None for all players)

        Returns:
            Dictionary mapping player names to list of hand results
        """
        allin_situations = self.extract_allin_situations(hands)

        # Track results by player
        player_results = defaultdict(list)

        for idx, situation in enumerate(allin_situations):
            hand = situation['hand']
            allin_players = situation['allin_players']
            board = situation['board_at_allin']
            pot = hand.get('pot', 0)
            winner = hand.get('winner')

            # Calculate equities at time of all-in
            player_hands = [p['hole_cards'] for p in allin_players]
            equities = calculate_exact_equity_multiway(player_hands, board)

            if equities is None or len(equities) != len(allin_players):
                continue

            # Calculate EV and actual for each player
            for player_data, equity in zip(allin_players, equities):
                player = player_data['player']
                unified_player = self.player_mapper.get_unified_name(player)

                # Skip if we're filtering for a specific player
                if target_player and unified_player != target_player:
                    continue

                invested = player_data['invested']

                # EV = equity * pot - investment
                ev_result = equity * pot - invested

                # Actual result
                if player == winner:
                    actual_result = pot - invested
                else:
                    actual_result = -invested

                player_results[unified_player].append({
                    'hand_number': hand['hand_number'],
                    'timestamp': hand['start_time'],
                    'street': situation['allin_street'],
                    'equity': equity,
                    'pot': pot,
                    'invested': invested,
                    'ev_result': ev_result,
                    'actual_result': actual_result,
                    'won': player == winner
                })

        return player_results

    def create_ev_comparison_dataframe(
        self,
        player_results: Dict[str, List[Dict]],
        player_name: str
    ) -> pd.DataFrame:
        """
        Create a DataFrame with cumulative EV vs actual results.

        Args:
            player_results: Dictionary of player results from calculate_allin_ev_by_hand
            player_name: Player name to create DataFrame for

        Returns:
            DataFrame with columns: hand_number, timestamp, cumulative_ev, cumulative_actual
        """
        if player_name not in player_results:
            return pd.DataFrame(columns=[
                'hand_number', 'timestamp', 'street', 'equity',
                'ev_result', 'actual_result', 'cumulative_ev', 'cumulative_actual'
            ])

        results = player_results[player_name]

        # Sort by timestamp
        results_sorted = sorted(results, key=lambda x: x['timestamp'])

        # Calculate cumulative totals
        cumulative_ev = 0
        cumulative_actual = 0

        rows = []
        for result in results_sorted:
            cumulative_ev += result['ev_result']
            cumulative_actual += result['actual_result']

            rows.append({
                'hand_number': result['hand_number'],
                'timestamp': result['timestamp'],
                'street': result['street'],
                'equity': result['equity'],
                'ev_result': result['ev_result'],
                'actual_result': result['actual_result'],
                'cumulative_ev': cumulative_ev,
                'cumulative_actual': cumulative_actual,
                'won': result['won']
            })

        return pd.DataFrame(rows)

    def plot_ev_comparison(
        self,
        player_name: str,
        df: pd.DataFrame,
        figsize: Tuple[int, int] = (14, 6)
    ) -> plt.Figure:
        """
        Plot cumulative EV vs actual results for a player.

        Args:
            player_name: Name of the player
            df: DataFrame from create_ev_comparison_dataframe
            figsize: Figure size tuple

        Returns:
            Matplotlib figure object
        """
        if df.empty:
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, f'No all-in data available for {player_name}',
                   ha='center', va='center', fontsize=14)
            ax.set_title(f'All-In EV Comparison: {player_name}')
            return fig

        fig, ax = plt.subplots(figsize=figsize)

        # Create x-axis as hand count (0, 1, 2, 3, ...)
        # Start at 0 with value 0, then plot actual data points
        x = list(range(0, len(df) + 1))
        ev_values = [0] + df['cumulative_ev'].tolist()
        actual_values = [0] + df['cumulative_actual'].tolist()

        # Plot both lines
        ax.plot(x, ev_values,
               label='Expected Value (EV)',
               color='#2E86AB',
               linewidth=2.5,
               marker='o',
               markersize=4,
               alpha=0.8)

        ax.plot(x, actual_values,
               label='Actual Result',
               color='#A23B72',
               linewidth=2.5,
               marker='s',
               markersize=4,
               alpha=0.8)

        # Add zero line
        ax.axhline(y=0, color='gray', linestyle='--', linewidth=1, alpha=0.5)

        # Styling
        ax.set_xlabel('Number of All-In Hands', fontsize=12, fontweight='bold')
        ax.set_ylabel('Profit/Loss', fontsize=12, fontweight='bold')
        ax.set_title(f'All-In EV Comparison: {player_name}',
                    fontsize=14, fontweight='bold', pad=20)

        # Set x-axis to start at 0 with integer intervals of at least 1
        ax.set_xlim(left=0)
        ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True, min_n_ticks=1))

        ax.legend(fontsize=11, loc='best', framealpha=0.9)
        ax.grid(True, alpha=0.3, linestyle='--')

        # Format y-axis as currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

        # Add final values as text
        final_ev = df['cumulative_ev'].iloc[-1]
        final_actual = df['cumulative_actual'].iloc[-1]
        diff = final_actual - final_ev

        stats_text = f'Final EV: ${final_ev:,.0f}\n'
        stats_text += f'Final Actual: ${final_actual:,.0f}\n'
        stats_text += f'Difference: ${diff:+,.0f}'

        # Position text box
        ax.text(0.02, 0.98, stats_text,
               transform=ax.transAxes,
               fontsize=10,
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

        plt.tight_layout()
        return fig

    def print_allin_summary(
        self,
        player_name: str,
        df: pd.DataFrame
    ):
        """
        Print a summary of all-in performance.

        Args:
            player_name: Name of the player
            df: DataFrame from create_ev_comparison_dataframe
        """
        if df.empty:
            print(f"\nNo all-in data available for {player_name}\n")
            return

        print("\n" + "="*80)
        print(f"ALL-IN EV ANALYSIS: {player_name}")
        print("="*80)

        total_hands = len(df)
        wins = df['won'].sum()
        losses = total_hands - wins
        win_rate = (wins / total_hands * 100) if total_hands > 0 else 0

        final_ev = df['cumulative_ev'].iloc[-1]
        final_actual = df['cumulative_actual'].iloc[-1]
        ev_diff = final_actual - final_ev

        print(f"\n📊 SUMMARY STATISTICS:")
        print(f"   Total All-In Hands (pre-river): {total_hands}")
        print(f"   Wins: {wins} | Losses: {losses} | Win Rate: {win_rate:.1f}%")

        print(f"\n💰 FINANCIAL RESULTS:")
        print(f"   Expected Value (EV):  ${final_ev:>12,.0f}")
        print(f"   Actual Result:        ${final_actual:>12,.0f}")
        print(f"   Difference:           ${ev_diff:>+12,.0f}")

        if ev_diff > 0:
            print(f"\n🍀 Running ABOVE EV (lucky)")
        elif ev_diff < 0:
            print(f"\n😢 Running BELOW EV (unlucky)")
        else:
            print(f"\n➡️  Running exactly at EV")

        # Street breakdown
        street_counts = df['street'].value_counts()
        print(f"\n🃏 ALL-IN BY STREET:")
        for street in ['preflop', 'flop', 'turn']:
            count = street_counts.get(street, 0)
            pct = (count / total_hands * 100) if total_hands > 0 else 0
            print(f"   {street.capitalize():8s}: {count:3d} hands ({pct:5.1f}%)")

        # Average equity when all-in
        avg_equity = df['equity'].mean() * 100
        print(f"\n📈 AVERAGE EQUITY AT ALL-IN: {avg_equity:.1f}%")

        print("="*80 + "\n")
