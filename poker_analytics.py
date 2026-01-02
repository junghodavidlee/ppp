import pandas as pd
import re
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

class PokerDataProcessor:
    """Process and analyze Texas Hold'em poker hand logs."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.raw_data = []
        self.hands = []

    def load_all_csvs(self) -> pd.DataFrame:
        """Load all CSV files from the data directory."""
        csv_files = sorted(self.data_dir.glob("*.csv"))

        dfs = []
        for csv_file in csv_files:
            print(f"Loading {csv_file.name}...")
            df = pd.read_csv(csv_file)
            df['source_file'] = csv_file.name
            dfs.append(df)

        combined_df = pd.concat(dfs, ignore_index=True)
        print(f"\nTotal entries loaded: {len(combined_df)}")

        # Convert timestamp
        combined_df['at'] = pd.to_datetime(combined_df['at'])

        # Sort by order (chronological)
        combined_df = combined_df.sort_values('order').reset_index(drop=True)

        self.raw_data = combined_df
        return combined_df

    def extract_hand_info(self, entry: str) -> Dict:
        """Extract information from different types of log entries."""
        info = {'type': 'unknown', 'raw': entry}

        # Hand start/end markers
        if '-- starting hand' in entry:
            match = re.search(r'hand #(\d+) \(id: ([^\)]+)\)', entry)
            if match:
                info['type'] = 'hand_start'
                info['hand_number'] = int(match.group(1))
                info['hand_id'] = match.group(2)

            # Extract dealer
            dealer_match = re.search(r'dealer: "([^"]+)"', entry)
            if dealer_match:
                info['dealer'] = dealer_match.group(1)

        elif '-- ending hand' in entry:
            match = re.search(r'hand #(\d+)', entry)
            if match:
                info['type'] = 'hand_end'
                info['hand_number'] = int(match.group(1))

        # Player stacks
        elif 'Player stacks:' in entry:
            info['type'] = 'player_stacks'
            players = re.findall(r'#(\d+) "([^"]+)" \((\d+)\)', entry)
            info['stacks'] = {player[1]: int(player[2]) for player in players}

        # Blinds
        elif 'posts a small blind' in entry:
            match = re.search(r'"([^"]+)" posts a small blind of (\d+)', entry)
            if match:
                info['type'] = 'small_blind'
                info['player'] = match.group(1)
                info['amount'] = int(match.group(2))

        elif 'posts a big blind' in entry:
            match = re.search(r'"([^"]+)" posts a big blind of (\d+)', entry)
            if match:
                info['type'] = 'big_blind'
                info['player'] = match.group(1)
                info['amount'] = int(match.group(2))

        # Flop, Turn, River
        elif entry.startswith('Flop:'):
            cards = re.findall(r'[2-9TJQKA][♠♥♦♣]', entry)
            info['type'] = 'flop'
            info['cards'] = cards

        elif entry.startswith('Turn:'):
            cards = re.findall(r'[2-9TJQKA][♠♥♦♣]', entry)
            info['type'] = 'turn'
            info['cards'] = cards

        elif entry.startswith('River:'):
            cards = re.findall(r'[2-9TJQKA][♠♥♦♣]', entry)
            info['type'] = 'river'
            info['cards'] = cards

        # Player actions
        elif ' calls ' in entry:
            match = re.search(r'"([^"]+)" calls (\d+)', entry)
            if match:
                info['type'] = 'call'
                info['player'] = match.group(1)
                info['amount'] = int(match.group(2))

        elif ' bets ' in entry:
            match = re.search(r'"([^"]+)" bets (\d+)', entry)
            if match:
                info['type'] = 'bet'
                info['player'] = match.group(1)
                info['amount'] = int(match.group(2))

        elif ' raises to ' in entry:
            match = re.search(r'"([^"]+)" raises to (\d+)', entry)
            if match:
                info['type'] = 'raise'
                info['player'] = match.group(1)
                info['amount'] = int(match.group(2))

        elif ' checks' in entry:
            match = re.search(r'"([^"]+)" checks', entry)
            if match:
                info['type'] = 'check'
                info['player'] = match.group(1)

        elif ' folds' in entry:
            match = re.search(r'"([^"]+)" folds', entry)
            if match:
                info['type'] = 'fold'
                info['player'] = match.group(1)

        # Showdown
        elif ' shows a ' in entry:
            match = re.search(r'"([^"]+)" shows a (.+)\.', entry)
            if match:
                info['type'] = 'show'
                info['player'] = match.group(1)
                cards = re.findall(r'[2-9TJQKA][♠♥♦♣]', match.group(2))
                info['cards'] = cards

        # Pot collection
        elif ' collected ' in entry and ' from pot' in entry:
            match = re.search(r'"([^"]+)" collected (\d+) from pot', entry)
            if match:
                info['type'] = 'pot_collected'
                info['player'] = match.group(1)
                info['amount'] = int(match.group(2))

            # Extract winning hand
            hand_match = re.search(r'with (.+?) \(combination: ([^)]+)\)', entry)
            if hand_match:
                info['winning_hand'] = hand_match.group(1)
                info['combination'] = hand_match.group(2)

        # Uncalled bet
        elif 'Uncalled bet' in entry:
            match = re.search(r'Uncalled bet of (\d+) returned to "([^"]+)"', entry)
            if match:
                info['type'] = 'uncalled_bet'
                info['amount'] = int(match.group(1))
                info['player'] = match.group(2)

        return info

    def parse_hands(self) -> List[Dict]:
        """Parse raw data into structured hand information."""
        if self.raw_data is None or len(self.raw_data) == 0:
            raise ValueError("No data loaded. Call load_all_csvs() first.")

        hands = []
        current_hand = None

        for idx, row in self.raw_data.iterrows():
            entry = row['entry']
            info = self.extract_hand_info(entry)
            info['timestamp'] = row['at']
            info['order'] = row['order']

            if info['type'] == 'hand_start':
                # Start new hand
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
                # Close current hand
                if current_hand:
                    current_hand['end_time'] = info['timestamp']
                    hands.append(current_hand)
                    current_hand = None

            elif current_hand:
                # Add information to current hand
                if info['type'] == 'player_stacks':
                    for player, stack in info['stacks'].items():
                        current_hand['players'][player] = {'initial_stack': stack, 'invested': 0}

                elif info['type'] in ['small_blind', 'big_blind', 'call', 'bet', 'raise']:
                    player = info['player']
                    amount = info['amount']

                    if player in current_hand['players']:
                        current_hand['players'][player]['invested'] = \
                            current_hand['players'][player].get('invested', 0) + amount

                    current_hand['actions'].append({
                        'action': info['type'],
                        'player': player,
                        'amount': amount,
                        'timestamp': info['timestamp']
                    })

                elif info['type'] in ['check', 'fold']:
                    current_hand['actions'].append({
                        'action': info['type'],
                        'player': info['player'],
                        'timestamp': info['timestamp']
                    })

                elif info['type'] in ['flop', 'turn', 'river']:
                    current_hand['board'] = info['cards']
                    current_hand['actions'].append({
                        'action': info['type'],
                        'cards': info['cards'],
                        'timestamp': info['timestamp']
                    })

                elif info['type'] == 'show':
                    player = info['player']
                    if player in current_hand['players']:
                        current_hand['players'][player]['hole_cards'] = info['cards']

                elif info['type'] == 'pot_collected':
                    current_hand['winner'] = info['player']
                    current_hand['pot'] = info['amount']
                    current_hand['winning_hand'] = info.get('winning_hand')

        self.hands = hands
        print(f"\nParsed {len(hands)} complete hands")
        return hands

    def get_player_statistics(self) -> pd.DataFrame:
        """Calculate statistics for each player."""
        player_stats = {}

        for hand in self.hands:
            for player, data in hand['players'].items():
                if player not in player_stats:
                    player_stats[player] = {
                        'hands_played': 0,
                        'hands_won': 0,
                        'total_invested': 0,
                        'total_won': 0,
                        'net_profit': 0
                    }

                player_stats[player]['hands_played'] += 1
                player_stats[player]['total_invested'] += data.get('invested', 0)

                if hand['winner'] == player:
                    player_stats[player]['hands_won'] += 1
                    player_stats[player]['total_won'] += hand['pot']

        # Calculate net profit
        for player in player_stats:
            player_stats[player]['net_profit'] = \
                player_stats[player]['total_won'] - player_stats[player]['total_invested']
            player_stats[player]['win_rate'] = \
                player_stats[player]['hands_won'] / player_stats[player]['hands_played'] if player_stats[player]['hands_played'] > 0 else 0

        return pd.DataFrame.from_dict(player_stats, orient='index')

    def summary(self):
        """Print a summary of the loaded data."""
        print("\n" + "="*60)
        print("POKER DATA SUMMARY")
        print("="*60)

        if len(self.raw_data) > 0:
            print(f"\nTotal log entries: {len(self.raw_data)}")
            print(f"Date range: {self.raw_data['at'].min()} to {self.raw_data['at'].max()}")
            print(f"\nEntry types:")

            entry_types = self.raw_data['entry'].apply(lambda x: self.extract_hand_info(x)['type'])
            print(entry_types.value_counts().head(20))

        if len(self.hands) > 0:
            print(f"\n\nTotal hands: {len(self.hands)}")

            # Player stats
            stats = self.get_player_statistics()
            print("\n" + "="*60)
            print("PLAYER STATISTICS")
            print("="*60)
            print(stats.sort_values('net_profit', ascending=False))


# Main execution
if __name__ == "__main__":
    print("Texas Hold'em Poker Analytics")
    print("="*60)

    processor = PokerDataProcessor()

    # Load data
    df = processor.load_all_csvs()

    # Parse hands
    hands = processor.parse_hands()

    # Show summary
    processor.summary()
