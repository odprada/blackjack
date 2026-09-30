# Blackjack

## Rules

### Cards

* Standard 52-card deck.
* Cards 2–10 have their face value.
* J, Q, and K are worth 10.
* An Ace is worth 1 or 11, whichever gives the hand the highest value without exceeding 21 when possible.
* A hand consisting of exactly two cards — an Ace and a 10-value card — is a **Blackjack**.
* A hand exceeding 21 **busts**.
* A 21 made with three or more cards is **not** a Blackjack.

### Game Flow

1. The player is dealt two cards.
2. The dealer is dealt two cards and reveals one of them.
3. The player plays their hand(s).
4. After all player hands are finished, the dealer reveals the hidden card and plays their hand.
5. Remaining player hands are compared with the dealer's hand and bets are settled.

### Player Actions

On an eligible hand, the player may:

* **Hit** — take another card.
* **Stand** — take no more cards.
* **Double Down** — double the initial bet and take exactly one additional card. Doubling is also allowed after splitting.
* **Split** — split a pair into two separate hands by placing an additional bet.

#### Splitting

* Only cards of the same face value can be split. For example, `10 + K` cannot be split.
* A player may split up to **4 hands**.
* When splitting Aces, each resulting hand receives exactly one additional card and then automatically stands.
* A 21 obtained after splitting is not considered a Blackjack.

### Dealer Rules

* The dealer draws until reaching **17 or higher**.
* The dealer **stands on soft 17**.
* The dealer never hits, doubles, splits, or surrenders.

### Winning and Payouts

* If the dealer busts, all non-busted player hands win.
* If neither hand busts, the higher-valued hand wins.
* Equal values result in a **push**, and the original bet is returned.
* A Blackjack beats any non-Blackjack hand, including a 21 made with three or more cards.
* A player Blackjack immediately wins unless the dealer also has a Blackjack, resulting in a push.
* If the dealer has a Blackjack, all players without a Blackjack lose.
* Normal wins pay **1:1**.
* Blackjacks pay **3:2**.