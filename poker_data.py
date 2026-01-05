"""Data loading and processing classes for poker analytics."""

import pandas as pd
from pathlib import Path
from typing import List, Dict
from poker_utils import extract_hand_info


class PokerDataLoader:
    """Handles loading and preprocessing of poker log data."""

    def __init__(self, data_dir: str = 'data/log', ledger_dir: str = 'data/ledger'):
        """
        Initialize the data loader.

        Args:
            data_dir: Directory containing log CSV files
            ledger_dir: Directory containing ledger CSV files
        """
        self.data_dir = Path(data_dir)
        self.ledger_dir = Path(ledger_dir)
        self.raw_data = None
        self.ledger_data = None

    def load_log_data(self) -> pd.DataFrame:
        """
        Load all CSV log files from the data directory.

        Returns:
            DataFrame containing all log entries
        """
        csv_files = sorted(self.data_dir.glob('*.csv'))
        dfs = []

        for csv_file in csv_files:
            print(f"Loading {csv_file.name}...")
            df = pd.read_csv(csv_file)
            df['source_file'] = csv_file.name
            dfs.append(df)

        self.raw_data = pd.concat(dfs, ignore_index=True)
        self.raw_data['at'] = pd.to_datetime(self.raw_data['at'])
        self.raw_data = self.raw_data.sort_values('order').reset_index(drop=True)

        print(f"\nTotal entries: {len(self.raw_data):,}")
        print(f"Date range: {self.raw_data['at'].min()} to {self.raw_data['at'].max()}")

        return self.raw_data

    def load_ledger_data(self) -> pd.DataFrame:
        """
        Load all CSV ledger files from the ledger directory.

        Returns:
            DataFrame containing all ledger entries
        """
        ledger_files = sorted(self.ledger_dir.glob('*.csv'))
        ledger_dfs = []

        for ledger_file in ledger_files:
            print(f"Loading {ledger_file.name}...")
            df = pd.read_csv(ledger_file)
            ledger_dfs.append(df)

        self.ledger_data = pd.concat(ledger_dfs, ignore_index=True)
        print(f"Total ledger entries: {len(self.ledger_data):,}\n")

        return self.ledger_data


class HandParser:
    """Parses poker hands from log data."""

    @staticmethod
    def parse_hands(data: pd.DataFrame) -> List[Dict]:
        """
        Parse all hands from log data.

        Args:
            data: DataFrame containing log entries

        Returns:
            List of hand dictionaries
        """
        hands = []
        current_hand = None

        for idx, row in data.iterrows():
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
                    'winning_hand': None
                }

            elif info['type'] == 'hand_end':
                if current_hand:
                    current_hand['end_time'] = info['timestamp']
                    hands.append(current_hand)
                    current_hand = None

            elif current_hand:
                if info['type'] == 'player_stacks':
                    for player, stack in info['stacks'].items():
                        current_hand['players'][player] = {
                            'initial_stack': stack,
                            'invested': 0
                        }

                elif info['type'] in ['small_blind', 'big_blind', 'call', 'bet', 'raise']:
                    player = info['player']
                    amount = info['amount']
                    if player in current_hand['players']:
                        current_hand['players'][player]['invested'] = \
                            current_hand['players'][player].get('invested', 0) + amount

                elif info['type'] in ['flop', 'turn', 'river']:
                    current_hand['board'] = info['cards']

                elif info['type'] == 'show':
                    player = info['player']
                    if player in current_hand['players']:
                        current_hand['players'][player]['hole_cards'] = info['cards']

                elif info['type'] == 'pot_collected':
                    current_hand['winner'] = info['player']
                    current_hand['pot'] = info['amount']
                    current_hand['winning_hand'] = info.get('winning_hand')

        return hands


class PlayerMapper:
    """Manages player identity mapping."""

    def __init__(self, player_id_mapping: Dict[str, str]):
        """
        Initialize player mapper.

        Args:
            player_id_mapping: Dictionary mapping player IDs to unified names
        """
        self.player_id_mapping = player_id_mapping
        self.player_full_to_unified = {}

    def build_mapping(self, all_player_ids: set):
        """
        Build full player string to unified name mapping.

        Args:
            all_player_ids: Set of all player identifier strings
        """
        from poker_utils import parse_player_string

        for player_str in all_player_ids:
            player_id, _ = parse_player_string(player_str)
            unified_name = self.player_id_mapping.get(player_id, player_str)
            self.player_full_to_unified[player_str] = unified_name

    def get_unified_name(self, player_str: str) -> str:
        """
        Get unified player name from any player identifier.

        Args:
            player_str: Player identifier string

        Returns:
            Unified player name
        """
        return self.player_full_to_unified.get(player_str, player_str)

    def get_merged_accounts(self) -> Dict[str, List[str]]:
        """
        Get dictionary of merged accounts (multiple IDs to same name).

        Returns:
            Dictionary mapping usernames to list of IDs
        """
        from collections import defaultdict

        username_to_ids = defaultdict(list)
        for pid, uname in self.player_id_mapping.items():
            username_to_ids[uname].append(pid)

        return {uname: ids for uname, ids in username_to_ids.items() if len(ids) > 1}
