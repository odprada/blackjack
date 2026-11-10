import ctypes
import os
import sys
from pathlib import Path

import pygame

from ..classes.deck import Deck
from .round import MAX_PLAYERS, OUTCOMES, Round

DESIGN_W, DESIGN_H = 1440, 800

ASSETS = Path(__file__).resolve().parents[2] / "assets"
MAT_PATH = ASSETS / "mat.jpg"  # menu background
MAT_PATHS = {n: ASSETS / f"mat_{n}.jpg" for n in range(1, MAX_PLAYERS + 1)}
CARDS_DIR = ASSETS / "cards"
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

TEXT_COLOR = (230, 230, 230)
GOLD = (240, 200, 80)
GREEN = (120, 220, 130)
RED = (235, 110, 100)
GREY = (190, 190, 190)
OUTCOME_COLORS = {
    OUTCOMES["player_win"]: GREEN,
    OUTCOMES["player_blackjack"]: GOLD,
    OUTCOMES["dealer_win"]: RED,
    OUTCOMES["tie"]: GREY,
}

BUTTON_COLOR = (80, 80, 80)
BUTTON_HOVER = (105, 105, 105)
BUTTON_PRESSED = (60, 60, 60)
BUTTON_DISABLED = (52, 52, 52)
BUTTON_SHADOW = (20, 20, 20)
BUTTON_TEXT_COLOR = (255, 255, 255)
BUTTON_TEXT_DISABLED = (120, 120, 120)

DEAL_MS = 260
DEAL_STAGGER_MS = 140
FLIP_MS = 320
DEALER_PAUSE_MS = 450
DEALER_DRAW_MS = 650


