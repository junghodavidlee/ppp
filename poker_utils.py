"""Utility functions for poker hand analysis."""

import re
import eval7
from typing import Dict, List, Optional, Tuple


def parse_player_string(player_str: str) -> Tuple[str, str]:
    """
    Extract username and ID from 'Username @ ID' format.

    Args:
        player_str: Player string in format 'Username @ ID'

    Returns:
        Tuple of (player_id, username)
    """
    if ' @ ' in player_str:
        parts = player_str.split(' @ ')
        username = parts[0].strip()
        player_id = parts[1].strip()
        return player_id, username
    return player_str, player_str


def card_string_to_eval7(card_str: str) -> Optional[eval7.Card]:
    """
    Convert card string like 'A♥' to eval7.Card format.

    Args:
        card_str: Card string in format like 'A♥', 'K♠', etc.

    Returns:
        eval7.Card object or None if invalid
    """
    rank_map = {
        'A': 'A', 'K': 'K', 'Q': 'Q', 'J': 'J', 'T': 'T',
        '9': '9', '8': '8', '7': '7', '6': '6', '5': '5',
        '4': '4', '3': '3', '2': '2'
    }
    suit_map = {'♠': 's', '♥': 'h', '♦': 'd', '♣': 'c'}

    if len(card_str) != 2:
        return None

    rank = card_str[0]
    suit = card_str[1]

    if rank not in rank_map or suit not in suit_map:
        return None

    try:
        return eval7.Card(rank_map[rank] + suit_map[suit])
    except Exception:
        return None


def parse_hole_cards(cards: List[str]) -> Optional[str]:
    """
    Convert hole cards to hand notation (e.g., ['A♥', 'K♠'] -> 'AKo').

    Args:
        cards: List of two card strings

    Returns:
        Hand notation string or None if invalid
    """
    if not cards or len(cards) != 2:
        return None

    rank_order = '23456789TJQKA'
    card1_rank, card1_suit = cards[0][0], cards[0][1]
    card2_rank, card2_suit = cards[1][0], cards[1][1]

    if rank_order.index(card1_rank) >= rank_order.index(card2_rank):
        high_rank, low_rank = card1_rank, card2_rank
        suited = card1_suit == card2_suit
    else:
        high_rank, low_rank = card2_rank, card1_rank
        suited = card1_suit == card2_suit

    if high_rank == low_rank:
        return f"{high_rank}{high_rank}"
    else:
        return f"{high_rank}{low_rank}{'s' if suited else 'o'}"


def calculate_exact_equity_multiway(
    player_hands: List[List[str]],
    board: List[str]
) -> Optional[List[float]]:
    """
    Calculate exact equity for multi-way all-in using eval7.

    Args:
        player_hands: List of lists of card strings [['A♥', 'K♥'], ['Q♠', 'Q♦'], ...]
        board: List of card strings ['7♦', 'K♠', '6♦']

    Returns:
        List of equities for each player or None if calculation fails
    """
    if not player_hands or len(player_hands) < 2:
        return None

    # Convert all cards to eval7 format
    eval7_hands = []
    for hand in player_hands:
        if not hand or len(hand) != 2:
            return None
        eval7_hand = [card_string_to_eval7(c) for c in hand]
        if None in eval7_hand:
            return None
        eval7_hands.append(eval7_hand)

    eval7_board = [card_string_to_eval7(c) for c in board] if board else []
    if board and None in eval7_board:
        return None

    try:
        equities = eval7.py_hand_vs_range_exact(
            eval7_hands,
            eval7_board,
            iterations=10000
        )
        return equities
    except Exception:
        try:
            equities = eval7.py_hand_vs_range_monte_carlo(
                eval7_hands,
                eval7_board,
                iterations=10000
            )
            return equities
        except Exception:
            return None


