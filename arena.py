import random

VERSION = '0.5'

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

shield_list = {
    None: 0,
    'small shield': 1,
    'large shield': 2
}

def roll(dice, sides):
    return sum(random.randint(1, sides) for _ in range(dice))

#############################################################################
# Fighters

class Fighter:
    def __init__(self, name, level, ai, faction, weapon=None, armor=None, shield=None):
        self.name = name
        self.level = level
        self.max_health = sum(roll(1, 10) for _ in range(level))
        self.health = self.max_health
        self.faction = faction
        self.weapon = weapon
        self.armor = armor
        self.shield = shield
        self.armor_class = 10 - armor_list[self.armor] - shield_list.get(self.shield, 0)
        self.battle = None
        self.ai = ai
        self.buffs = []
        self.attack_bonus = 0
        self.extra_attacks = 0
        self.damage_bonus = 0
        self.critical_chance = 0

    def __repr__(self):
        ai_name = self.ai.__name__ if hasattr(self.ai, '__name__') else str(self.ai)
        return f'{self.name} ({self.health}/{self.max_health}) [Level {self.level} {self.__class__.__name__},  {ai_name}, {self.weapon}, {self.armor}, {self.faction}]'

    def take_turn(self):
        for buff in self.buffs:
            buff.tick(self)
        self.ai.take_turn(self)

    def attack(self, opponent):
        attack_roll = roll(1, 20) + self.attack_bonus
        target_ac = 22 - opponent.armor_class - self.level
        if attack_roll >= target_ac:
            (dice, sides, addend) = weapon_list[self.weapon]
            damage = roll(dice, sides) + addend + self.damage_bonus
            opponent.take_damage(damage, self)
        else:
            self.battle.log(f'{self.name} misses {opponent.name}')

    def take_damage(self, damage, attacker):
        self.battle.log(f'{attacker.name} attacks {self.name} for {damage} damage!')
        self.health -= damage
        if self.health < 1:
            self.die()

    def die(self):
        self.battle.log(f'{self.name} dies!')
        teammates = [f for f in self.battle.fighters if f.faction == self.faction and f != self]
        if len(teammates) == 1:
            last_teammate = teammates[0]
            berserk_rage_buff = BuffManager.create_berserk_rage()
            last_teammate.apply_buff(berserk_rage_buff)
            self.battle.log(f'{last_teammate.name} goes into Berserk Rage!')
        self.battle.fighters.remove(self)
        self.battle = None

    def take_defensive_action(self):
        # Check if the 'Shield Wall' buff is already active or on cooldown
        shield_wall_buff_active = any(buff.name == 'Shield Wall' and buff.remaining_cooldown == 0 for buff in self.buffs)
        if self.shield and not shield_wall_buff_active:
            self.apply_buff(BuffManager.create_shield_wall())
        else:
            # Only apply 'Defensive Stance' if it is not already active
            defensive_stance_buff_active = any(buff.name == 'Defensive Stance' and buff.remaining_cooldown == 0 for buff in self.buffs)
            if not defensive_stance_buff_active:
                self.apply_buff(BuffManager.create_defensive_stance())

    def apply_buff(self, buff):
        # Check if the buff is already applied or in cooldown
        for active_buff in self.buffs:
            if active_buff.name == buff.name and active_buff.remaining_cooldown > 0:
                self.battle.log(f'{self.name} already has buff: {buff.name}')
                return
        buff.apply(self)
        self.buffs.append(buff)
        self.battle.log(f'{self.name} gains buff: {buff.name}')

class Battle:
    def __init__(self, title, roles, verbose):
        self.title = title
        self.verbose = verbose
        self.fighters = []
        self.winner = None
        self.turn = 0
        self.logs = []

        for role in roles:
            fighter = role['class'](role['name'], role['level'], role['ai'], role['faction'], role['weapon'], role['armor'], role['shield'])
            self.add_fighter(fighter)

    def __repr__(self):
        return f'{self.title} turn {self.turn}'

    def add_fighter(self, fighter):
        self.fighters.append(fighter)
        fighter.battle = self

    def fight_battle(self):
        self.log(f'{self.title} fighters:')
        for fighter in self.fighters:
            self.log(fighter)
        while self.winner is None:
            self.play_round()
        self.log(f'{self.winner} wins {self.title}!')
        return self.winner

    def play_round(self):
        self.turn += 1
        self.log(f'{self}:')
        for f in self.fighters:
            f.take_turn()
        if len({f.faction for f in self.fighters}) == 1:
            self.winner = self.fighters[0].faction

    def log(self, message):
        self.logs.append(message)
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

#############################################################################
# AI

class AI:
    @staticmethod
    def take_turn(fighter):
        raise NotImplementedError

class RandomAttackAI(AI):
    @staticmethod
    def take_turn(fighter):
        opponents = [f for f in fighter.battle.fighters if f.faction != fighter.faction]
        if opponents:
            target = random.choice(opponents)
            fighter.attack(target)

