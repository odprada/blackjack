# Blackjack

A Blackjack game with a graphical interface, built with Python and [pygame-ce](https://github.com/pygame-community/pygame-ce), the community edition of pygame. One to four players sit at the same table and play against the dealer.

## Getting Started

### Requirements

* Python 3.10 or newer (developed and tested with Python 3.14)
* pygame-ce (the community fork of pygame; it is still imported as `pygame`)

### Installation

```bash
git clone https://github.com/odprada/blackjack.git
cd blackjack

python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

pip install pygame-ce
```

Install `pygame-ce` only. Having the original `pygame` installed next to it can cause conflicts, since both provide the same `pygame` module.

### Running the game

Run this from the repository root:

```bash
python run_main.py
```

The window opens on a menu. Choose how many players (1–4) will sit at the table, and the first round is dealt.

### Controls

| Key | Action |
|-----|--------|
| `1`–`4` | Choose the number of players (menu) |
| `H` | Hit |
| `S` | Stand |
| `N` | New round (once the current round is over) |
| `M` | Back to the menu |

Every action also has an on-screen button that you can click.

The window size adapts to your screen. To set the scale yourself, set the `BLACKJACK_SCALE` environment variable, for example `BLACKJACK_SCALE=1.2 python run_main.py`.

## Rules

### Cards

* Standard 52-card deck.
* Cards 2–10 have their face value.
* J, Q, and K are worth 10.
* An Ace is worth 1 or 11, whichever gives the hand the highest value without exceeding 21 when possible.
* A hand consisting of an Ace and a 10-value card is a **Blackjack**.
* A hand exceeding 21 **busts**.
* A 21 made with three or more cards is **not** a Blackjack.

### Game Flow

1. Each player (1 to 4 can sit at the table) is dealt two cards.
2. The dealer is dealt two cards and reveals one of them.
3. The players play their hands one after another.
4. After all players are finished, the dealer reveals the hidden card and plays their hand.
5. Each player's hand is compared with the dealer's hand and the result is shown.

### Player Actions

On their turn, a player may:

* **Hit** — take another card.
* **Stand** — take no more cards.

A player whose hand reaches 21 or busts is finished automatically.

### Dealer Rules

* The dealer draws until reaching **17 or higher**.
* The dealer **stands on soft 17**.
* The dealer has no choices to make: they only draw according to these rules.

### Winning

* If the dealer busts, all non-busted player hands win.
* If neither hand busts, the higher-valued hand wins.
* Equal values result in a **push** (shown as a tie).
* A Blackjack beats any non-Blackjack hand, including a 21 made with three or more cards.
* A player Blackjack wins unless the dealer also has a Blackjack, resulting in a push.
* If the dealer has a Blackjack, all players without a Blackjack lose.

Each hand ends with one of four results: "You win!", "Blackjack!", "Dealer wins" or "Tie". There is no betting, so no payouts are calculated.
