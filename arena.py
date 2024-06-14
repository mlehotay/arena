VERSION = '0.4'

import random

weapon_list = {
    None: (1, 2, 0),  # 1d2
    'axe': (1, 6, 0),  # 1d6
    'battle axe': (1, 8, 0),  # 1d8
    'club': (1, 6, 0),
    'dagger': (1, 4, 0),
    'flail': (1, 6, 1),  # 1d6+1
    'hammer': (1, 4, 1),
    'mace': (1, 6, 1),
    'morning star': (2, 4, 0),  # 2d4
    'scimitar': (1, 8, 0),
    'spear': (1, 6, 0),
    'quarterstaff': (1, 6, 0),
    'broad sword': (2, 4, 0),
    'long sword': (1, 8, 0),
    'short sword': (1, 6, 0),
    'trident': (1, 6, 1),
    'two-handed sword': (1, 10, 0)
}

armor_list = {
    None: 0,
    'shield': 1,
    'padded armor': 2,
    'leather armor': 2,
    'studded leather': 3,
    'ring mail': 3,
    'scale mail': 4,
    'chain mail': 5,
    'splint mail': 6,
    'banded mail': 6,
    'plate mail': 7
}

def roll(dice, sides):
    return sum(random.randint(1, sides) for _ in range(dice))

class Buff:
    def __init__(self, name, effect, duration, cooldown):
        self.name = name
        self.effect = effect
        self.duration = duration
        self.cooldown = cooldown
        self.remaining_duration = 0
        self.remaining_cooldown = 0

    def apply(self, fighter):
        if self.remaining_cooldown == 0:
            self.remaining_duration = self.duration
            self.remaining_cooldown = self.cooldown

    def tick(self, fighter):
        if self.remaining_duration > 0:
            self.remaining_duration -= 1
            self.effect(fighter)
        elif self.remaining_cooldown > 0:
            self.remaining_cooldown -= 1

class RandomAttackAI:
    @staticmethod
    def take_turn(fighter):
        opponents = [f for f in fighter.battle.fighters if f.faction != fighter.faction]
        if opponents:
            target = random.choice(opponents)
            fighter.attack(target)

class LowestHealthAttackAI:
    @staticmethod
    def take_turn(fighter):
        opponents = [f for f in fighter.battle.fighters if f.faction != fighter.faction]
        if opponents:
            target = min(opponents, key=lambda f: f.health)
            fighter.attack(target)

class DefensiveAI:
    @staticmethod
    def take_turn(fighter):
        if fighter.health < fighter.max_health / 4:
            fighter.take_defensive_action()
        else:
            LowestHealthAttackAI.take_turn(fighter)

class Fighter:
    def __init__(self, name, level, faction, weapon, armor, ai):
        self.name = name
        self.level = level
        self.max_health = sum(roll(1, 10) for _ in range(level))
        self.health = self.max_health
        self.faction = faction
        self.weapon = weapon
        self.armor = armor
        self.armor_class = 10 - armor_list[self.armor]
        self.base_armor_class = self.armor_class
        self.battle = None
        self.ai = ai
        self.buffs = []

    def __repr__(self):
        return f'{self.name} ({self.health}/{self.max_health}) [Level {self.level} {self.__class__.__name__}, {self.weapon}, {self.armor}, {self.faction}]'

    def take_turn(self):
        for buff in self.buffs:
            buff.tick(self)
        self.ai.take_turn(self)

    def attack(self, opponent):
        if roll(1, 20) >= (22 - opponent.armor_class - self.level):
            (dice, sides, plus) = weapon_list[self.weapon]
            damage = roll(dice, sides) + plus
            opponent.take_damage(damage, self)
        elif self.battle.verbose:
            print(f'  {self.name} swings at {opponent.name} and misses')

    def take_damage(self, damage, attacker):
        if self.battle.verbose:
            print(f'  {attacker.name} attacks {self.name} for {damage} damage')
        self.health -= damage
        if self.health < 1:
            self.die()

    def die(self):
        if self.battle.verbose:
            print(f'  {self.name} dies!')
        self.battle.fighters.remove(self)
        self.battle = None

    def take_defensive_action(self):
        defense_buff = Buff(
            name='Defensive Stance',
            effect=lambda fighter: setattr(fighter, 'armor_class', fighter.base_armor_class + 2),
            duration=1,
            cooldown=3
        )
        defense_buff.apply(self)
        self.buffs.append(defense_buff)
        if self.battle.verbose:
            print(f'{self.name} takes a defensive action! AC is now {self.armor_class}')

class Battle:
    def __init__(self, title, roles, verbose):
        self.title = title
        self.verbose = verbose
        self.fighters = []
        self.winner = None
        self.turn = 0
        for role in roles:
            fighter = role['class'](role['name'], role['level'], role['faction'], role['weapon'], role['armor'], role['ai'])
            self.add_fighter(fighter)

    def __repr__(self):
        return f'{self.title} turn {self.turn}'

    def add_fighter(self, fighter):
        self.fighters.append(fighter)
        fighter.battle = self

    def fight_battle(self):
        if self.verbose:
            print(f'{self.title} fighters:')
            for fighter in self.fighters:
                print(fighter)
        while self.winner is None:
            self.play_round()
        if self.verbose:
            print(f'{self.winner} wins {self.title}!')
        return self.winner

    def play_round(self):
        self.turn += 1
        if self.verbose:
            print(f'{self}:')
        for f in self.fighters:
            f.take_turn()
        if len({f.faction for f in self.fighters}) == 1:
            self.winner = self.fighters[0].faction

class Arena:
    def __init__(self, roles, iterations=1000, verbose=False):
        self.roles = roles
        self.iterations = iterations
        self.verbose = verbose
        self.factions = {role['faction'] for role in roles}
        self.wins = {faction: 0 for faction in self.factions}
        self.winner = None

    def simulate_battle(self):
        for i in range(self.iterations):
            winner = Battle(f'Battle {i + 1}', self.roles, self.verbose).fight_battle()
            self.wins[winner] += 1

    def print_probabilities(self):
        print('Estimated Probabilities of Victory:')
        for faction in sorted(self.factions):
            print(f'{faction}: {self.wins[faction] / self.iterations}')

class Game:
    def run(self):
        print('Arena version ' + VERSION)

        roles = [
            {'name': 'Alice', 'faction': 'Order', 'level': 1, 'class': Fighter, 'weapon': 'long sword', 'armor': 'chain mail', 'ai': RandomAttackAI},
            {'name': 'Bob', 'faction': 'Order', 'level': 2, 'class': Fighter, 'weapon': 'two-handed sword', 'armor': 'leather armor', 'ai': LowestHealthAttackAI},
            {'name': 'Eve', 'faction': 'Chaos', 'level': 1, 'class': Fighter, 'weapon': 'flail', 'armor': 'shield', 'ai': DefensiveAI},
            {'name': 'Mallory', 'faction': 'Chaos', 'level': 2, 'class': Fighter, 'weapon': 'mace', 'armor': 'leather armor', 'ai': RandomAttackAI}
        ]

        battle = Arena(roles, iterations=1000, verbose=False)
        battle.simulate_battle()
        battle.print_probabilities()

#############################################################################
# start here
Game().run()
