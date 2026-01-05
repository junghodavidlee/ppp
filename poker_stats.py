"""Player statistics and analysis calculations."""

import pandas as pd
from typing import List, Dict
from collections import defaultdict
from poker_utils import get_position, calculate_exact_equity_multiway


class PlayerStatistics:
    """Calculate player statistics from hands and ledger data."""

    def __init__(self, player_mapper):
        """
        Initialize statistics calculator.

        Args:
            player_mapper: PlayerMapper instance for ID resolution
        """
        self.player_mapper = player_mapper

    def calculate_from_ledger(
        self,
        ledger_df: pd.DataFrame,
        hands: List[Dict]
    ) -> pd.DataFrame:
        """
        Calculate player statistics from ledger data.

        Args:
            ledger_df: DataFrame containing ledger data
            hands: List of hand dictionaries

        Returns:
            DataFrame with player statistics
        """
        player_stats = defaultdict(lambda: {
            'hands_played': 0,
            'hands_won': 0,
            'total_buy_in': 0,
            'total_buy_out': 0,
            'total_stack': 0,
            'net_profit': 0,
            'sessions': 0
        })

        # Process ledger data
        for idx, row in ledger_df.iterrows():
            player_id = row['player_id']
            player_nickname = row['player_nickname']

            # Try to map by ID first
            if player_id in self.player_mapper.player_id_mapping:
                unified_player = self.player_mapper.player_id_mapping[player_id]
            else:
                player_full = f"{player_nickname} @ {player_id}"
                unified_player = self.player_mapper.get_unified_name(player_full)

            buy_in = row['buy_in'] if pd.notna(row['buy_in']) else 0
            buy_out = row['buy_out'] if pd.notna(row['buy_out']) else 0
            stack = row['stack'] if pd.notna(row['stack']) else 0
            net = row['net'] if pd.notna(row['net']) else 0

            player_stats[unified_player]['total_buy_in'] += buy_in
            player_stats[unified_player]['total_buy_out'] += buy_out
            player_stats[unified_player]['total_buy_out'] += stack
            player_stats[unified_player]['total_stack'] += stack
            player_stats[unified_player]['net_profit'] += net
            player_stats[unified_player]['sessions'] += 1

        # Process hands for win statistics
        for hand in hands:
            for player, data in hand['players'].items():
                unified_player = self.player_mapper.get_unified_name(player)
                player_stats[unified_player]['hands_played'] += 1

                if hand['winner'] == player:
                    player_stats[unified_player]['hands_won'] += 1

        # Calculate derived metrics
        for player in player_stats:
            stats = player_stats[player]
            stats['win_rate'] = (
                stats['hands_won'] / stats['hands_played'] * 100
                if stats['hands_played'] > 0 else 0
            )
            stats['roi'] = (
                stats['net_profit'] / stats['total_buy_in'] * 100
                if stats['total_buy_in'] > 0 else 0
            )

        return pd.DataFrame.from_dict(
            player_stats, orient='index'
        ).sort_values('net_profit', ascending=False)

    def calculate_positional_stats(self, hands: List[Dict]) -> Dict:
        """
        Calculate positional statistics for all players.

        Args:
            hands: List of hand dictionaries

        Returns:
            Nested dictionary of positional stats by player and position
        """
        positional_stats = defaultdict(lambda: defaultdict(lambda: {
            'hands': 0, 'won': 0, 'invested': 0, 'won_chips': 0
        }))

        for hand in hands:
            winner = hand.get('winner')
            for player, data in hand['players'].items():
                unified_player = self.player_mapper.get_unified_name(player)
                position = get_position(hand, player)

                positional_stats[unified_player][position]['hands'] += 1
                positional_stats[unified_player][position]['invested'] += data.get('invested', 0)

                if player == winner:
                    positional_stats[unified_player][position]['won'] += 1
                    positional_stats[unified_player][position]['won_chips'] += hand.get('pot', 0)

        return positional_stats


