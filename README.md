# Poker Analytics Toolkit

A comprehensive poker hand analysis toolkit for parsing logs, calculating statistics, and visualizing player performance.

## Quick Start

### Using the Refactored Notebook

1. Open and run [main_refactored.ipynb](main_refactored.ipynb)
2. Edit player mapping in cell 4 to merge accounts
3. View statistics, EV analysis, and range charts

### Project Structure

```
ppp/
├── poker_utils.py              # Utility functions (card parsing, positions)
├── poker_data.py               # Data loading and hand parsing classes
├── poker_stats.py              # Statistical analysis classes
├── poker_viz.py                # Visualization and reporting
├── main_refactored.ipynb       # Clean, modular notebook
├── main_v2.ipynb              # Original notebook (preserved)
├── REFACTORING_GUIDE.md       # Detailed refactoring documentation
└── data/
    ├── log/                   # Hand history CSV files
    └── ledger/                # Session ledger CSV files
```

## Features

### 1. Data Loading & Parsing
- Load multiple CSV log files
- Parse hand histories into structured format
- Player identity mapping and account merging

### 2. Player Statistics
- Net profit/loss from ledger data
- Win rates and ROI
- Hands played and won
- Session tracking

### 3. All-In EV Analysis
- Exact equity calculation using eval7
- Multi-way all-in support
- EV vs actual results comparison
- Luck variance analysis

### 4. Positional Analysis
- Performance by position (BTN, BB, CO, etc.)
- Position-specific win rates
- Investment and profit tracking

### 5. Hand Range Analysis
- 13x13 starting hand matrix
- Showdown frequency heatmaps
- Top hands display
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

# Calculate stats
stats_calc = PlayerStatistics(player_mapper)
player_stats = stats_calc.calculate_from_ledger(ledger_data, hands)
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

## Key Improvements Over Original

### Code Organization
- ✅ Modular architecture with clear separation of concerns
- ✅ Reusable functions across projects
- ✅ Easy to maintain and extend

### Code Quality
- ✅ Type hints for all functions
- ✅ Comprehensive docstrings
- ✅ Consistent naming conventions
- ✅ Error handling

### Functionality
- ✅ Object-oriented design
- ✅ Configurable data paths
- ✅ Flexible player mapping
- ✅ Clean notebook interface

### Testing & Debugging
- ✅ Testable pure functions
- ✅ Clear error messages
- ✅ Isolated components

## Documentation

- [REFACTORING_GUIDE.md](REFACTORING_GUIDE.md) - Comprehensive refactoring documentation
- Function docstrings - Use `help(function_name)` in Python

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

### Player Rankings
```
================================================================================
PLAYER PERFORMANCE RANKINGS (FROM LEDGER DATA)
================================================================================
        total_buy_in  total_buy_out  net_profit  win_rate    roi
jho          6100000      9407705.0     3307705     19.96  54.22
zxc          8607405     11729918.0     3122513     20.82  36.28
LIT          6837662      8735702.0     1898040     25.09  27.76
```

### All-In Analysis
```
   🍀 LUCKIEST (Ran Above EV): Justin
      • EV Difference: $150,000
      • Expected: $50,000
      • Actual: $200,000
      • All-ins: 15 (12 HU, 3 MW)
```

### Range Heatmap
Colorful 13x13 grid showing:
- Pocket pairs on diagonal (AA, KK, QQ...)
- Suited hands in upper triangle (AKs, KQs...)
- Offsuit hands in lower triangle (AKo, 72o...)
- Frequency counts for each hand

## Maintenance

### Adding New Features

1. **Utility function**: Add to `poker_utils.py`
2. **Data processing**: Add to `poker_data.py`
3. **Analysis**: Add to `poker_stats.py`
4. **Visualization**: Add to `poker_viz.py`

### Updating Player Mappings

Simply edit the `player_id_mapping` dictionary in the notebook and re-run the cell.

## Future Enhancements

- [ ] CLI interface for batch processing
- [ ] Database storage (SQLite/PostgreSQL)
- [ ] Web dashboard (Flask/Streamlit)
- [ ] Advanced analytics (betting patterns, hand strength)
- [ ] PDF/Excel export
- [ ] Real-time hand import
- [ ] Tournament support

## License

This project is for personal/educational use.

## Support

For questions or issues:
1. Check function docstrings with `help(function_name)`
2. Review [REFACTORING_GUIDE.md](REFACTORING_GUIDE.md)
3. Compare with original notebook for validation

---

**Version**: 1.0
**Last Updated**: 2026-01-05
**Python Version**: 3.11+