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
    Convert card string like 'A♥' or '10♥' to eval7.Card format.

    Args:
        card_str: Card string in format like 'A♥', 'K♠', '10♥', etc.

    Returns:
        eval7.Card object or None if invalid
    """
    rank_map = {
        'A': 'A', 'K': 'K', 'Q': 'Q', 'J': 'J', 'T': 'T',
        '9': '9', '8': '8', '7': '7', '6': '6', '5': '5',
        '4': '4', '3': '3', '2': '2', '10': 'T'  # Handle '10' as 'T'
    }
    suit_map = {'♠': 's', '♥': 'h', '♦': 'd', '♣': 'c'}

    if len(card_str) < 2:
        return None

    # Handle '10♥' (3 chars) vs 'A♥' (2 chars)
    if card_str[:2] == '10' and len(card_str) >= 3:
        rank = '10'
        suit = card_str[2]
    elif len(card_str) >= 2:
        rank = card_str[0]
        suit = card_str[1]
    else:
        return None

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

    # Parse rank and suit from card strings
    # Handle both '10♥' (2 char rank) and 'A♥' (1 char rank)
    def parse_card(card: str):
        if len(card) >= 2 and card[:2] == '10':
            return 'T', card[2]  # Convert '10' to 'T'
        elif len(card) >= 2:
            return card[0], card[1]
        else:
            return None, None

    card1_rank, card1_suit = parse_card(cards[0])
    card2_rank, card2_suit = parse_card(cards[1])

    if not card1_rank or not card2_rank:
        return None

    rank_order = '23456789TJQKA'

    try:
        if rank_order.index(card1_rank) >= rank_order.index(card2_rank):
            high_rank, low_rank = card1_rank, card2_rank
            suited = card1_suit == card2_suit
        else:
            high_rank, low_rank = card2_rank, card1_rank
            suited = card1_suit == card2_suit
    except ValueError:
        return None

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
        info['cards'] = re.findall(r'(?:10|[2-9TJQKA])[♠♥♦♣]', entry)

    elif entry.startswith('Turn:'):
        info['type'] = 'turn'
        info['cards'] = re.findall(r'(?:10|[2-9TJQKA])[♠♥♦♣]', entry)

    elif entry.startswith('River:'):
        info['type'] = 'river'
        info['cards'] = re.findall(r'(?:10|[2-9TJQKA])[♠♥♦♣]', entry)

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
            # Match cards: handle both '10♥' and 'A♥' formats
            info['cards'] = re.findall(r'(?:10|[2-9TJQKA])[♠♥♦♣]', match.group(2))

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

    Position naming follows standard poker conventions:
    - 8-handed: Button, Small Blind, Big Blind, UTG, UTG+1, Lojack, Hijack, Cutoff
    - 7-handed: Button, Small Blind, Big Blind, UTG, UTG+1, Hijack, Cutoff (remove Lojack)
    - 6-handed: Button, Small Blind, Big Blind, UTG, Hijack, Cutoff (remove UTG+1)
    - 5-handed: Button, Small Blind, Big Blind, UTG, Cutoff (remove Hijack)
    - 4-handed: Button, Small Blind, Big Blind, UTG (remove Cutoff)
    - 3-handed: Button, Small Blind, Big Blind (remove UTG)
    - 2-handed: Button, Big Blind (remove Small Blind, Button posts SB)

    Args:
        hand: Hand dictionary containing player information
        player: Player identifier string

    Returns:
        Position string (BTN, SB, BB, UTG, UTG+1, LJ, HJ, CO)
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

    # Calculate position relative to dealer (0 = BTN/dealer)
    position_offset = (player_idx - dealer_idx) % num_players

    # Position mapping based on player count
    # Format: position_offset -> position_name
    position_maps = {
        2: {0: 'BTN', 1: 'BB'},
        3: {0: 'BTN', 1: 'SB', 2: 'BB'},
        4: {0: 'BTN', 1: 'SB', 2: 'BB', 3: 'UTG'},
        5: {0: 'BTN', 1: 'SB', 2: 'BB', 3: 'UTG', 4: 'CO'},
        6: {0: 'BTN', 1: 'SB', 2: 'BB', 3: 'UTG', 4: 'HJ', 5: 'CO'},
        7: {0: 'BTN', 1: 'SB', 2: 'BB', 3: 'UTG', 4: 'UTG+1', 5: 'HJ', 6: 'CO'},
        8: {0: 'BTN', 1: 'SB', 2: 'BB', 3: 'UTG', 4: 'UTG+1', 5: 'LJ', 6: 'HJ', 7: 'CO'},
    }

    # For 9+ players, use 8-player mapping with additional middle positions
    if num_players >= 9:
        if position_offset == 0:
            return 'BTN'
        elif position_offset == 1:
            return 'SB'
        elif position_offset == 2:
            return 'BB'
        elif position_offset == 3:
            return 'UTG'
        elif position_offset == 4:
            return 'UTG+1'
        elif position_offset == num_players - 3:
            return 'HJ'
        elif position_offset == num_players - 2:
            return 'CO'
        else:
            # Middle positions between UTG+1 and HJ
            return 'LJ'

    # Use position map for 2-8 players
    position_map = position_maps.get(num_players, {})
    return position_map.get(position_offset, 'Unknown')
