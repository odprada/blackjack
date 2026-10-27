import pygame
from pathlib import Path
from ..classes.deck import Deck
from .round import Round

WINDOW_SIZE = (640, 480)
MAT_PATH = Path(__file__).resolve().parents[2] / "assets" / "mat.png"
CARDS_DIR = Path(__file__).resolve().parents[2] / "assets" / "cards"
CARDBACK_PATH = CARDS_DIR / "back.png"

PATHS = {
    f"{rank}{suit_symbol}": CARDS_DIR / f"{rank}{suit}.png"
    for rank in ["A", *map(str, range(2, 11)), "J", "Q", "K"]
    for suit_symbol, suit in [
        ("♠", "S"),
        ("♥", "H"),
        ("♦", "D"),
        ("♣", "C"),
    ]
}

CAPTION = "blackjack"
FPS = 60

FONT_NAMES = "menlo,consolas,dejavusansmono,couriernew"
FONT_SIZE = 22

TEXT_COLOR = (230, 230, 230)
BUTTON_COLOR = (80, 80, 80)
BUTTON_TEXT_COLOR = (255, 255, 255)
BUTTON_RADIUS = 8

CARD_SIZE = (80, 112)
CARD_W = CARD_SIZE[0]
CARD_STEP = 120
CENTER_X = 320
MAX_ROW_WIDTH = 580
DEALER_Y = 34
PLAYER_Y = 270
OUTCOME_Y = 396

BUTTONS = {
    "hit": pygame.Rect(80, 410, 150, 50),
    "stand": pygame.Rect(245, 410, 150, 50),
    "new": pygame.Rect(410, 410, 150, 50),
}

LABELS = {"hit": "Hit (H)", "stand": "Stand (S)", "new": "New (N)"}
KEYS = {pygame.K_h: "hit", pygame.K_s: "stand", pygame.K_n: "new"}


def load_image(path) -> pygame.Surface:
    image = pygame.image.load(str(path)).convert_alpha()
    return pygame.transform.smoothscale(image, CARD_SIZE)


def draw_hand(screen, hand, y, cardfront, cardback, hide_second=False) -> None:
    count = len(hand.cards)
    step = CARD_STEP
    if count > 1 and step * (count - 1) + CARD_W > MAX_ROW_WIDTH:
        step = (MAX_ROW_WIDTH - CARD_W) // (count - 1)
    start_x = CENTER_X - (step * (count - 1) + CARD_W) // 2

    for i, card in enumerate(hand.cards):
        if hide_second and i == 1:
            image = cardback
        else:
            image = cardfront[f"{card.rank}{card.suit}"]
        screen.blit(image, (start_x + i * step, y))


def new_round() -> Round:
    deck = Deck()
    deck.shuffle()
    return Round(deck)


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption(CAPTION)
    mat = pygame.image.load(str(MAT_PATH)).convert()
    font = pygame.font.SysFont(FONT_NAMES, FONT_SIZE)
    clock = pygame.time.Clock()

    cardfront = {card: load_image(path) for card, path in PATHS.items()}
    cardback = load_image(CARDBACK_PATH)

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

        screen.blit(mat, (0, 0))
        draw_hand(screen, game_round.dealer_hand, DEALER_Y, cardfront, cardback,
                  hide_second=not game_round.is_over)
        draw_hand(screen, game_round.player_hand, PLAYER_Y, cardfront, cardback)

        if game_round.outcome:
            text = font.render(game_round.outcome, True, TEXT_COLOR)
            screen.blit(text, text.get_rect(center=(CENTER_X, OUTCOME_Y)))

        for name, rect in BUTTONS.items():
            pygame.draw.rect(screen, BUTTON_COLOR, rect, border_radius=BUTTON_RADIUS)
            text = font.render(LABELS[name], True, BUTTON_TEXT_COLOR)
            screen.blit(text, text.get_rect(center=rect.center))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()