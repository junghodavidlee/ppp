# Ledger-Based Profit/Loss Calculation

## Overview
The profit/loss calculation now uses the **ledger data** instead of trying to infer it from hand logs.

## Ledger Data Format
Each row in the ledger represents a session:
- `player_nickname`: Display name (e.g., "Justin", "LIT", "LIT2")
- `player_id`: Unique ID (e.g., "g0FfVCh6gI")
- `session_start_at`: When the session started
- `session_end_at`: When the session ended (blank if ongoing)
- `buy_in`: Amount bought in
- `buy_out`: Amount cashed out
- `stack`: Current stack (if session ongoing)
- `net`: Profit/loss for this session

## How Profit/Loss is Calculated

For each player (after applying ID mapping):
1. **Total Buy-In**: Sum of all `buy_in` values across all sessions
2. **Total Buy-Out**: Sum of all `buy_out` values
3. **Total Stack**: Sum of all current `stack` values (ongoing sessions)
4. **Net Profit**: Sum of all `net` values from ledger

## Player Mapping Applied
The player ID mapping (from Section 10) is still applied to merge accounts:
- "LIT" and "LIT2" are merged into "LIT"
- Multiple IDs for the same person are combined

## Example
If LIT has these ledger entries:
```
LIT2, Mw0SATaN53, ..., 183900, ..., 740047, 556147
LIT,  3jIWLYiXzx, ..., 100000, 183900, 0, 83900
```

After mapping, "LIT" will show:
- Total Buy-In: 283,900
- Net Profit: 640,047 (556,147 + 83,900)

## Benefits
✓ Accurate profit/loss from actual buy-in/cash-out records
✓ Handles ongoing sessions (where players haven't cashed out yet)
✓ No need to infer from truncated hand logs
✓ Player mapping still works correctly
