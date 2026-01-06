"""Advanced poker statistics module.

Calculates comprehensive playing style statistics with detailed action tracking:

Preflop Metrics:
    - VPIP (Voluntarily Put money In Pot): % of hands where player invests voluntarily
    - PFR (PreFlop Raise): % of hands where player raises preflop
    - 3bet%: % of times player 3-bets when facing a raise
    - 4bet%: % of times player 4-bets when facing a 3-bet
    - Call vs 3bet%: % of times player calls a 3-bet

Flop Metrics:
    - Cbet% (Continuation Bet): % of times preflop raiser bets on flop
    - Fold to Cbet%: % of times player folds to a continuation bet
    - Cbet after 3bet%: % of times 3-bettor continues betting on flop
    - Check after 3bet%: % of times 3-bettor checks on flop

Turn Metrics:
    - Turn Cbet% (Double Barrel): % of times player continues betting on turn after flop cbet
    - Fold to Turn Cbet%: % of times player folds to a turn continuation bet

Advanced Play Metrics:
    - Donk Bet%: % of times player bets into preflop raiser
    - Bet when Checked To%: % of times player bets after aggressor checks
    - Check Raise%: % of times player check-raises
    - WTSD% (Went To ShowDown): % of hands that go to showdown

Note: By default, heads-up (2-player) hands are excluded to provide more meaningful
      multi-way statistics. This can be configured in the analysis functions.
"""

import pandas as pd
from typing import List, Dict
from collections import defaultdict


class AdvancedPlayerStatistics:
    """Calculate advanced poker statistics for each player."""

    def __init__(self, player_mapper):
        """
        Initialize advanced statistics calculator.

        Args:
            player_mapper: PlayerMapper instance for ID resolution
        """
        self.player_mapper = player_mapper

    def calculate_all_stats(self, hands: List[Dict]) -> pd.DataFrame:
        """
        Calculate all advanced statistics for all players.

        Args:
            hands: List of hand dictionaries

        Returns:
            DataFrame with all statistics per player
        """
        player_stats = defaultdict(lambda: {
            'hands_played': 0,
            'vpip_count': 0,
            'pfr_count': 0,
            'faced_raise_count': 0,
            'threebets': 0,
            'pfr_opportunities': 0,
            'cbet_opportunities': 0,
            'cbets_made': 0,
            'faced_cbet_count': 0,
            'folded_to_cbet': 0,
            'showdown_count': 0
        })

        for hand in hands:
            self._analyze_hand(hand, player_stats)

        # Calculate percentages
        results = []
        for player, stats in player_stats.items():
            hands_played = stats['hands_played']

            if hands_played == 0:
                continue

            vpip = (stats['vpip_count'] / hands_played * 100) if hands_played > 0 else 0
            pfr = (stats['pfr_count'] / hands_played * 100) if hands_played > 0 else 0
            threebets = (stats['threebets'] / stats['faced_raise_count'] * 100) if stats['faced_raise_count'] > 0 else 0
            cbet = (stats['cbets_made'] / stats['cbet_opportunities'] * 100) if stats['cbet_opportunities'] > 0 else 0
            fold_to_cbet = (stats['folded_to_cbet'] / stats['faced_cbet_count'] * 100) if stats['faced_cbet_count'] > 0 else 0
            wtsd = (stats['showdown_count'] / hands_played * 100) if hands_played > 0 else 0

            results.append({
                'player': player,
                'hands': hands_played,
                'vpip': round(vpip, 1),
                'pfr': round(pfr, 1),
                'threebets': round(threebets, 1),
                'cbet': round(cbet, 1),
                'fold_to_cbet': round(fold_to_cbet, 1),
                'wtsd': round(wtsd, 1),
                # Raw counts for reference
                'vpip_count': stats['vpip_count'],
                'pfr_count': stats['pfr_count'],
                'threebets_count': stats['threebets'],
                'faced_raise': stats['faced_raise_count'],
                'cbet_opps': stats['cbet_opportunities'],
                'cbets_made_count': stats['cbets_made'],
                'faced_cbet': stats['faced_cbet_count'],
                'folded_cbet': stats['folded_to_cbet']
            })

        df = pd.DataFrame(results)
        if len(df) > 0:
            df = df.sort_values('hands', ascending=False)

        return df

    def _analyze_hand(self, hand: Dict, player_stats: Dict):
        """
        Analyze a single hand and update statistics.

        Args:
            hand: Hand dictionary
            player_stats: Dictionary to update with statistics
        """
        players = list(hand['players'].keys())
        unified_players = {p: self.player_mapper.get_unified_name(p) for p in players}

        # Track hand participation for each player
        for player in players:
            unified = unified_players[player]
            player_stats[unified]['hands_played'] += 1

        # Analyze preflop actions
        preflop_actions = self._get_preflop_actions(hand)
        self._analyze_preflop(preflop_actions, unified_players, player_stats)

        # Analyze postflop for cbet
        postflop_actions = self._get_postflop_actions(hand)
        pfr_players = self._get_pfr_players(preflop_actions, unified_players)
        self._analyze_cbets(postflop_actions, pfr_players, unified_players, player_stats)

        # Check for showdown
        self._analyze_showdown(hand, unified_players, player_stats)

    def _get_preflop_actions(self, hand: Dict) -> List[Dict]:
        """Extract all preflop actions from hand actions."""
        preflop_actions = []

        # In the absence of explicit action tracking, we need to parse from the raw data
        # For now, we'll use a simplified approach based on hand structure
        # This would need to be enhanced based on actual hand action data structure

        return preflop_actions

    def _get_postflop_actions(self, hand: Dict) -> List[Dict]:
        """Extract all postflop actions (flop, turn, river) from hand actions."""
        postflop_actions = []

        return postflop_actions

    def _analyze_preflop(self, preflop_actions: List[Dict], unified_players: Dict, player_stats: Dict):
        """
        Analyze preflop actions for VPIP, PFR, and 3bet%.

        This is a simplified version - full implementation would require
        tracking all actions in the hand parsing phase.
        """
        # This would be implemented with full action tracking
        pass

    def _analyze_cbets(self, postflop_actions: List[Dict], pfr_players: set,
                      unified_players: Dict, player_stats: Dict):
        """
        Analyze continuation bets.

        Args:
            postflop_actions: List of postflop action dictionaries
            pfr_players: Set of players who raised preflop
            unified_players: Mapping of player IDs to unified names
            player_stats: Statistics dictionary to update
        """
        # This would be implemented with full action tracking
        pass

    def _get_pfr_players(self, preflop_actions: List[Dict], unified_players: Dict) -> set:
        """Get set of players who raised preflop."""
        pfr_players = set()
        # Would track based on preflop actions
        return pfr_players

    def _analyze_showdown(self, hand: Dict, unified_players: Dict, player_stats: Dict):
        """Check if players went to showdown."""
        for player, data in hand['players'].items():
            if data.get('hole_cards'):  # Player showed cards
                unified = unified_players[player]
                player_stats[unified]['showdown_count'] += 1


