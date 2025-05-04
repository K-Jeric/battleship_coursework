# Objektinio Programavimo Kursinis Darbas: Laivų Mūšis

## 1. Įvadas

### Apie ką šis projektas?

Šis projektas yra klasikinio žaidimo "Laivų Mūšis" realizacija, parašyta Python programavimo kalba, naudojant Pygame biblioteką. Programa leidžia vienam žaidėjui (žmogui) žaisti prieš kompiuterio valdomą oponentą (AI). Projektu siekiama pademonstruoti objektinio programavimo (OOP) principų taikymą žaidimų kūrimui.

Sistema palaiko šias funkcijas:

* Grafinė vartotojo sąsaja (GUI) su Pygame.
* Žmogaus valdomas laivų išdėstymas lentoje.
* Automatinis AI laivų išdėstymas.
* Ėjimais pagrįsta žaidimo logika (žmogus prieš AI).
* Šūvių registravimas (pataikyta, nepataikyta, nuskandinta).
* Žaidimo pabaigos nustatymas ir laimėtojo paskelbimas.
* Žaidimo rezultatų saugojimas tekstiniame faile results.txt.
* Ankstesnių rezultatų rodymas paleidžiant programą.

### Kaip paleisti programą?

1.  Įsitikinkite, kad turite įdiegtą Python 3.x versiją.
2.  Įdiekite Pygame biblioteką, jei jos neturite: `pip install pygame`
3.  Atsidarykite terminalą arba komandinę eilutę aplanke, kuriame yra pagrindinis programos failas (pvz., `main.py`).
4.  Paleiskite programą komanda: `python main.py`.

### Kaip naudoti programą?

1.  **Laivų Dėliojimas:**
    * Paleidus programą, kairėje pusėje matysite savo žaidimo lentą.
    * Pele spauskite ant langelių, kur norite padėti laivą (pradedant nuo viršutinio/kairiausio langelio).
    * Norėdami pasukti statomą laivą (pakeisti kryptį iš horizontalios į vertikalią ar atvirkščiai), paspauskite klaviatūros mygtuką `R`.
    * Pagal numatytuosius `SHIP_SIZES` turėsite sudėlioti visus nurodytus laivus. Programa rodys, kokio dydžio laivą šiuo metu dėliojate.
2.  **Žaidimas:**
    * Kai visi jūsų laivai bus sudėlioti, prasidės žaidimas. Jūsų ėjimas pirmas.
    * Norėdami šauti, pele spauskite ant langelio dešinėje esančioje lentoje (oponento lenta).
    * Pataikius, langelis bus pažymėtas raudonai (kryžiuku arba visa spalva, jei laivas nuskandintas). Nepataikius – juodu tašku.
    * Jei pataikote, šaunate dar kartą. Jei nepataikote, eilė pereina kompiuteriui (AI).
    * AI atliks savo ėjimą automatiškai (su nedidele pauze). Jo šūviai bus žymimi jūsų (kairėje) lentoje.
3.  **Žaidimo Pabaiga:**
    * Žaidimas baigiasi, kai vieno iš žaidėjų visi laivai yra nuskandinami.
    * Lango viršuje bus parodytas pranešimas, skelbiantis laimėtoją.
4.  **Rezultatai:**
    * Kiekvieno žaidimo pabaigoje rezultatas (laimėtojas ir laikas) įrašomas į `results.txt` failą.
    * Paleidus programą iš naujo, konsolėje bus parodyti ankstesnių žaidimų rezultatai iš šio failo.

## 2. Analizė

### OOP principų taikymas

Programoje įgyvendinti keturi pagrindiniai objektinio programavimo principai:

#### Paveldėjimas (Inheritance)

Paveldėjimas leidžia vienai klasei perimti atributus ir metodus iš kitos klasės (superklasės). Tai skatina kodo pakartotinį naudojimą.

```python
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


class AIPlayer(Player):
    def __init__(self):
        super().__init__()
        self.shots = set()
```

#### Abstrakcija (Abstraction)
Kas tai? Abstrakcija leidžia modeliuoti sudėtingas sistemas, sutelkiant dėmesį į esmines objekto savybes ir elgseną, o nereikšmingas detales paslepiant. Abstrakti klasė apibrėžia bendrus metodus, kuriuos turi įgyvendinti konkrečios klasės.

``` python
class Player:
    def __init__(self):
        self.grid = Grid()

    def take_turn(self, opponent_grid):
        raise NotImplementedError

    def place_ships(self):
         raise NotImplementedError 
```

#### Inkapsuliacija (Encapsulation)
Inkapsuliacija yra objekto vidinių duomenų (atributų) ir metodų, kurie su tais duomenimis dirba, vidinės būsenos apsaugojimas nuo tiesioginės išorinės prieigos ar modifikacijos. Prieiga prie duomenų ir jų keitimas vyksta per objekto metodus.

