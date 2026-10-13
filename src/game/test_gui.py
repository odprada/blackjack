import pygame

from ..classes.deck import Deck
from .round import Round


def show(hand) -> str:
    cards = " ".join(f"{card.rank}{card.suit}" for card in hand.cards)
    return f"{cards}   value {hand.value}" + ("  (soft)" if hand.is_soft else "")


def new_round() -> Round:
    deck = Deck()
    deck.shuffle()
    return Round(deck)


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((520, 370))
    pygame.display.set_caption("blackjack")
    font = pygame.font.SysFont("menlo,consolas,dejavusansmono,couriernew", 22)
    clock = pygame.time.Clock()

    buttons = {
        "hit": pygame.Rect(20, 300, 150, 50),
        "stand": pygame.Rect(185, 300, 150, 50),
        "new": pygame.Rect(350, 300, 150, 50),
    }
    labels = {"hit": "Hit (H)", "stand": "Stand (S)", "new": "New (N)"}
    keys = {pygame.K_h: "hit", pygame.K_s: "stand", pygame.K_n: "new"}

    game_round = new_round()
    running = True

    while running:
        action = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for name, rect in buttons.items():
                    if rect.collidepoint(event.pos):
                        action = name
            elif event.type == pygame.KEYDOWN:
                action = keys.get(event.key)

        if action == "hit":
            game_round.hit()
        elif action == "stand":
            game_round.stand()
        elif action == "new":
            game_round = new_round()

        lines = [
            f"Dealer: {show(game_round.dealer_hand)}",
            f"Player: {show(game_round.player_hand)}",
            "",
            f"player_stood : {game_round.player_stood}",
            f"player_bust  : {game_round.player_bust}",
            f"is_over      : {game_round.is_over}",
            f"outcome      : {game_round.outcome}",
            f"cards in deck: {len(game_round.deck)}",
        ]

        screen.fill((30, 30, 30))
        for i, line in enumerate(lines):
            screen.blit(font.render(line, True, (230, 230, 230)), (20, 20 + i * 32))
        for name, rect in buttons.items():
            pygame.draw.rect(screen, (80, 80, 80), rect, border_radius=8)
            text = font.render(labels[name], True, (255, 255, 255))
            screen.blit(text, text.get_rect(center=rect.center))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()