def extract_hand_info(entry: str) -> Dict:
    """
    Parse a single log entry and extract relevant information.

    Args:
        entry: Log entry string

    Returns:
        Dictionary containing parsed information
    """
    info = {'type': 'unknown', 'raw': entry}

    if '-- starting hand' in entry:
        match = re.search(r'hand #(\d+) \(id: ([^\)]+)\)', entry)
        if match:
            info['type'] = 'hand_start'
            info['hand_number'] = int(match.group(1))
            info['hand_id'] = match.group(2)
        dealer_match = re.search(r'dealer: "([^"]+)"', entry)
        if dealer_match:
            info['dealer'] = dealer_match.group(1)

    elif '-- ending hand' in entry:
        match = re.search(r'hand #(\d+)', entry)
        if match:
            info['type'] = 'hand_end'
            info['hand_number'] = int(match.group(1))

    elif 'Player stacks:' in entry:
        info['type'] = 'player_stacks'
        players = re.findall(r'#(\d+) "([^"]+)" \((\d+)\)', entry)
        info['stacks'] = {player[1]: int(player[2]) for player in players}

    elif 'joined the game with a stack of' in entry:
        match = re.search(r'"([^"]+)" joined the game with a stack of (\d+)', entry)
        if match:
            info['type'] = 'player_join'
            info['player'] = match.group(1)
            info['stack'] = int(match.group(2))

    elif 'posts a small blind' in entry:
        match = re.search(r'"([^"]+)" posts a small blind of (\d+)', entry)
        if match:
            info.update({
                'type': 'small_blind',
                'player': match.group(1),
                'amount': int(match.group(2))
            })

    elif 'posts a big blind' in entry:
        match = re.search(r'"([^"]+)" posts a big blind of (\d+)', entry)
        if match:
            info.update({
                'type': 'big_blind',
                'player': match.group(1),
                'amount': int(match.group(2))
            })

    elif entry.startswith('Flop:'):
        info['type'] = 'flop'
        info['cards'] = re.findall(r'[2-9TJQKA][♠♥♦♣]', entry)

    elif entry.startswith('Turn:'):
        info['type'] = 'turn'
        info['cards'] = re.findall(r'[2-9TJQKA][♠♥♦♣]', entry)

    elif entry.startswith('River:'):
        info['type'] = 'river'
        info['cards'] = re.findall(r'[2-9TJQKA][♠♥♦♣]', entry)

    elif ' calls ' in entry:
        match = re.search(r'"([^"]+)" calls (\d+)', entry)
        if match:
            info.update({
                'type': 'call',
                'player': match.group(1),
                'amount': int(match.group(2))
            })

    elif ' bets ' in entry:
        match = re.search(r'"([^"]+)" bets (\d+)', entry)
        if match:
            info.update({
                'type': 'bet',
                'player': match.group(1),
                'amount': int(match.group(2))
            })

    elif ' raises to ' in entry:
        match = re.search(r'"([^"]+)" raises to (\d+)', entry)
        if match:
            info.update({
                'type': 'raise',
                'player': match.group(1),
                'amount': int(match.group(2))
            })

    elif ' checks' in entry:
        match = re.search(r'"([^"]+)" checks', entry)
        if match:
            info.update({'type': 'check', 'player': match.group(1)})

    elif ' folds' in entry:
        match = re.search(r'"([^"]+)" folds', entry)
        if match:
            info.update({'type': 'fold', 'player': match.group(1)})

    elif ' shows a ' in entry:
        match = re.search(r'"([^"]+)" shows a (.+)\.', entry)
        if match:
            info['type'] = 'show'
            info['player'] = match.group(1)
            info['cards'] = re.findall(r'[2-9TJQKA][♠♥♦♣]', match.group(2))

    elif ' collected ' in entry and ' from pot' in entry:
        match = re.search(r'"([^"]+)" collected (\d+) from pot', entry)
        if match:
            info.update({
                'type': 'pot_collected',
                'player': match.group(1),
                'amount': int(match.group(2))
            })
        hand_match = re.search(r'with (.+?) \(combination: ([^)]+)\)', entry)
        if hand_match:
            info['winning_hand'] = hand_match.group(1)
            info['combination'] = hand_match.group(2)

    elif 'Uncalled bet' in entry:
        match = re.search(r'Uncalled bet of (\d+) returned to "([^"]+)"', entry)
        if match:
            info.update({
                'type': 'uncalled_bet',
                'amount': int(match.group(1)),
                'player': match.group(2)
            })

    return info


def get_position(hand: Dict, player: str) -> str:
    """
    Determine player's position in the hand.

    Args:
        hand: Hand dictionary containing player information
        player: Player identifier string

    Returns:
        Position string (BTN, SB, BB, UTG, MP, CO, etc.)
    """
    players = list(hand['players'].keys())
    num_players = len(players)

    if num_players < 2:
        return 'Unknown'

    dealer = hand.get('dealer')
    if not dealer or dealer not in players:
        return 'Unknown'

    dealer_idx = players.index(dealer)
    player_idx = players.index(player) if player in players else -1

    if player_idx == -1:
        return 'Unknown'

    position_offset = (player_idx - dealer_idx) % num_players

    if num_players == 2:
        return 'BTN' if position_offset == 0 else 'BB'
    elif num_players <= 6:
        positions = ['BTN', 'SB', 'BB', 'UTG', 'MP', 'CO']
        return positions[position_offset] if position_offset < len(positions) else 'MP'
    else:
        positions = ['BTN', 'SB', 'BB', 'UTG', 'UTG+1', 'MP', 'MP+1', 'HJ', 'CO']
        return positions[position_offset] if position_offset < len(positions) else 'MP'