```python

class AIPlayer(Player):
    def __init__(self):
        super().__init__()
        self.shots = set() # Vidinė būsena - kur AI jau šovė

    # ...

    def take_turn(self, opponent_grid):
        # Metodas naudoja ir modifikuoja vidinę 'shots' būseną
        while True:
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if (x, y) not in self.shots: # Tikrina vidinę būseną
                self.shots.add((x, y)) # Modifikuoja vidinę būseną
                # ... tolesnė logika ...
                return opponent_grid.receive_shot(x, y)
```
#### Polimorfizmas (Polymorphism)
Polimorfizmas leidžia skirtingų klasių objektams reaguoti į tą patį metodo kvietimą skirtingai. Dažniausiai pasireiškia per paveldėjimą, kai poklasiai skirtingai implementuoja tą patį bazinės klasės metodą.

```python

if game_state == "player_turn":
    result = human.take_turn(ai.grid) 

elif game_state == "ai_turn":
    result = ai.take_turn(human.grid) 


if game_state == "placing_ships":
     if human.place_ships(event): 
         game_state = "player_turn"
```
### Panaudotas dizaino šablonas: Factory Method (Gamyklinis Metodas)
Factory Method yra kūrimo dizaino šablonas, kuris apibrėžia sąsają objektų kūrimui, bet leidžia poklasiams (arba, kaip šiuo atveju, pačiai gamyklos klasei) nuspręsti, kurią konkrečią klasę instancijuoti.

Tinka dėl lankstumo. Leidžia lengvai pridėti naujų žaidėjų tipų(pvz: Networkplayer, AIEasy, AINormal, AIHard), modifikuojant tik `PlayerFactory`. Nereikėtų keisti `main` funkcijos.

```python

class PlayerFactory:
    @staticmethod
    def create_player(player_type):
        if player_type == "human":
            return HumanPlayer()
        elif player_type == "ai":
            ai_player = AIPlayer()
            ai_player.place_ships()
            return ai_player
        else:
            raise ValueError(f"Klaidingas žaidėjo tipas: {player_type}")
```

### Kompozicija ir agregacija
```python

class Player:
    def __init__(self):
        self.grid = Grid() 


class Grid:
    def __init__(self):
        
        self.ships = [] 

    def place_ship(self, ship):
        
        self.ships.append(ship)
```
### Skaitymas iš failo ir rašymas į failą

Programa sąveikauja su results.txt failu:

Rašymas: Funkcija `save_result(winner)` atidaro failą `results.txt` pridėjimo režimu ("a") ir įrašo naują eilutę su žaidimo baigties laiku ir laimėtoju. Pridėjimo režimas užtikrina, kad seni įrašai nebus ištrinti.

```python

def save_result(winner):
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open("results.txt", "a", encoding='utf-8') as file: 
            file.write(f"{time} — {winner} laimėjo žaidimą\n")

```

```python

def show_previous_results():
    try:
        with open("results.txt", "r", encoding='utf-8') as file: 
            results = file.readlines()
    
    except FileNotFoundError:
        print("Failas results.txt nerastas...")
```
## Rezultatai

* Sukurta veikianti "Laivų Mūšio" žaidimo programa su grafine vartotojo sąsaja (naudojant Pygame), leidžianti žaisti žmogui prieš AI.

* Sėkmingai įgyvendinta pagrindinė žaidimo logika: laivų dėliojimas (įskaitant pasukimą), ėjimų sistema, šūvių mechanizmas, laimėtojo nustatymas.

* Pritaikius OOP principus (paveldėjimą, abstrakciją, inkapsuliaciją, polimorfizmą), kodas tapo struktūrizuotas ir lengviau suprantamas.

* Integruotas Factory Method dizaino šablonas centralizavo ir supaprastino žaidėjų objektų kūrimą.

* Įgyvendintas žaidimo rezultatų išsaugojimas faile ir jų nuskaitymas.

## Išvados

Sukurta programa yra veikiantis "Laivų Mūšio" prototipas. Pritaikyti OOP principai leido sukurti modulinę ir pakankamai lanksčią kodo struktūrą. Factory Method šablono panaudojimas išsprendė žaidėjų kūrimo problemą elegantiškai.

Ateityje programą būtų galima tobulinti:

1. Tobulinti AI: Įdiegti sudėtingesnę AI logiką.

2. Leisti vartotojui pasirinkti lentos dydį, laivų rinkinį.

3. Tinklo žaidimas: Pridėti galimybę žaisti dviem žaidėjams per tinklą.

4. Pridėti daugiau vizualinių efektų, aiškesnį žaidimo būsenos atvaizdavimą.