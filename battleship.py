import pygame
import random
from datetime import datetime

# --- Nustatymai ---
CELL_SIZE = 40
GRID_SIZE = 10
MARGIN = 30
SCREEN_WIDTH = CELL_SIZE * GRID_SIZE * 2 + MARGIN * 3
SCREEN_HEIGHT = CELL_SIZE * GRID_SIZE + MARGIN * 2
SHIP_SIZES = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]

# --- Spalvos ---
GRAY = (60, 60, 60)
BLUE = (0, 0, 255)
GREY = (200, 200, 200)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Laivų Mūšis")
font = pygame.font.SysFont(None, 24) #teksto šriftas


class Ship:
    def __init__(self, size, x, y, horizontal=True):
        self.size = size
        self.x = x
        self.y = y
        self.horizontal = horizontal
        self.hits = 0

    def get_cells(self):
        cells=[]
        for i in range(self.size):
            if self.horizontal:
                x = self.x + i
                y =self.y
            else:
                x= self.x
                y= self.y +i
            cells.append((x,y))
        return cells

    def is_sunk(self):
        return self.hits >= self.size

class Grid:
    def __init__(self):
        self.cells=[]
        self.ships = []
        for y in range(GRID_SIZE):
            row=[]
            for x in range(GRID_SIZE):
                row.append("~")
            self.cells.append(row)

    def can_place_ship(self, ship):
        for x, y in ship.get_cells():
            if not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE):
                return False
            if self.cells[y][x] != "~":
                return False 
            # Patikrina aplinkui
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx = x + dx
                    ny = y + dy
                    if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                        if self.cells[ny][nx] == "S":
                             return False
        return True

    def place_ship(self, ship):
        for x, y in ship.get_cells():
            self.cells[y][x] = "S"
        self.ships.append(ship)

    def receive_shot(self, x, y):
        if self.cells[y][x] == "S":
            self.cells[y][x] = "X"
            for ship in self.ships:
                if (x, y) in ship.get_cells():
                    ship.hits += 1
                    return True, ship.is_sunk()
        elif self.cells[y][x] == "~":
            self.cells[y][x] = "O"
        return False, False
    
    def all_ships_sunk(self):
        for ship in self.ships:
            if not ship.is_sunk():
                return False
        return True

    def draw(self, surf, offset_x, offset_y, hide_ships=False):
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                rect = pygame.Rect(offset_x + x * CELL_SIZE, offset_y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(surf, GREY, rect, 1)
                cell = self.cells[y][x]

                # Nuskendusių laivų žymėjimas
                is_sunk_ship_part = False
                if cell == 'X':
                    for ship in self.ships:
                         if ship.is_sunk() and (x,y) in ship.get_cells():
                             is_sunk_ship_part = True
                             break

                if is_sunk_ship_part:
                     pygame.draw.rect(surf, RED, rect.inflate(-2, -2))
                elif cell == "X":
                    pygame.draw.line(surf, RED, rect.topleft, rect.bottomright, 3)
                    pygame.draw.line(surf, RED, rect.topright, rect.bottomleft, 3)
                elif cell == "O":
                    pygame.draw.circle(surf, BLACK, rect.center, 5)
                elif cell == "S" and not hide_ships:
                    pygame.draw.rect(surf, GREEN, rect.inflate(-4, -4))


class Player:
    def __init__(self):
        self.grid = Grid()

    def take_turn(self, opponent_grid):
        raise NotImplementedError

    def place_ships(self):
         raise NotImplementedError


class HumanPlayer(Player):
    def __init__(self):
        super().__init__()
        self.placing_ships_state = {'active': True, 'current_ship_index': 0, 'horizontal': True}
        # active statusas reiškia, jog galima dėlioti laivus
    def place_ships(self, event):
        if not self.placing_ships_state['active']:
            return True # Jau yra sudėlioti laivai

        state = self.placing_ships_state
        current_ship_index = state['current_ship_index']
        horizontal = state['horizontal']

        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            state['horizontal'] = not horizontal
            print(f"Laivo kryptis pakeista į: {'Horizontali' if state['horizontal'] else 'Vertikali'}")

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            if MARGIN <= mx < MARGIN + GRID_SIZE * CELL_SIZE and MARGIN <= my < MARGIN + GRID_SIZE * CELL_SIZE:
                gx = (mx - MARGIN) // CELL_SIZE
                gy = (my - MARGIN) // CELL_SIZE
                if 0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE:
                    size = SHIP_SIZES[current_ship_index]
                    ship = Ship(size, gx, gy, horizontal)
                    if self.grid.can_place_ship(ship):
                        self.grid.place_ship(ship)
                        print(f"Padėtas {size} dydžio laivas.")
                        state['current_ship_index'] += 1
                        if state['current_ship_index'] >= len(SHIP_SIZES):
                                print("Visi laivai sudėlioti!")
                                state['active'] = False
                                return True # Dėliojimas baigtas
                        else:
                            print("Negalima padėti laivo šioje vietoje.")

    def draw_placement_indicator(self, surf):
        if not self.placing_ships_state['active']:
            return

        state = self.placing_ships_state
        current_ship_index = state['current_ship_index']
        if current_ship_index >= len(SHIP_SIZES):
              return

        size = SHIP_SIZES[current_ship_index]
        horizontal = state['horizontal']
        mx, my = pygame.mouse.get_pos()

        gx = (mx - MARGIN) // CELL_SIZE
        gy = (my - MARGIN) // CELL_SIZE

        temp_ship = Ship(size, gx, gy, horizontal)
        can_place = self.grid.can_place_ship(temp_ship)
        color = (0, 200, 0, 150) if can_place else (200, 0, 0, 150)

        s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        s.fill(color)

        for i in range(size):
            cell_x = gx + i if horizontal else gx
            cell_y = gy if horizontal else gy + i
            if 0 <= cell_x < GRID_SIZE and 0 <= cell_y < GRID_SIZE:
                rect_x = MARGIN + cell_x * CELL_SIZE
                rect_y = MARGIN + cell_y * CELL_SIZE
                surf.blit(s, (rect_x, rect_y))

    def take_turn(self, opponent_grid):
        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            opponent_grid_offset_x = MARGIN * 2 + CELL_SIZE * GRID_SIZE

            gx = (mx - opponent_grid_offset_x) // CELL_SIZE
            gy = (my - MARGIN) // CELL_SIZE

            if 0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE:
                print(f"Žmogus šauna į ({gx}, {gy})")
                return opponent_grid.receive_shot(gx, gy)
        return None

class AIPlayer(Player):
    def __init__(self):
        super().__init__()
        self.shots = set()

    def place_ships(self):
        for size in SHIP_SIZES:
            placed = False
            attempts = 0
            while not placed and attempts < 200:
                x = random.randint(0, GRID_SIZE - 1)
                y = random.randint(0, GRID_SIZE - 1)
                horizontal = random.choice([True, False])
                ship = Ship(size, x, y, horizontal)
                if self.grid.can_place_ship(ship):
                    self.grid.place_ship(ship)
                    placed = True
                attempts += 1
        print("Kompiuterio laivai sudėlioti.")
        return True

    def take_turn(self, opponent_grid):
        attempts = 0
        while attempts < GRID_SIZE * GRID_SIZE:
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if (x, y) not in self.shots:
                self.shots.add((x, y))
                print(f"AI šauna į ({x}, {y})")
                return opponent_grid.receive_shot(x, y)
            attempts += 1

# FACTORY METHOD
class PlayerFactory:

    @staticmethod
    def create_player(player_type):
     
        if player_type == "human":
            print("Kuriamas žmogaus žaidėjas...")
            return HumanPlayer()
        elif player_type == "ai":
            print("Kuriamas AI žaidėjas...")
            ai_player = AIPlayer()
            ai_player.place_ships()
            return ai_player
        else:
            raise ValueError(f"Klaidingas žaidėjo tipas: {player_type}")

def save_result(winner):
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open("results.txt", "a", encoding='utf-8') as file:
            file.write(f"{time} — {winner} laimėjo žaidimą\n")
        print(f"Rezultatas sėkmingai įrašytas: {time} - {winner}")
    except IOError as e:
        print(f"!!! Klaida rašant į results.txt: {e}")

def show_previous_results():
    try:
        with open("results.txt", "r", encoding='utf-8') as file:
            results = file.readlines()
            print("-" * 20)
            print("Ankstesni rezultatai:")
            if results:
                for line in results:
                    print(line.strip())
            else:
                print("(Kol kas įrašų nėra)")
            print("-" * 20)
    except FileNotFoundError:
        print("-" * 20)
        print("Failas results.txt nerastas. Jis bus sukurtas po pirmo žaidimo.")
        print("-" * 20)

def main():
    show_previous_results()

    human = PlayerFactory.create_player("human")
    ai = PlayerFactory.create_player("ai")

    clock = pygame.time.Clock()
    running = True
    game_state = "placing_ships" # Galimos būsenos: placing_ships, player_turn, ai_turn, game_over
    winner = None
    shot_delay = 300 # Pauzė po šūvio ms
    last_shot_time = 0 # Kada buvo paskutinis šūvis

    # Pagrindinis žaidimo ciklas
    while running:
        current_time = pygame.time.get_ticks()
        screen.fill(GRAY)

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            if game_state == "placing_ships":
                 if human.place_ships(event): # True kai baigta
                     game_state = "player_turn"
                     print("\n--- Žaidimas Prasideda ---")
                     print("Jūsų ėjimas.")

        if game_state == "player_turn":
            if current_time - last_shot_time > shot_delay:
                result = human.take_turn(ai.grid)
                if result is not None:
                    last_shot_time = current_time
                    hit, sunk = result
                    if hit:
                        print("Žmogus pataikė!")
                        if sunk: print("...ir nuskandino laivą!")
                        if ai.grid.all_ships_sunk():
                            winner = "Žaidėjas"
                            game_state = "game_over"
                            save_result(winner)
                    else:
                        print("Žmogus nepataikė.")
                        game_state = "ai_turn"
                        print("Kompiuterio ėjimas.")

        elif game_state == "ai_turn":
            if current_time - last_shot_time > shot_delay:
                result = ai.take_turn(human.grid)
                if result is not None:
                    last_shot_time = current_time
                    hit, sunk = result
                    if hit:
                        print("AI pataikė!")
                        if sunk: print("...ir nuskandino laivą!")
                        if human.grid.all_ships_sunk():
                            winner = "Kompiuteris"
                            game_state = "game_over"
                            save_result(winner)
                    else:
                        print("AI nepataikė.")
                        game_state = "player_turn"
                        print("Jūsų ėjimas.")

        # Piešimas 
        human.grid.draw(screen, MARGIN, MARGIN)
        ai.grid.draw(screen, MARGIN * 2 + CELL_SIZE * GRID_SIZE, MARGIN, hide_ships=(game_state != "game_over"))

        if game_state == "placing_ships":
             human.draw_placement_indicator(screen)
             # Tekstas
             if human.placing_ships_state['active']:
                  index = human.placing_ships_state['current_ship_index']
                  if index < len(SHIP_SIZES):
                       size = SHIP_SIZES[index]
                       direction = 'Horizontali' if human.placing_ships_state['horizontal'] else 'Vertikali'
                       place_text = font.render(f"Dėkite {size} dydžio laivą. Kryptis: {direction} (R - keisti)", True, BLACK, GREY)
                       screen.blit(place_text, (MARGIN, SCREEN_HEIGHT - MARGIN + 5))
                  else:
                       place_text = font.render("Klaida dėliojant laivus.", True, RED, GREY)
                       screen.blit(place_text, (MARGIN, SCREEN_HEIGHT - MARGIN + 5))

        if game_state == "game_over" and winner:
            text = font.render(f"{winner} laimėjo! Uždarykite langą.", True, BLACK, GREY)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, MARGIN // 2))
            screen.blit(text, text_rect)

        pygame.display.flip()

    pygame.quit()
    print("Žaidimas baigtas.")

if __name__ == "__main__":
    main()