"""Data loading and processing classes for poker analytics."""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple
from poker_utils import extract_hand_info, parse_player_string


class PokerDataLoader:
    """Handles loading and preprocessing of poker log and ledger data."""

    def __init__(self, data_dir: str = 'data/log', ledger_dir: str = 'data/ledger'):
        """
        Initialize the data loader.

        Args:
            data_dir: Directory containing log CSV files
            ledger_dir: Directory containing ledger CSV files
        """
        self.data_dir = Path(data_dir)
        self.ledger_dir = Path(ledger_dir)

    def load_log_data(self) -> pd.DataFrame:
        """
        Load all CSV log files from the data directory.

        Returns:
            DataFrame containing all log entries with source_file column

        Raises:
            FileNotFoundError: If data directory doesn't exist
            ValueError: If no CSV files found in directory
        """
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {self.data_dir}")

        csv_files = sorted(self.data_dir.glob('*.csv'))
        if not csv_files:
            raise ValueError(f"No CSV files found in {self.data_dir}")

        dfs = []
        for csv_file in csv_files:
            print(f"Loading {csv_file.name}...")
            df = pd.read_csv(csv_file)
            df['source_file'] = csv_file.name
            dfs.append(df)

        raw_data = pd.concat(dfs, ignore_index=True)
        raw_data['at'] = pd.to_datetime(raw_data['at'])
        raw_data = raw_data.sort_values('order').reset_index(drop=True)

        print(f"\nTotal entries: {len(raw_data):,}")
        print(f"Date range: {raw_data['at'].min()} to {raw_data['at'].max()}\n")

        return raw_data

    def load_ledger_data(self) -> pd.DataFrame:
        """
        Load all CSV ledger files from the ledger directory.

        Returns:
            DataFrame containing all ledger entries with source_file column

        Raises:
            FileNotFoundError: If ledger directory doesn't exist
            ValueError: If no CSV files found in directory
        """
        if not self.ledger_dir.exists():
            raise FileNotFoundError(f"Ledger directory not found: {self.ledger_dir}")

        ledger_files = sorted(self.ledger_dir.glob('*.csv'))
        if not ledger_files:
            raise ValueError(f"No CSV files found in {self.ledger_dir}")

        ledger_dfs = []
        for ledger_file in ledger_files:
            print(f"Loading {ledger_file.name}...")
            df = pd.read_csv(ledger_file)
            df['source_file'] = ledger_file.name
            ledger_dfs.append(df)

        ledger_data = pd.concat(ledger_dfs, ignore_index=True)
        print(f"Total ledger entries: {len(ledger_data):,}\n")

        return ledger_data


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

                    # If no dealer was recorded (dead button situation), infer the button
                    # In dead button hands, the cutoff becomes the effective button
                    # Find the player who is not SB or BB - they are in the button/cutoff position
                    if not current_hand.get('dealer'):
                        sb_player = current_hand.get('small_blind_player')
                        bb_player = current_hand.get('big_blind_player')
                        players = list(current_hand['players'].keys())

                        # The button is the player who is neither SB nor BB
                        for player in players:
                            if player != sb_player and player != bb_player:
                                current_hand['dealer'] = player
                                break

                        # If we still don't have a dealer (e.g., heads-up dead button),
                        # use the small blind as the button
                        if not current_hand.get('dealer') and sb_player:
                            current_hand['dealer'] = sb_player

                    hands.append(current_hand)
                    current_hand = None

            elif current_hand:
                if info['type'] == 'player_stacks':
                    for player, stack in info['stacks'].items():
                        current_hand['players'][player] = {
                            'initial_stack': stack,
                            'invested': 0
                        }

                elif info['type'] == 'small_blind':
                    player = info['player']
                    amount = info['amount']
                    # Track small blind player for dead button inference
                    current_hand['small_blind_player'] = player
                    if player in current_hand['players']:
                        current_hand['players'][player]['invested'] = \
                            current_hand['players'][player].get('invested', 0) + amount

                elif info['type'] == 'big_blind':
                    player = info['player']
                    amount = info['amount']
                    # Track big blind player for dead button inference
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

                elif info['type'] == 'uncalled_bet':
                    # Subtract uncalled bet from player's invested amount
                    player = info['player']
                    amount = info['amount']
                    if player in current_hand['players']:
                        current_hand['players'][player]['invested'] = \
                            current_hand['players'][player].get('invested', 0) - amount

        return hands


class PlayerMapper:
    """Manages player identity mapping and unified player names."""

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

    def map_ledger_data(self, ledger_df: pd.DataFrame) -> pd.DataFrame:
        """
        Add unified_player and session_date columns to ledger data.

        Args:
            ledger_df: DataFrame containing ledger data

        Returns:
            DataFrame with unified_player and session_date columns added
        """
        ledger_df = ledger_df.copy()

        # Map player IDs to unified names
        unified_names = []
        for _, row in ledger_df.iterrows():
            player_id = row['player_id']
            player_nickname = row['player_nickname']

            if player_id in self.player_id_mapping:
                unified_player = self.player_id_mapping[player_id]
            else:
                player_full = f"{player_nickname} @ {player_id}"
                unified_player = self.get_unified_name(player_full)

            unified_names.append(unified_player)

        ledger_df['unified_player'] = unified_names

        # Extract session date from source_file
        if 'source_file' in ledger_df.columns:
            ledger_df['session_date'] = ledger_df['source_file'].str.extract(r'(\d+)_ledger\.csv')[0]
        elif 'session_start_at' in ledger_df.columns:
            ledger_df['session_date'] = pd.to_datetime(ledger_df['session_start_at']).dt.strftime('%m%d')
        else:
            ledger_df['session_date'] = ledger_df.index.astype(str)

        return ledger_df

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