class DetailedHandAnalyzer:
    """Enhanced hand parser that tracks all actions for advanced statistics."""

    def __init__(self, player_mapper):
        """
        Initialize detailed hand analyzer.

        Args:
            player_mapper: PlayerMapper instance for ID resolution
        """
        self.player_mapper = player_mapper

    def parse_hands_with_actions(self, data: pd.DataFrame) -> List[Dict]:
        """
        Parse hands with detailed action tracking.

        Args:
            data: DataFrame containing log entries

        Returns:
            List of hand dictionaries with detailed actions
        """
        from poker_utils import extract_hand_info

        hands = []
        current_hand = None
        current_street = 'preflop'

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
                    'players': {},
                    'board': [],
                    'pot': 0,
                    'winner': None,
                    'winning_hand': None,
                    'preflop_actions': [],
                    'flop_actions': [],
                    'turn_actions': [],
                    'river_actions': []
                }
                current_street = 'preflop'

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
                            'invested': 0,
                            'hole_cards': None
                        }

                # Track street changes
                if info['type'] == 'flop':
                    current_street = 'flop'
                    current_hand['board'] = info['cards']
                elif info['type'] == 'turn':
                    current_street = 'turn'
                    current_hand['board'] = info['cards']
                elif info['type'] == 'river':
                    current_street = 'river'
                    current_hand['board'] = info['cards']

                # Track actions
                if info['type'] in ['small_blind', 'big_blind', 'call', 'bet', 'raise', 'check', 'fold']:
                    action = {
                        'player': info.get('player'),
                        'action_type': info['type'],
                        'amount': info.get('amount', 0),
                        'timestamp': info['timestamp']
                    }

                    # Add to appropriate street
                    if current_street == 'preflop':
                        current_hand['preflop_actions'].append(action)
                    elif current_street == 'flop':
                        current_hand['flop_actions'].append(action)
                    elif current_street == 'turn':
                        current_hand['turn_actions'].append(action)
                    elif current_street == 'river':
                        current_hand['river_actions'].append(action)

                    # Track investment
                    player = info.get('player')
                    amount = info.get('amount', 0)
                    if player and player in current_hand['players']:
                        current_hand['players'][player]['invested'] = \
                            current_hand['players'][player].get('invested', 0) + amount

                # Track showdowns
                if info['type'] == 'show':
                    player = info['player']
                    if player in current_hand['players']:
                        current_hand['players'][player]['hole_cards'] = info['cards']

                # Track pot and winner
                if info['type'] == 'pot_collected':
                    current_hand['winner'] = info['player']
                    current_hand['pot'] = info['amount']
                    current_hand['winning_hand'] = info.get('winning_hand')

        return hands

    def calculate_advanced_stats(self, hands: List[Dict], exclude_heads_up: bool = True) -> pd.DataFrame:
        """
        Calculate advanced statistics from detailed hand data.

        Args:
            hands: List of hand dictionaries with action tracking
            exclude_heads_up: If True, exclude hands with only 2 players (default: True)

        Returns:
            DataFrame with advanced statistics per player
        """
        player_stats = defaultdict(lambda: {
            'hands_played': 0,
            'flop_hands': 0,
            'turn_hands': 0,
            'vpip_count': 0,
            'pfr_count': 0,
            'faced_raise_count': 0,
            'threebets': 0,
            'faced_3bet_count': 0,
            'fourbets': 0,
            'called_3bet': 0,
            'cbet_opportunities': 0,
            'cbets_made': 0,
            'faced_cbet_count': 0,
            'folded_to_cbet': 0,
            'turn_cbet_opportunities': 0,
            'turn_cbets_made': 0,
            'faced_turn_cbet_count': 0,
            'folded_to_turn_cbet': 0,
            'threebetpot_opportunities': 0,
            'cbet_after_3bet_made': 0,
            'check_after_3bet_made': 0,
            'donk_bet_opportunities': 0,
            'donk_bets_made': 0,
            'pfr_checked_to_opportunities': 0,
            'pfr_checked_to_bets': 0,
            'check_raise_opportunities': 0,
            'check_raises_made': 0,
            'showdown_count': 0
        })

        # Filter hands if needed
        filtered_hands = []
        heads_up_count = 0

        for hand in hands:
            num_players = len(hand['players'])

            if exclude_heads_up and num_players == 2:
                heads_up_count += 1
                continue

            filtered_hands.append(hand)

        if exclude_heads_up and heads_up_count > 0:
            print(f"   Excluded {heads_up_count:,} heads-up hands (only 2 players)")
            print(f"   Analyzing {len(filtered_hands):,} hands with 3+ players")

        for hand in filtered_hands:
            players = list(hand['players'].keys())
            unified_players = {p: self.player_mapper.get_unified_name(p) for p in players}

            # Track hands played
            for player in players:
                unified = unified_players[player]
                player_stats[unified]['hands_played'] += 1

            # Analyze preflop
            self._analyze_preflop_detailed(hand, unified_players, player_stats)

            # Analyze postflop (cbets)
            self._analyze_postflop_detailed(hand, unified_players, player_stats)

            # Check showdown
            for player, data in hand['players'].items():
                if data.get('hole_cards'):
                    unified = unified_players[player]
                    player_stats[unified]['showdown_count'] += 1

        # Calculate percentages
        results = []
        for player, stats in player_stats.items():
            hands_played = stats['hands_played']

            if hands_played == 0:
                continue

            vpip = (stats['vpip_count'] / hands_played * 100) if hands_played > 0 else 0
            pfr = (stats['pfr_count'] / hands_played * 100) if hands_played > 0 else 0
            threebets = (stats['threebets'] / stats['faced_raise_count'] * 100) if stats['faced_raise_count'] > 0 else 0
            fourbets = (stats['fourbets'] / stats['faced_3bet_count'] * 100) if stats['faced_3bet_count'] > 0 else 0
            call_vs_3bet = (stats['called_3bet'] / stats['faced_3bet_count'] * 100) if stats['faced_3bet_count'] > 0 else 0
            cbet = (stats['cbets_made'] / stats['cbet_opportunities'] * 100) if stats['cbet_opportunities'] > 0 else 0
            fold_to_cbet = (stats['folded_to_cbet'] / stats['faced_cbet_count'] * 100) if stats['faced_cbet_count'] > 0 else 0
            turn_cbet = (stats['turn_cbets_made'] / stats['turn_cbet_opportunities'] * 100) if stats['turn_cbet_opportunities'] > 0 else 0
            fold_to_turn_cbet = (stats['folded_to_turn_cbet'] / stats['faced_turn_cbet_count'] * 100) if stats['faced_turn_cbet_count'] > 0 else 0
            cbet_after_3bet = (stats['cbet_after_3bet_made'] / stats['threebetpot_opportunities'] * 100) if stats['threebetpot_opportunities'] > 0 else 0
            check_after_3bet = (stats['check_after_3bet_made'] / stats['threebetpot_opportunities'] * 100) if stats['threebetpot_opportunities'] > 0 else 0
            donk_bet = (stats['donk_bets_made'] / stats['donk_bet_opportunities'] * 100) if stats['donk_bet_opportunities'] > 0 else 0
            bet_when_checked_to = (stats['pfr_checked_to_bets'] / stats['pfr_checked_to_opportunities'] * 100) if stats['pfr_checked_to_opportunities'] > 0 else 0
            check_raise = (stats['check_raises_made'] / stats['check_raise_opportunities'] * 100) if stats['check_raise_opportunities'] > 0 else 0
            wtsd = (stats['showdown_count'] / hands_played * 100) if hands_played > 0 else 0

            results.append({
                'player': player,
                'hands': hands_played,
                'flop_hands': stats['flop_hands'],
                'turn_hands': stats['turn_hands'],
                'vpip': round(vpip, 1),
                'pfr': round(pfr, 1),
                'threebets': round(threebets, 1),
                'fourbets': round(fourbets, 1),
                'call_vs_3bet': round(call_vs_3bet, 1),
                'cbet': round(cbet, 1),
                'fold_to_cbet': round(fold_to_cbet, 1),
                'turn_cbet': round(turn_cbet, 1),
                'fold_to_turn_cbet': round(fold_to_turn_cbet, 1),
                'cbet_after_3bet': round(cbet_after_3bet, 1),
                'check_after_3bet': round(check_after_3bet, 1),
                'donk_bet': round(donk_bet, 1),
                'bet_when_checked_to': round(bet_when_checked_to, 1),
                'check_raise': round(check_raise, 1),
                'wtsd': round(wtsd, 1)
            })

        df = pd.DataFrame(results)
        if len(df) > 0:
            df = df.sort_values('hands', ascending=False).set_index('player')

        return df

    def _analyze_preflop_detailed(self, hand: Dict, unified_players: Dict, player_stats: Dict):
        """Analyze preflop actions for VPIP, PFR, 3bet%, and 4bet%."""
        preflop_actions = hand['preflop_actions']

        # Track which players have voluntarily put money in
        players_invested = set()
        first_raiser = None
        players_facing_raise = set()
        three_bettors = set()
        players_facing_3bet = set()
        four_bettors = set()
        players_called_3bet = set()

        # Count raises to determine 3bet vs 4bet
        raise_count = 0

        # Process each action
        for action in preflop_actions:
            player = action['player']
            action_type = action['action_type']

            if not player:
                continue

            # VPIP: any voluntary action that puts money in (not BB, not SB unless they call/raise)
            if action_type in ['call', 'bet', 'raise']:
                players_invested.add(player)

            # Track raises for PFR, 3bet, 4bet
            if action_type == 'raise':
                raise_count += 1

                if raise_count == 1:
                    # First raise (PFR)
                    first_raiser = player
                    # Mark all players who acted before this as facing a raise
                    for prev_action in preflop_actions:
                        if prev_action == action:
                            break
                        prev_player = prev_action['player']
                        if prev_player and prev_player != player:
                            players_facing_raise.add(prev_player)
                elif raise_count == 2:
                    # This is a 3bet
                    players_facing_raise.add(player)
                    three_bettors.add(player)
                    # The original raiser now faces a 3bet
                    if first_raiser:
                        players_facing_3bet.add(first_raiser)
                elif raise_count == 3:
                    # This is a 4bet
                    players_facing_3bet.add(player)
                    four_bettors.add(player)
                elif raise_count > 3:
                    # 5bet or higher - track as facing 3bet
                    players_facing_3bet.add(player)

            # Track who called the raise (facing raise opportunity)
            if action_type == 'call':
                if raise_count == 1:
                    players_facing_raise.add(player)
                elif raise_count == 2:
                    # Calling a 3bet
                    players_facing_3bet.add(player)
                    players_called_3bet.add(player)

        # Update stats
        for player in hand['players'].keys():
            unified = unified_players[player]

            # VPIP
            if player in players_invested:
                player_stats[unified]['vpip_count'] += 1

            # PFR
            if player == first_raiser:
                player_stats[unified]['pfr_count'] += 1

            # 3bet opportunities and 3bets
            if player in players_facing_raise:
                player_stats[unified]['faced_raise_count'] += 1
                if player in three_bettors:
                    player_stats[unified]['threebets'] += 1

            # 4bet opportunities and 4bets
            if player in players_facing_3bet:
                player_stats[unified]['faced_3bet_count'] += 1
                if player in four_bettors:
                    player_stats[unified]['fourbets'] += 1
                if player in players_called_3bet:
                    player_stats[unified]['called_3bet'] += 1

    def _analyze_postflop_detailed(self, hand: Dict, unified_players: Dict, player_stats: Dict):
        """Analyze postflop actions for cbet, turn cbet, cbet after 3bet, check after 3bet, donk bet, check raise, etc."""
        # Find preflop raiser and check if there was a 3bet
        pfr_player = None
        three_bettor = None
        raise_count = 0

        for action in hand['preflop_actions']:
            if action['action_type'] == 'raise':
                raise_count += 1
                if raise_count == 1:
                    pfr_player = action['player']
                elif raise_count == 2:
                    three_bettor = action['player']

        # Determine who has cbet opportunities (3-bettor if exists, otherwise PFR)
        aggressor = three_bettor if three_bettor else pfr_player
        is_3bet_pot = three_bettor is not None

        if not hand['flop_actions']:
            return

        # Track flop hands for all players who saw the flop
        for player in hand['players'].keys():
            if player in [a['player'] for a in hand['flop_actions']]:
                unified = unified_players.get(player)
                if unified:
                    player_stats[unified]['flop_hands'] += 1

        # FLOP ANALYSIS
        flop_first_actor = None
        flop_first_action_type = None
        flop_first_bettor = None
        flop_cbet_made = False
        players_checked = set()
        players_who_bet_after_check = set()

        for i, action in enumerate(hand['flop_actions']):
            player = action['player']
            action_type = action['action_type']

            if not player:
                continue

            # Track first action
            if flop_first_actor is None:
                flop_first_actor = player
                flop_first_action_type = action_type

            # Track checks
            if action_type == 'check':
                players_checked.add(player)

            # Track first bet
            if action_type in ['bet', 'raise'] and flop_first_bettor is None:
                flop_first_bettor = player

                # Check if this is a donk bet (someone other than aggressor bets first)
                if aggressor and player != aggressor:
                    unified = unified_players.get(player)
                    if unified:
                        player_stats[unified]['donk_bet_opportunities'] += 1
                        player_stats[unified]['donk_bets_made'] += 1

                break

        # Track cbet opportunities for aggressor
        if aggressor:
            unified_aggressor = unified_players.get(aggressor)
            if unified_aggressor and aggressor in [a['player'] for a in hand['flop_actions']]:
                # If aggressor bet first on flop, it's a cbet
                if aggressor == flop_first_bettor:
                    if is_3bet_pot:
                        player_stats[unified_aggressor]['threebetpot_opportunities'] += 1
                        player_stats[unified_aggressor]['cbet_after_3bet_made'] += 1
                    else:
                        player_stats[unified_aggressor]['cbet_opportunities'] += 1
                        player_stats[unified_aggressor]['cbets_made'] += 1

                    flop_cbet_made = True

                    # Track who faced the cbet
                    cbet_action_found = False
                    for action in hand['flop_actions']:
                        if not cbet_action_found:
                            if action['player'] == aggressor and action['action_type'] in ['bet', 'raise']:
                                cbet_action_found = True
                            continue

                        player = action['player']
                        if not player or player == aggressor:
                            continue

                        unified = unified_players[player]
                        action_type = action['action_type']

                        # This player faced the cbet
                        player_stats[unified]['faced_cbet_count'] += 1

                        # Did they fold?
                        if action_type == 'fold':
                            player_stats[unified]['folded_to_cbet'] += 1

                        break  # Only count first action after cbet

                # If aggressor checked first in 3bet pot
                elif flop_first_actor == aggressor and flop_first_action_type == 'check' and is_3bet_pot:
                    player_stats[unified_aggressor]['threebetpot_opportunities'] += 1
                    player_stats[unified_aggressor]['check_after_3bet_made'] += 1

                # If aggressor didn't bet first but is still in hand
                elif aggressor != flop_first_bettor:
                    if is_3bet_pot:
                        player_stats[unified_aggressor]['threebetpot_opportunities'] += 1
                        # Also check if they checked
                        if aggressor in players_checked:
                            player_stats[unified_aggressor]['check_after_3bet_made'] += 1
                    else:
                        player_stats[unified_aggressor]['cbet_opportunities'] += 1

        # Track donk bet opportunities for non-aggressors
        if aggressor:
            for player in hand['players'].keys():
                if player != aggressor and player in [a['player'] for a in hand['flop_actions']]:
                    unified = unified_players.get(player)
                    if unified:
                        player_stats[unified]['donk_bet_opportunities'] += 1

        # Track "Bet when Checked To" opportunities for non-aggressors
        # This happens when the aggressor checks and a non-aggressor acts after
        if aggressor and aggressor in players_checked:
            # Aggressor checked, now check if any non-aggressors had opportunity to bet
            for player in hand['players'].keys():
                if player != aggressor and player in [a['player'] for a in hand['flop_actions']]:
                    unified = unified_players.get(player)
                    if unified:
                        # Check if this player acted after the aggressor checked
                        aggressor_checked = False
                        player_acted_after_check = False

                        for action in hand['flop_actions']:
                            if action['player'] == aggressor and action['action_type'] == 'check':
                                aggressor_checked = True
                            elif aggressor_checked and action['player'] == player:
                                player_acted_after_check = True
                                player_stats[unified]['pfr_checked_to_opportunities'] += 1

                                # Check if they bet
                                if action['action_type'] in ['bet', 'raise']:
                                    player_stats[unified]['pfr_checked_to_bets'] += 1
                                break

        # Check raise analysis
        for i, action in enumerate(hand['flop_actions']):
            player = action['player']
            action_type = action['action_type']

            if not player:
                continue

            if action_type == 'check':
                unified = unified_players.get(player)
                if unified:
                    # Look ahead to see if this player raises after someone bets
                    checked = True
                    for j in range(i + 1, len(hand['flop_actions'])):
                        next_action = hand['flop_actions'][j]
                        if next_action['player'] == player:
                            player_stats[unified]['check_raise_opportunities'] += 1
                            if next_action['action_type'] == 'raise':
                                player_stats[unified]['check_raises_made'] += 1
                            break

        # TURN CBET (DOUBLE BARREL) ANALYSIS
        if flop_cbet_made and hand['turn_actions']:
            # Track turn hands for all players who saw the turn
            for player in hand['players'].keys():
                if player in [a['player'] for a in hand['turn_actions']]:
                    unified = unified_players.get(player)
                    if unified:
                        player_stats[unified]['turn_hands'] += 1

            turn_first_aggressor = None

            for action in hand['turn_actions']:
                player = action['player']
                action_type = action['action_type']

                if action_type in ['bet', 'raise']:
                    turn_first_aggressor = player
                    break

            # If same aggressor bet first on turn, it's a turn cbet (double barrel)
            if aggressor == turn_first_aggressor:
                unified_aggressor = unified_players.get(aggressor)
                if unified_aggressor:
                    player_stats[unified_aggressor]['turn_cbet_opportunities'] += 1
                    player_stats[unified_aggressor]['turn_cbets_made'] += 1

                    # Track who faced the turn cbet
                    turn_cbet_action_found = False
                    for action in hand['turn_actions']:
                        if not turn_cbet_action_found:
                            if action['player'] == aggressor and action['action_type'] in ['bet', 'raise']:
                                turn_cbet_action_found = True
                            continue

                        player = action['player']
                        if not player or player == aggressor:
                            continue

                        unified = unified_players[player]
                        action_type = action['action_type']

                        # This player faced the turn cbet
                        player_stats[unified]['faced_turn_cbet_count'] += 1

                        # Did they fold?
                        if action_type == 'fold':
                            player_stats[unified]['folded_to_turn_cbet'] += 1

                        break  # Only count first action after turn cbet

            elif aggressor and aggressor in [a['player'] for a in hand['turn_actions']]:
                # Aggressor was in the hand but didn't bet first on turn - missed opportunity
                unified_aggressor = unified_players.get(aggressor)
                if unified_aggressor:
                    player_stats[unified_aggressor]['turn_cbet_opportunities'] += 1
