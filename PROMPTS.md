## Prompts

### 1. Ace value handling (provided by Claude)

* Asked Claude to provide a solution for handling the cases where the A cards should have value 1, i.e., when having the ace as 11 would bust the hand. The solution provided handles these cases affecting only the value of the hand, and leaving the card's attributes intact. Aditionally, it included an attribute "is_soft" obtained from the same evaluations, which tells us whether we have any soft aces (and hence a soft hand), that is, any aces with value 11.

```python
def _evaluate(self) -> tuple[int, bool]:
        total = sum(c.cardvalue for c in self.cards)
        soft_aces = sum(1 for c in self.cards if c.rank == 'A')
        while total > 21 and soft_aces > 0:
            total -= 10
            soft_aces -= 1
        return total, soft_aces > 0