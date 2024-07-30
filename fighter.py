# fighter.py
import random
from map import *
from buff import *
from weapon import RangedWeapon, ThrownWeapon

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

# Dice rolling function
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
        self.position = None  # This will be set when the fighter is added to the map
        self.weapon = weapon
        self.ranged_weapon = None
        self.wielded_weapon = None  # For spears and other wielded weapons
        self.armor = armor
        self.shield = shield
        self.armor_class = 10 - armor_list[self.armor] - shield_list.get(self.shield, 0)
        self.battle = None
        self.ai = ai
        self.buffs = []
        self.attack_bonus = 0
        self.damage_bonus = 0

    def __repr__(self):
        ai_name = self.ai.__name__ if hasattr(self.ai, '__name__') else str(self.ai)
        return f'{self.name} ({self.health}/{self.max_health}) [Level {self.level} {self.__class__.__name__},  {ai_name}, {self.weapon}, {self.armor}, {self.faction}]'

    def is_alive(self):
        return self.health > 0

    def is_dead(self):
        return not self.is_alive()

    def take_turn(self):
        if self.is_dead():
            return # RIP
        # Tick buffs before taking turn
        for buff in self.buffs[:]:
            buff.tick(self)
        # Remove buffs that have finished cooldown
        self.buffs = [buff for buff in self.buffs if buff.remaining_cooldown > 0 or buff.remaining_duration > 0]
        self.ai.take_turn(self)

    def attack(self, opponent):
        # Check if the opponent is there and not dead
        if opponent is None or opponent.health <= 0:
            self.battle.log(f'{self.name} cannot attack because the opponent is not valid or is already dead.')
            return

        # Check if attacker and opponent are adjacent
        if not self.battle.map.is_adjacent(self.position, opponent.position):
            self.battle.log(f'{self.name} cannot attack {opponent.name} because they are not adjacent.')
            return

        attack_roll = roll(1, 20) + self.attack_bonus
        to_hit_target = 22 - opponent.armor_class - self.level

        if attack_roll >= to_hit_target:
            (dice, sides, addend) = weapon_list[self.weapon]
            damage = roll(dice, sides) + addend + self.damage_bonus
            opponent.take_damage(damage, self)
            # self.battle.log(f'{self.name} attacks {opponent.name} for {damage} damage!')
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
            berserk_rage_buff = BuffCreator.create_berserk_rage()
            last_teammate.apply_buff(berserk_rage_buff)
            self.battle.log(f'{last_teammate.name} goes into a Berserk Rage!')
        self.battle.remove_fighter(self)
        self.battle = None

    def take_defensive_action(self):
        # Check if the 'Shield Wall' buff is already active or on cooldown
        shield_wall_buff_active = any(buff.name == 'Shield Wall' and buff.remaining_cooldown == 0 for buff in self.buffs)
        if self.shield and not shield_wall_buff_active:
            self.apply_buff(BuffCreator.create_shield_wall())
        else:
            # Only apply 'Defensive Stance' if it is not already active
            defensive_stance_buff_active = any(buff.name == 'Defensive Stance' and buff.remaining_cooldown == 0 for buff in self.buffs)
            if not defensive_stance_buff_active:
                self.apply_buff(BuffCreator.create_defensive_stance())

    def apply_buff(self, buff):
        # Check if the buff is already applied or in cooldown
        for active_buff in self.buffs:
            if active_buff.name == buff.name and (active_buff.remaining_duration > 0 or active_buff.remaining_cooldown > 0):
                self.battle.log(f'{self.name} already has buff: {buff.name} with remaining duration: {active_buff.remaining_duration} or cooldown: {active_buff.remaining_cooldown}')
                return
        buff.apply(self)
        self.buffs.append(buff)
        self.battle.log(f'{self.name} gains buff: {buff.name}')

    def move_to(self, position: Position):
        if self.battle and self.position:
            if self.battle.map.is_position_occupied(position):
                self.battle.log(f"{self.name} cannot move to {position}, position is occupied.")
                return
            terrain_cost = TERRAIN_COSTS.get(position.terrain, 1)
            self.battle.map.move_fighter(self, position)
            self.battle.log(f'{self.name} moves to {position} with terrain cost {terrain_cost}')

    def equip_ranged_weapon(self, weapon):
        self.ranged_weapon = weapon

    def equip_wielded_weapon(self, weapon):
        if isinstance(weapon, ThrownWeapon):
            self.wielded_weapon = weapon

    def throw_weapon(self, target):
        if isinstance(self.wielded_weapon, ThrownWeapon):
            distance = self.battle.map.calculate_distance(self.position, target.position)
            if distance <= self.wielded_weapon.damage:  # Assuming the range is tied to damage for simplicity
                self.battle.log(f'{self.name} throws {self.wielded_weapon.name} at {target.name} for {self.wielded_weapon.damage} damage')
                target.take_damage(self.wielded_weapon.damage, self)
                self.wielded_weapon = None  # Weapon is used up

    def attack_with_ranged_weapon(self, target):
        if self.ranged_weapon and self.ranged_weapon.ammunition:
            if self.ranged_weapon.fire(self, target, self.battle.map):
                self.battle.log(f'{self.name} hits {target.name} with {self.ranged_weapon.name} for {self.ranged_weapon.damage} damage')
            else:
                self.battle.log(f'{self.name} misses {target.name} with {self.ranged_weapon.name}')
