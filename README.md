# Poker Analytics Toolkit

A comprehensive poker hand analysis toolkit for parsing logs, calculating statistics, and visualizing player performance. Features include player statistics, all-in EV analysis, positional analysis, advanced playing style metrics (VPIP, PFR, 3bet%, cbet%, etc.), and hand range visualization.

## Quick Start

### Using the Analysis Notebook

1. Open and run [main_v3.ipynb](main_v3.ipynb)
2. Edit player mapping in Section 3 to merge accounts
3. Configure analysis settings in Section 2
4. View comprehensive statistics, EV analysis, and range charts

### Project Structure

```
ppp/
├── poker_utils.py              # Utility functions (card parsing, positions, equity)
├── poker_data.py               # Data loading and hand parsing classes
├── poker_stats.py              # Statistical analysis classes
├── poker_advanced_stats.py     # Advanced statistics (VPIP, PFR, cbet%, etc.)
├── poker_viz.py                # Visualization and reporting
├── main_v3.ipynb               # Main analysis notebook
└── data/
    ├── log/                    # Hand history CSV files
    └── ledger/                 # Session ledger CSV files
```

## Features

### 1. Data Loading & Parsing
- Load multiple CSV log and ledger files
- Parse hand histories into structured format with detailed action tracking
- Player identity mapping and account merging

### 2. Player Statistics
- Net profit/loss from ledger data
- Session-based win rates and performance
- Biggest wins and losses
- Hands played and session tracking

### 3. Advanced Playing Style Statistics
- **Preflop**: VPIP, PFR, 3bet%, 4bet%, Call vs 3bet%
- **Flop**: Cbet%, Fold to Cbet%, Cbet after 3bet%, Check after 3bet%
- **Turn**: Turn Cbet% (Double Barrel), Fold to Turn Cbet%
- **Advanced Plays**: Donk Bet%, Bet when Checked To%, Check Raise%, WTSD%
- Excludes heads-up hands for more accurate multi-way statistics

### 4. All-In EV Analysis
- Exact equity calculation using eval7 library
- Multi-way all-in support (3+ players)
- EV vs actual results comparison
- Luck variance analysis with detailed insights

### 5. Positional Analysis
- Performance by position (BTN, BB, SB, CO, UTG, MP, etc.)
- Position-specific win rates
- Investment and profit tracking per position

### 6. Hand Range Analysis
- 13x13 starting hand matrix visualization
- Showdown frequency heatmaps
- Color-coded intensity maps
- Suited vs offsuit breakdown

## Installation

### Requirements

```bash
pip install pandas numpy matplotlib eval7
```

### Optional for Development
```bash
pip install jupyter notebook
```

## Usage Examples

### Import Modules

```python
from poker_data import PokerDataLoader, HandParser, PlayerMapper
from poker_stats import PlayerStatistics, AllInAnalyzer, RangeAnalyzer
from poker_advanced_stats import DetailedHandAnalyzer
from poker_viz import RangeVisualizer, StatisticsReporter
```

### Load and Parse Data

```python
# Load data
loader = PokerDataLoader(data_dir='data/log', ledger_dir='data/ledger')
raw_data = loader.load_log_data()
ledger_data = loader.load_ledger_data()

# Parse hands
hands = HandParser.parse_hands(raw_data)
```

### Calculate Statistics

```python
# Set up player mapping
player_id_mapping = {"id1": "Player1", "id2": "Player1"}  # Merge accounts
player_mapper = PlayerMapper(player_id_mapping)
player_mapper.build_mapping(all_player_ids)

# Calculate basic stats
stats_calc = PlayerStatistics(player_mapper)
player_stats = stats_calc.calculate_from_sessions(ledger_data)

# Calculate advanced statistics
detailed_analyzer = DetailedHandAnalyzer(player_mapper)
detailed_hands = detailed_analyzer.parse_hands_with_actions(raw_data)
advanced_stats = detailed_analyzer.calculate_advanced_stats(detailed_hands)
```

### Analyze All-Ins

```python
# All-in EV analysis
allin_analyzer = AllInAnalyzer(player_mapper)
allin_df = allin_analyzer.analyze_allin_ev(hands)
```

### Visualize Ranges

```python
# Range analysis
range_analyzer = RangeAnalyzer(player_mapper)
player_ranges = range_analyzer.collect_showdown_ranges(hands)
hand_matrix, ranks = RangeAnalyzer.create_hand_matrix()

# Generate heatmap
RangeVisualizer.plot_hand_range_heatmap(
    "PlayerName",
    player_ranges["PlayerName"],
    hand_matrix,
    ranks
)
```

