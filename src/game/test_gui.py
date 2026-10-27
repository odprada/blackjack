import pygame

from ..classes.deck import Deck
from .round import Round

WINDOW_SIZE = (520, 370)
CAPTION = "blackjack"
FPS = 30

FONT_NAMES = "menlo,consolas,dejavusansmono,couriernew"
FONT_SIZE = 18

BACKGROUND = (30, 30, 30)
TEXT_COLOR = (230, 230, 230)
BUTTON_COLOR = (80, 80, 80)
BUTTON_TEXT_COLOR = (255, 255, 255)
BUTTON_RADIUS = 8

TEXT_X = 20
TEXT_Y = 20
LINE_HEIGHT = 32

BUTTONS = {
    "hit": pygame.Rect(20, 300, 150, 50),
    "stand": pygame.Rect(185, 300, 150, 50),
    "new": pygame.Rect(350, 300, 150, 50),
}
LABELS = {"hit": "Hit (H)", "stand": "Stand (S)", "new": "New (N)"}
KEYS = {pygame.K_h: "hit", pygame.K_s: "stand", pygame.K_n: "new"}


def show(hand) -> str:
    cards = " ".join(f"{card.rank}{card.suit}" for card in hand.cards)
    return f"{cards}   value {hand.value}" + ("  (soft)" if hand.is_soft else "")


def new_round() -> Round:
    deck = Deck()
    deck.shuffle()
    return Round(deck)


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption(CAPTION)
    font = pygame.font.SysFont(FONT_NAMES, FONT_SIZE)
    clock = pygame.time.Clock()

    game_round = new_round()
    running = True

    while running:
        action = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for name, rect in BUTTONS.items():
                    if rect.collidepoint(event.pos):
                        action = name
            elif event.type == pygame.KEYDOWN:
                action = KEYS.get(event.key)

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

        screen.fill(BACKGROUND)
        for i, line in enumerate(lines):
            screen.blit(font.render(line, True, TEXT_COLOR), (TEXT_X, TEXT_Y + i * LINE_HEIGHT))
        for name, rect in BUTTONS.items():
            pygame.draw.rect(screen, BUTTON_COLOR, rect, border_radius=BUTTON_RADIUS)
            text = font.render(LABELS[name], True, BUTTON_TEXT_COLOR)
            screen.blit(text, text.get_rect(center=rect.center))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()