class LowestHealthAI(AI):
    @staticmethod
    def take_turn(fighter):
        opponents = [f for f in fighter.battle.fighters if f.faction != fighter.faction]
        if opponents:
            target = min(opponents, key=lambda x: x.health)
            fighter.attack(target)

class GreatestThreatAI(AI):
    @staticmethod
    def take_turn(fighter):
        opponents = [f for f in fighter.battle.fighters if f.faction != fighter.faction]
        if opponents:
            target = max(opponents, key=lambda x: GreatestThreatAI.calculate_threat(x))
            fighter.attack(target)

    @staticmethod
    def calculate_threat(opponent):
        if opponent.weapon in weapon_list:
            dice, sides, addend = weapon_list[opponent.weapon]
            average_roll = dice * (1 + sides) / 2
            return average_roll + addend + opponent.damage_bonus
        return 0

class DefensiveAI(AI):
    deadlock_threshold = 5  # Number of turns to wait before breaking deadlock
    deadlock_counter = 0

    @staticmethod
    def take_turn(fighter):
        if fighter.health < fighter.max_health / 4:
            DefensiveAI.deadlock_counter += 1
            if DefensiveAI.deadlock_counter >= DefensiveAI.deadlock_threshold:
                DefensiveAI.deadlock_counter = 0  # Reset counter and force attack
                GreatestThreatAI.take_turn(fighter)
            else:
                fighter.take_defensive_action()
        else:
            DefensiveAI.deadlock_counter = 0  # Reset counter if not in defensive action
            GreatestThreatAI.take_turn(fighter)

#############################################################################
# Buffs

class Buff:
    def __init__(self, name, attribute, value, duration, cooldown, dynamic_function=None):
        self.name = name
        self.attribute = attribute
        self.value = value
        self.duration = duration
        self.cooldown = cooldown
        self.remaining_duration = 0
        self.remaining_cooldown = 0
        self.dynamic_function = dynamic_function

    def apply(self, fighter):
        if self.remaining_cooldown == 0:
            fighter.battle.log(f"Applying buff {self.name} to {fighter.name}")
            self.remaining_duration = self.duration
            self.remaining_cooldown = self.cooldown
            self._effect(fighter, apply=True)

    def tick(self, fighter):
        if self.remaining_duration > 0:
            self.remaining_duration -= 1
            fighter.battle.log(f"{self.name} duration: {self.remaining_duration} for {fighter.name}")
            if self.remaining_duration == 0:
                self._effect(fighter, apply=False)
                fighter.battle.log(f"Buff {self.name} expired for {fighter.name}")
        elif self.remaining_cooldown > 0:
            self.remaining_cooldown -= 1
            fighter.battle.log(f"{self.name} cooldown: {self.remaining_cooldown} for {fighter.name}")

    def _effect(self, fighter, apply):
        if self.dynamic_function:
            self.dynamic_function(fighter, apply)
        else:
            if apply:
                setattr(fighter, self.attribute, getattr(fighter, self.attribute) + self.value)
            else:
                setattr(fighter, self.attribute, getattr(fighter, self.attribute) - self.value)

class BuffManager:
    @staticmethod
    def create_defensive_stance():
        return Buff('Defensive Stance', 'armor_class', -2, duration=3, cooldown=5)

    @staticmethod
    def create_shield_wall():
        return Buff('Shield Wall', 'armor_class', -4, duration=3, cooldown=5)

    @staticmethod
    def create_berserk_rage():
        def berserk_rage_effect(fighter, apply):
            current_value = 3
            decrement = 1
            if apply:
                fighter.attack_bonus += current_value
            else:
                fighter.attack_bonus -= current_value
                current_value = max(0, current_value - decrement)

        return Buff('Berserk Rage', None, None, duration=3, cooldown=5, dynamic_function=berserk_rage_effect)

    @staticmethod
    def create_heal_over_time():
        def heal_over_time_effect(fighter, apply):
            if apply:
                fighter.health = min(fighter.max_health, fighter.health + 2)

        return Buff('Heal Over Time', 'health', 2, duration=3, cooldown=5, dynamic_function=heal_over_time_effect)

#############################################################################
# start here

class Game:
    def run(self):
        print('Arena version ' + VERSION)

        roles = [
            {'name': 'Glenda', 'faction': 'Red', 'level': 6, 'class': Fighter, 'weapon': 'long sword', 'armor': 'chain mail', 'shield': None, 'ai': GreatestThreatAI},
            {'name': 'Hiro', 'faction': 'Blue', 'level': 3, 'class': Fighter, 'weapon': 'two-handed sword', 'armor': 'leather armor', 'shield': None, 'ai': LowestHealthAI},
            {'name': 'Alice', 'faction': 'Blue', 'level': 4, 'class': Fighter, 'weapon': 'trident', 'armor': 'ring mail', 'shield': 'small shield', 'ai': DefensiveAI},
        ]

        battle = Arena(roles, iterations=1, verbose=True)
        battle.simulate_battle()
        battle.print_probabilities()

Game().run()
