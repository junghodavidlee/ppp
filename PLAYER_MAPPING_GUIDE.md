# Player Identity Mapping Guide

## Problem
Your friend John (and potentially others) uses multiple usernames/player IDs across different sessions:
- Sometimes appears as "LIT"
- Sometimes appears as "LIT2"
- Both should be counted as the same person for analytics

## Solution
A centralized player ID mapping system that merges multiple accounts into a single player identity.

## How It Works

### Location
The player mapping is in **Section 10** of `main_v2.ipynb` ("Player Identity Mapping")

### The Mapping Dictionary

```python
player_id_mapping = {
    # LIT (sometimes appears as LIT or LIT2)
    "3jIWLYiXzx": "LIT",
    "thyyJUIpI9": "LIT",
    "Mw0SATaN53": "LIT",

    # zxc
    "u341hEhZ9E": "zxc",
    "uaMcxyz0Rj": "zxc",
    "cIaXP7lyE_": "zxc",

    # black
    "e2LT3dd3Tx": "black",
    "eLlYR19TDN": "black",

    # sh
    "xpbZinNQx9": "sh",
    "Ek559oOV8c": "sh",

    # 9292
    "xswHkyUXqL": "9292",

    # jho
    "t3NhL8TnYz": "jho",

    # Justin
    "g0FfVCh6gI": "Justin",
}
```

## Your 7 Known Players
1. **jho**
2. **Justin**
3. **black**
4. **zxc**
5. **9292**
6. **sh**
7. **LIT** (merges LIT and LIT2)

## How to Use

### Step 1: Run Section 10
Open `main_v2.ipynb` in VSCode and run the cell in Section 10. It will show you all unique player IDs found in your data.

### Step 2: Identify Unknown IDs
The output will look like:
```
📋 ALL UNIQUE PLAYER IDs FOUND:
ID                   | Username
----------------------------------------
Ek559oOV8c           | 9917.
xpbZinNQx9           | 9917..
...
```

### Step 3: Update the Mapping
If you see new player IDs that aren't mapped:
1. Edit the `player_id_mapping` dictionary in Section 10
2. Add the new ID and assign it to one of your 7 players
3. Example: `"new_id_here": "LIT"`

### Step 4: Re-run the Notebook
After updating the mapping:
1. Re-run Section 10 to apply changes
2. Re-run Section 4 onwards to regenerate statistics with merged accounts

## What Gets Merged

When you map multiple IDs to the same player name, the system automatically merges:
- Hands played
- Hands won
- Total invested
- Total winnings
- Net profit
- Win rates
- All other statistics

## Example Output

After running Section 10, you'll see:
```
🔗 MERGED ACCOUNTS (multiple IDs → same username):
   LIT: 3jIWLYiXzx, thyyJUIpI9, Mw0SATaN53
   zxc: u341hEhZ9E, uaMcxyz0Rj, cIaXP7lyE_
   black: e2LT3dd3Tx, eLlYR19TDN
   sh: xpbZinNQx9, Ek559oOV8c
```

This confirms that multiple IDs are being combined correctly.

## Benefits

1. **Accurate Statistics**: All of LIT's hands (whether logged as "LIT" or "LIT2") count toward a single player
2. **Easy Maintenance**: Add new IDs as they appear in the data
3. **Fixed Player Count**: You always have exactly 7 players in your analytics
4. **Automatic Application**: Once mapped, all downstream analyses use the unified names

## Troubleshooting

### If a player appears twice in the results
- Check that all their IDs are mapped to the exact same name (case-sensitive!)
- Re-run Section 10 and verify the merge was successful

### If you see unknown players
- Run Section 10 to see all IDs
- Determine which of your 7 players each ID belongs to
- Add the mapping to `player_id_mapping`

### To add a new player ID
Just add a line to the dictionary:
```python
"new_player_id": "LIT",  # or whichever player this ID belongs to
```

Then re-run from Section 10 onwards.