## Code Architecture

### Design Principles
- **Modular Architecture**: Clear separation of concerns across modules
- **Object-Oriented Design**: Reusable classes for different analysis types
- **Type Safety**: Type hints throughout for better IDE support
- **Comprehensive Documentation**: Detailed docstrings for all public functions

### Module Responsibilities
- `poker_utils.py`: Pure utility functions (parsing, conversions, equity calculations)
- `poker_data.py`: Data loading and initial hand parsing
- `poker_stats.py`: Core statistical calculations (sessions, all-in EV, ranges)
- `poker_advanced_stats.py`: Detailed action tracking and advanced metrics
- `poker_viz.py`: Visualization and formatted reporting

## Documentation

- Function docstrings - Use `help(function_name)` in Python
- Inline code comments for complex logic
- This README for high-level overview

## Player Mapping

Edit the player mapping dictionary to merge multiple accounts:

```python
player_id_mapping = {
    "3jIWLYiXzx": "LIT",
    "thyyJUIpI9": "LIT",    # Same player, different session
    "Mw0SATaN53": "LIT",    # Same player, different device

    "g0FfVCh6gI": "Justin",
    # Add more mappings...
}
```

## Output Examples

### Player Performance Summary
```
================================================================================
PLAYER PERFORMANCE SUMMARY
================================================================================
Player       Net Profit Sessions   Wins Losses    Win%  Biggest Win  Biggest Loss
--------------------------------------------------------------------------------
jho           4,068,662       15     11      4   73.3%    2,061,944    -1,300,000
LIT           2,578,197       15      9      6   60.0%      950,000      -600,200
zxc           2,472,513       16     11      5   68.8%    1,165,150      -671,250
```

### All-In EV Analysis
```
♠️ ALL-IN EV ANALYSIS (Exact Multi-Way Equity)
   🍀 LUCKIEST (Ran Above EV): Player1
      • EV Difference: $150,000
      • Expected: $50,000
      • Actual: $200,000
      • All-ins: 15 (12 HU, 3 MW)
```

### Advanced Statistics
```
📊 PREFLOP STATISTICS
        Hands  VPIP%  PFR%  3bet%  4bet%  Call vs 3bet%
Player1  2634   65.4  22.2    8.9    4.9           89.3
Player2  2333   59.0  21.9    5.0    8.7           85.2
```

### Range Heatmap
Interactive 13x13 grid visualization showing:
- **Pocket pairs** on diagonal (AA, KK, QQ, etc.)
- **Suited hands** in upper triangle (AKs, KQs, etc.)
- **Offsuit hands** in lower triangle (AKo, 72o, etc.)
- **Frequency counts** for each hand shown at showdown
- **Color intensity** indicates how often each hand is played

## Maintenance

### Adding New Features

1. **Utility function** (parsing, calculations): Add to `poker_utils.py`
2. **Data loading/processing**: Add to `poker_data.py`
3. **Basic statistics**: Add to `poker_stats.py`
4. **Advanced statistics** (action-based): Add to `poker_advanced_stats.py`
5. **Visualization/reporting**: Add to `poker_viz.py`

### Updating Player Mappings

Edit the `player_id_mapping` dictionary in [main_v3.ipynb](main_v3.ipynb) Section 3 (cell 9) and re-run the cell.

### Configuring Analysis

Edit the configuration variables in [main_v3.ipynb](main_v3.ipynb) Section 2 (cell 2):
- `PLAYER`: Default player for analysis
- `POSITIONAL_PLAYER`: Player for positional analysis
- `ALLIN_PLAYER`: Player for all-in EV analysis
- `RANGE_CHART_PLAYER`: Player for range visualization

## Future Enhancements

- [ ] CLI interface for batch processing
- [ ] Database storage (SQLite/PostgreSQL) for larger datasets
- [ ] Web dashboard (Flask/Streamlit) for interactive analysis
- [ ] Additional advanced metrics (aggression factor, fold to 3bet%, etc.)
- [ ] Betting pattern analysis and hand strength modeling
- [ ] PDF/Excel export functionality
- [ ] Real-time hand import and live tracking
- [ ] Tournament support (ICM calculations, bubble factors)
- [ ] Player tendency reports and leak detection
- [ ] Historical trend analysis over time

## License

This project is for personal/educational use.

## Support

For questions or issues:
1. Check function docstrings with `help(function_name)` in Python
2. Review the code comments and module documentation
3. Inspect the notebook cells for usage examples

---

**Version**: 2.0
**Last Updated**: 2026-01-06
**Python Version**: 3.11+
**Key Dependencies**: pandas, numpy, matplotlib, eval7