class Layout:
    """
    Every pixel size in one place, scaled from the DESIGN_W x DESIGN_H design by a single factor,
    so the game looks the same on a 1080p laptop and a 2560x1600 monitor.
    """

    def __init__(self, scale: float) -> None:
        def s(value: float) -> int:
            return max(1, round(value * scale))

        self.scale = scale
        self.width, self.height = s(DESIGN_W), s(DESIGN_H)
        self.window = (self.width, self.height)
        self.center_x = self.width // 2

        self.card_size = (s(90), s(126))
        self.card_w, self.card_h = self.card_size
        self.card_step = s(72)
        self.card_radius = s(8)
        self.shadow_dx, self.shadow_dy = s(3), s(5)
        self.deck_pos = (self.width - s(150), s(40))
        self.stack_offset = s(2)

        self.dealer_label_y = s(36)
        self.dealer_y = s(72)
        self.dealer_max_width = s(900)

        self.panel_y = s(290)
        self.panel_h = s(280)
        self.panel_max_w = s(380)
        self.panel_margin = s(24)
        self.panel_pad = s(14)
        self.panel_radius = s(14)
        self.panel_border = s(3)
        self.name_dy = s(26)
        self.cards_dy = s(54)
        self.total_dy = s(26)
        self.result_dy = s(68)

        self.status_y = s(612)
        self.button_y = s(668)
        self.button_w, self.button_h, self.button_gap = s(170), s(58), s(24)
        self.button_radius = s(8)
        self.button_depth = s(4)
        self.button_press = s(2)

        self.menu_title_y, self.menu_sub_y, self.menu_hint_y = s(240), s(340), s(510)
        self.menu_button_y = s(400)
        self.menu_button_w, self.menu_button_h, self.menu_button_gap = s(200), s(70), s(36)

        self.font_size, self.font_big_size, self.font_title_size = s(24), s(34), s(76)

    def hand_positions(self, count: int, center_x: int, max_width: int) -> list[int]:
        """Left x of each card, shrinking the spacing so the row fits in max_width."""
        step = self.card_step
        if count > 1 and step * (count - 1) + self.card_w > max_width:
            step = max(1, (max_width - self.card_w) // (count - 1))
        start_x = center_x - (step * (count - 1) + self.card_w) // 2
        return [start_x + i * step for i in range(count)]


def choose_scale() -> float:
    """Largest scale at which the window fits the desktop (BLACKJACK_SCALE overrides it)."""
    override = os.environ.get("BLACKJACK_SCALE")
    if override:
        return float(override)
    info = pygame.display.Info()  # before set_mode this is the desktop size
    scale = min(info.current_w * 0.92 / DESIGN_W, info.current_h * 0.88 / DESIGN_H)
    return max(0.6, min(scale, 2.0))


def load_image(path, size) -> pygame.Surface:
    image = pygame.image.load(str(path)).convert_alpha()
    return pygame.transform.smoothscale(image, size)


def load_mat(path, size) -> pygame.Surface:
    image = pygame.image.load(str(path)).convert()
    return pygame.transform.smoothscale(image, size)


def ease_out(t: float) -> float:
    return 1 - (1 - t) ** 3


def hand_label(hand) -> str:
    if hand.is_blackjack:
        return "Blackjack"
    if hand.value > 21:
        return f"{hand.value} - Bust"
    return f"{'Soft ' if hand.is_soft else ''}{hand.value}"


class Button:
    def __init__(self, action: str, label: str, rect: pygame.Rect, layout: Layout) -> None:
        self.action = action
        self.label = label
        self.rect = rect
        self.layout = layout

    def draw(self, screen, font, mouse_pos, mouse_down, enabled: bool) -> None:
        L = self.layout
        hover = enabled and self.rect.collidepoint(mouse_pos)
        pressed = hover and mouse_down
        if not enabled:
            color, text_color = BUTTON_DISABLED, BUTTON_TEXT_DISABLED
        else:
            color = BUTTON_PRESSED if pressed else BUTTON_HOVER if hover else BUTTON_COLOR
            text_color = BUTTON_TEXT_COLOR

        pygame.draw.rect(screen, BUTTON_SHADOW, self.rect.move(0, L.button_depth),
                         border_radius=L.button_radius)
        face = self.rect.move(0, L.button_press if pressed else 0)
        pygame.draw.rect(screen, color, face, border_radius=L.button_radius)
        text = font.render(self.label, True, text_color)
        screen.blit(text, text.get_rect(center=face.center))


class Game:
    """Menu + table state, drawing and animation timing. All times are pygame ticks (ms)."""

    def __init__(self, layout: Layout) -> None:
        L = self.L = layout
        self.mat = load_mat(MAT_PATH, L.window)
        self.mats = {n: load_mat(path, L.window) for n, path in MAT_PATHS.items()}
        self.fronts = {card: load_image(path, L.card_size) for card, path in PATHS.items()}
        self.back = load_image(CARDBACK_PATH, L.card_size)
        self.shadow = pygame.Surface(L.card_size, pygame.SRCALPHA)
        pygame.draw.rect(self.shadow, (0, 0, 0, 90), self.shadow.get_rect(), border_radius=L.card_radius)

        self.font = pygame.font.SysFont(FONT_NAMES, L.font_size)
        self.font_big = pygame.font.SysFont(FONT_NAMES, L.font_big_size, bold=True)
        self.font_title = pygame.font.SysFont(FONT_NAMES, L.font_title_size, bold=True)

        self.state = "menu"
        self.num_players = 1
        self.round: Round | None = None

        self.appear: dict = {}
        self.settle_at = 0
        self.reveal_at: int | None = None
        self.dealer_ready_at = 0
        self.finished = False

        x0 = (L.width - (4 * L.button_w + 3 * L.button_gap)) // 2
        self.table_buttons = [
            Button(action, label,
                   pygame.Rect(x0 + i * (L.button_w + L.button_gap), L.button_y, L.button_w, L.button_h), L)
            for i, (action, label) in enumerate(
                [("hit", "Hit (H)"), ("stand", "Stand (S)"), ("new", "New (N)"), ("menu", "Menu (M)")]
            )
        ]
        mw, mh, mgap = L.menu_button_w, L.menu_button_h, L.menu_button_gap
        mx0 = (L.width - (MAX_PLAYERS * mw + (MAX_PLAYERS - 1) * mgap)) // 2
        self.menu_buttons = [
            Button(f"players:{n}", f"{n} player{'s' if n > 1 else ''}",
                   pygame.Rect(mx0 + (n - 1) * (mw + mgap), L.menu_button_y, mw, mh), L)
            for n in range(1, MAX_PLAYERS + 1)
        ]
        self.menu_keys = {getattr(pygame, f"K_{n}"): f"players:{n}" for n in range(1, MAX_PLAYERS + 1)}
        self.table_keys = {pygame.K_h: "hit", pygame.K_s: "stand", pygame.K_n: "new", pygame.K_m: "menu"}


    def buttons(self) -> list[Button]:
        return self.menu_buttons if self.state == "menu" else self.table_buttons

    def key_actions(self) -> dict:
        return self.menu_keys if self.state == "menu" else self.table_keys

    def enabled_actions(self) -> set[str]:
        if self.state == "menu":
            return {b.action for b in self.menu_buttons}
        actions = {"menu"}
        if not self.round.dealer_turn:
            actions |= {"hit", "stand"}
        if self.finished:
            actions.add("new")
        return actions

    def handle(self, action: str, now: int) -> None:
        if action.startswith("players:"):
            self.num_players = int(action.split(":")[1])
            self.state = "table"
            self.new_round(now)
        elif action == "menu":
            self.state = "menu"
        elif action == "new":
            self.new_round(now)
        elif action == "hit":
            self.round.hit()
        elif action == "stand":
            self.round.stand()

    def new_round(self, now: int) -> None:
        deck = Deck()
        deck.shuffle()
        self.round = Round(deck, self.num_players)

        order = []
        for i in range(2):
            for seat in self.round.seats:
                order.append(seat.hand.cards[i])
            order.append(self.round.dealer_hand.cards[i])
        self.appear = {card: now + k * DEAL_STAGGER_MS for k, card in enumerate(order)}
        self.settle_at = now + (len(order) - 1) * DEAL_STAGGER_MS + DEAL_MS
        self.reveal_at = None
        self.dealer_ready_at = 0
        self.finished = False

    def update(self, now: int) -> None:
        if self.state != "table":
            return
        r = self.round
        if r.dealer_turn and self.reveal_at is None and now >= self.settle_at:
            self.reveal_at = now
            self.dealer_ready_at = now + FLIP_MS + DEALER_PAUSE_MS
        if self.reveal_at is not None:
            if r.dealer_must_draw and now >= self.dealer_ready_at:
                r.dealer_step()
                self.dealer_ready_at = now + DEALER_DRAW_MS
            self.finished = r.is_over and now >= self.reveal_at + FLIP_MS


    def draw(self, screen, mouse_pos, mouse_down, now: int) -> None:
        if self.state == "menu":
            self._draw_menu(screen)
        else:
            self._draw_table(screen, now)
        enabled = self.enabled_actions()
        for button in self.buttons():
            button.draw(screen, self.font, mouse_pos, mouse_down, button.action in enabled)

    def _text(self, screen, font, text, color, center) -> None:
        surface = font.render(text, True, color)
        screen.blit(surface, surface.get_rect(center=center))

    def _draw_menu(self, screen) -> None:
        L = self.L
        screen.blit(self.mat, (0, 0))
        self._text(screen, self.font_title, "Blackjack", GOLD, (L.center_x, L.menu_title_y))
        self._text(screen, self.font, "How many players?", TEXT_COLOR, (L.center_x, L.menu_sub_y))
        self._text(screen, self.font, "Press 1-4 or click", GREY, (L.center_x, L.menu_hint_y))

    def _draw_hand(self, screen, hand, y, center_x, max_width, now, hide_second=False, flip_t=None) -> None:
        L = self.L
        xs = L.hand_positions(len(hand.cards), center_x, max_width)
        for i, (card, x) in enumerate(zip(hand.cards, xs)):
            started = self.appear.setdefault(card, now)
            t = (now - started) / DEAL_MS
            if t < 0:
                continue  # not dealt yet
            e = ease_out(min(t, 1))
            px = L.deck_pos[0] + (x - L.deck_pos[0]) * e
            py = L.deck_pos[1] + (y - L.deck_pos[1]) * e

            front = self.fronts[f"{card.rank}{card.suit}"]
            image = front
            if i == 1 and hide_second:
                image = self.back
            elif i == 1 and flip_t is not None and flip_t < 1:
                # horizontal squash: back shrinks to a sliver, then the front grows out
                image = self.back if flip_t < 0.5 else front
                width = max(1, int(L.card_w * abs(1 - 2 * flip_t)))
                image = pygame.transform.smoothscale(image, (width, L.card_h))
                px += (L.card_w - width) / 2

            screen.blit(self.shadow, (px + L.shadow_dx, py + L.shadow_dy))
            screen.blit(image, (px, py))

    def _draw_panel(self, screen, rect, active: bool) -> None:
        L = self.L
        surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(surface, (0, 0, 0, 80), surface.get_rect(), border_radius=L.panel_radius)
        if active:
            pygame.draw.rect(surface, GOLD, surface.get_rect(), width=L.panel_border,
                             border_radius=L.panel_radius)
        screen.blit(surface, rect.topleft)

    def _draw_table(self, screen, now: int) -> None:
        L = self.L
        r = self.round
        screen.blit(self.mats[len(r.seats)], (0, 0))

        for k in (2, 1, 0):
            screen.blit(self.back, (L.deck_pos[0] + 2 * k * L.stack_offset,
                                    L.deck_pos[1] - 2 * k * L.stack_offset))

        revealed = self.reveal_at is not None and now >= self.reveal_at + FLIP_MS
        label = "Dealer" + (f"   {hand_label(r.dealer_hand)}" if revealed else "")
        self._text(screen, self.font, label, TEXT_COLOR, (L.center_x, L.dealer_label_y))
        flip_t = None if self.reveal_at is None else (now - self.reveal_at) / FLIP_MS
        self._draw_hand(screen, r.dealer_hand, L.dealer_y, L.center_x, L.dealer_max_width, now,
                        hide_second=self.reveal_at is None, flip_t=flip_t)

        n = len(r.seats)
        col_w = L.width // n
        panel_w = min(col_w - L.panel_margin, L.panel_max_w)
        for i, seat in enumerate(r.seats):
            cx = col_w * i + col_w // 2
            panel = pygame.Rect(0, 0, panel_w, L.panel_h)
            panel.midtop = (cx, L.panel_y)
            active = r.active_seat is seat
            self._draw_panel(screen, panel, active)

            self._text(screen, self.font, seat.name, GOLD if active else TEXT_COLOR,
                       (cx, panel.top + L.name_dy))
            cards_y = panel.top + L.cards_dy
            self._draw_hand(screen, seat.hand, cards_y, cx, panel_w - 2 * L.panel_pad, now)
            self._text(screen, self.font, hand_label(seat.hand), TEXT_COLOR,
                       (cx, cards_y + L.card_h + L.total_dy))
            if self.finished:
                result = r.outcome(seat)
                self._text(screen, self.font_big, result, OUTCOME_COLORS[result],
                           (cx, cards_y + L.card_h + L.result_dy))

        if self.finished:
            status, color = "Round over - press N for a new round", TEXT_COLOR
        elif r.dealer_turn:
            status, color = "Dealer's turn", TEXT_COLOR
        else:
            status, color = f"{r.active_seat.name}'s turn", GOLD
        self._text(screen, self.font, status, color, (L.center_x, L.status_y))


def main() -> None:
    if sys.platform == "win32":
        try:  # report real pixels instead of an OS-scaled desktop size
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

    pygame.init()
    layout = Layout(choose_scale())
    screen = pygame.display.set_mode(layout.window)
    pygame.display.set_caption(CAPTION)
    clock = pygame.time.Clock()
    game = Game(layout)
    running = True

    while running:
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            action = None
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in game.buttons():
                    if button.rect.collidepoint(event.pos):
                        action = button.action
            elif event.type == pygame.KEYDOWN:
                action = game.key_actions().get(event.key)
            if action in game.enabled_actions():
                game.handle(action, now)

        game.update(now)
        game.draw(screen, pygame.mouse.get_pos(), pygame.mouse.get_pressed()[0], now)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()