class AllInAnalyzer:
    """Analyze all-in situations and calculate EV."""

    def __init__(self, player_mapper):
        """
        Initialize all-in analyzer.

        Args:
            player_mapper: PlayerMapper instance for ID resolution
        """
        self.player_mapper = player_mapper

    def find_allin_situations(self, hands: List[Dict]) -> List[Dict]:
        """
        Identify all-in hands where 2+ players showed cards.

        Args:
            hands: List of hand dictionaries

        Returns:
            List of all-in situation dictionaries
        """
        allin_situations = []

        for hand in hands:
            players_allin = []

            for player, data in hand['players'].items():
                invested = data.get('invested', 0)
                initial_stack = data.get('initial_stack', 0)
                hole_cards = data.get('hole_cards')

                if initial_stack > 0 and invested >= initial_stack and hole_cards:
                    players_allin.append({
                        'player': player,
                        'hole_cards': hole_cards,
                        'invested': invested,
                        'initial_stack': initial_stack
                    })

            if len(players_allin) >= 2:
                allin_situations.append({
                    'hand': hand,
                    'allin_players': players_allin
                })

        return allin_situations

    def analyze_allin_ev(self, hands: List[Dict]) -> pd.DataFrame:
        """
        Analyze all-in EV vs actual results.

        Args:
            hands: List of hand dictionaries

        Returns:
            DataFrame with all-in statistics
        """
        allin_situations = self.find_allin_situations(hands)
        allin_stats = defaultdict(lambda: {
            'total_allin': 0,
            'won': 0,
            'lost': 0,
            'total_ev': 0,
            'total_actual': 0,
            'ev_diff': 0,
            'multiway_count': 0,
            'heads_up_count': 0
        })

        successful_calcs = 0
        failed_calcs = 0

        for situation in allin_situations:
            hand = situation['hand']
            allin_players = situation['allin_players']
            board = hand.get('board', [])
            pot = hand.get('pot', 0)
            winner = hand.get('winner')

            player_hands = [p['hole_cards'] for p in allin_players]
            equities = calculate_exact_equity_multiway(player_hands, board)

            if equities is not None and len(equities) == len(allin_players):
                successful_calcs += 1
                is_multiway = len(allin_players) > 2

                for player_data, equity in zip(allin_players, equities):
                    player = player_data['player']
                    unified_player = self.player_mapper.get_unified_name(player)
                    invested = player_data['invested']

                    ev = equity * pot - invested

                    if player == winner:
                        actual = pot - invested
                    else:
                        actual = -invested

                    allin_stats[unified_player]['total_allin'] += 1
                    allin_stats[unified_player]['total_ev'] += ev
                    allin_stats[unified_player]['total_actual'] += actual

                    if is_multiway:
                        allin_stats[unified_player]['multiway_count'] += 1
                    else:
                        allin_stats[unified_player]['heads_up_count'] += 1

                    if player == winner:
                        allin_stats[unified_player]['won'] += 1
                    else:
                        allin_stats[unified_player]['lost'] += 1
            else:
                failed_calcs += 1

        # Calculate final stats
        for player in allin_stats:
            stats = allin_stats[player]
            stats['ev_diff'] = stats['total_actual'] - stats['total_ev']
            stats['win_rate'] = (
                stats['won'] / stats['total_allin'] * 100
                if stats['total_allin'] > 0 else 0
            )

        # Create DataFrame from stats
        if allin_stats:
            df = pd.DataFrame.from_dict(
                allin_stats, orient='index'
            ).sort_values('ev_diff', ascending=False)
        else:
            # Return empty DataFrame with correct columns
            df = pd.DataFrame(columns=[
                'total_allin', 'won', 'lost', 'total_ev', 'total_actual',
                'ev_diff', 'multiway_count', 'heads_up_count', 'win_rate'
            ])

        return df


class RangeAnalyzer:
    """Analyze player hand ranges from showdown data."""

    def __init__(self, player_mapper):
        """
        Initialize range analyzer.

        Args:
            player_mapper: PlayerMapper instance for ID resolution
        """
        self.player_mapper = player_mapper

    def collect_showdown_ranges(self, hands: List[Dict]) -> Dict[str, Dict[str, int]]:
        """
        Collect all showdown hands for each player.

        Args:
            hands: List of hand dictionaries

        Returns:
            Dictionary mapping players to their showdown hand frequencies
        """
        from poker_utils import parse_hole_cards

        player_ranges = defaultdict(lambda: defaultdict(int))

        for hand in hands:
            for player, data in hand['players'].items():
                hole_cards = data.get('hole_cards')
                if hole_cards:
                    unified_player = self.player_mapper.get_unified_name(player)
                    hand_notation = parse_hole_cards(hole_cards)
                    if hand_notation:
                        player_ranges[unified_player][hand_notation] += 1

        return player_ranges

    @staticmethod
    def create_hand_matrix():
        """
        Create 13x13 matrix of all possible starting hands.

        Returns:
            Tuple of (matrix, ranks)
        """
        ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
        matrix = []

        for i, rank1 in enumerate(ranks):
            row = []
            for j, rank2 in enumerate(ranks):
                if i == j:
                    row.append(f"{rank1}{rank2}")
                elif i < j:
                    row.append(f"{rank1}{rank2}s")
                else:
                    row.append(f"{rank2}{rank1}o")
            matrix.append(row)

        return matrix, ranks
