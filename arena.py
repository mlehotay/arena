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
            self.effect(fighter, apply=True)

    def tick(self, fighter):
        if self.remaining_duration > 0:
            self.remaining_duration -= 1
            if self.remaining_duration == 0:
                self.effect(fighter, apply=False)
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
    deadlock_threshold = 5  # Number of turns to wait before breaking deadlock
    deadlock_counter = 0

    @staticmethod
    def take_turn(fighter):
        if fighter.health < fighter.max_health / 4:
            DefensiveAI.deadlock_counter += 1
            if DefensiveAI.deadlock_counter >= DefensiveAI.deadlock_threshold:
                DefensiveAI.deadlock_counter = 0  # Reset counter and force attack
                LowestHealthAttackAI.take_turn(fighter)
            else:
                fighter.take_defensive_action()
        else:
            DefensiveAI.deadlock_counter = 0  # Reset counter if not in defensive action
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
        self.attack_bonus = 0
        self.extra_attacks = 0
        self.damage_bonus = 0
        self.critical_chance = 0

    def __repr__(self):
        return f'{self.name} ({self.health}/{self.max_health}) [Level {self.level} {self.__class__.__name__}, {self.weapon}, {self.armor}, {self.faction}]'

    def take_turn(self):
        for buff in self.buffs:
            buff.tick(self)
        self.ai.take_turn(self)

    def attack(self, opponent):
        attack_roll = roll(1, 20) + self.attack_bonus
        target_ac = 22 - opponent.armor_class - self.level
        if attack_roll >= target_ac:
            (dice, sides, plus) = weapon_list[self.weapon]
            damage = roll(dice, sides) + plus + self.damage_bonus
            self.battle.log(f'{self.name} hits {opponent.name} for {damage} damage!')
            opponent.take_damage(damage, self)
        else:
            self.battle.log(f'{self.name} misses {opponent.name}')

    def take_damage(self, damage, attacker):
        self.battle.log(f'{attacker.name} attacks {self.name} for {damage} damage')
        self.health -= damage
        if self.health < 1:
            self.die()

    def die(self):
        self.battle.log(f'{self.name} dies!')
        self.battle.fighters.remove(self)
        self.battle = None

    def take_defensive_action(self):
        if self.armor == 'shield' and all(buff.remaining_cooldown == 0 for buff in self.buffs if buff.name == 'Shield Wall'):
            self.apply_buff(shield_wall)
        else:
            self.apply_buff(defensive_stance)

    def apply_buff(self, buff):
        buff.apply(self)
        self.buffs.append(buff)
        self.battle.log(f'{self.name} gains buff: {buff.name}')

# Define a generic buff effect function

def generic_buff_effect(attribute, value):
    def effect(fighter, apply):
        if apply:
            setattr(fighter, attribute, getattr(fighter, attribute) + value)
        else:
            setattr(fighter, attribute, getattr(fighter, attribute) - value)
    return effect

# Define specific buffs using the generic buff effect function

defensive_stance = Buff('Defensive Stance', generic_buff_effect('armor_class', 2), duration=1, cooldown=3)
shield_wall = Buff('Shield Wall', generic_buff_effect('armor_class', 4), duration=1, cooldown=4)
berserk_rage = Buff('Berserk Rage', generic_buff_effect('attack_bonus', 2), duration=3, cooldown=5)
speed_boost = Buff('Speed Boost', generic_buff_effect('extra_attacks', 1), duration=2, cooldown=4)
poison_weapon = Buff('Poison Weapon', generic_buff_effect('damage_bonus', 2), duration=3, cooldown=6)
fortify = Buff('Fortify', generic_buff_effect('max_health', 5), duration=4, cooldown=8)

# Special buff for healing over time
heal_over_time = Buff('Heal Over Time', lambda fighter, apply: setattr(fighter, 'health', min(fighter.max_health, fighter.health + 2) if apply else fighter.health), duration=3, cooldown=5)

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

    def log(self, message):
        if self.verbose:
            print(message)

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
            print(f'{faction}: {self.wins[faction] / self.iterations:.2%}')

class Game:
    def run(self):
        print('Arena version ' + VERSION)

        roles = [
            #{'name': 'Alice', 'faction': 'Order', 'level': 5, 'class': Fighter, 'weapon': 'long sword', 'armor': 'chain mail', 'ai': RandomAttackAI},
            #{'name': 'Bob', 'faction': 'Order', 'level': 4, 'class': Fighter, 'weapon': 'two-handed sword', 'armor': 'leather armor', 'ai': LowestHealthAttackAI},
            #{'name': 'Eve', 'faction': 'Chaos', 'level': 5, 'class': Fighter, 'weapon': 'flail', 'armor': 'shield', 'ai': LowestHealthAttackAI},
            #{'name': 'Mallory', 'faction': 'Chaos', 'level': 3, 'class': Fighter, 'weapon': 'mace', 'armor': 'banded mail', 'ai': RandomAttackAI},
            #{'name': 'Carol', 'faction': 'Otters', 'level': 4, 'class': Fighter, 'weapon': 'long sword', 'armor': 'chain mail', 'ai': RandomAttackAI},
            #{'name': 'Dave', 'faction': 'Otters', 'level': 4, 'class': Fighter, 'weapon': 'short sword', 'armor': 'scale mail', 'ai': LowestHealthAttackAI},
            #{'name': 'Frank', 'faction': 'Team Frank', 'level': 4, 'class': Fighter, 'weapon': 'broad sword', 'armor': 'splint mail', 'ai': DefensiveAI}
            {'name': 'Alice', 'faction': 'Red', 'level': 3, 'class': Fighter, 'weapon': 'long sword', 'armor': 'chain mail', 'ai': RandomAttackAI},
            {'name': 'Bob', 'faction': 'Blue', 'level': 3, 'class': Fighter, 'weapon': 'two-handed sword', 'armor': 'leather armor', 'ai': LowestHealthAttackAI},
        ]

        battle = Arena(roles, iterations=1, verbose=True)
        battle.simulate_battle()
        battle.print_probabilities()

#############################################################################
# start here
Game().run()
