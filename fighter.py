import random
from map import *
from buff import *
from weapon import *

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
        self.weapon = create_weapon(weapon)
        self.armor = armor
        self.shield = shield
        self.armor_class = 10 - armor_list.get(self.armor, 0) - shield_list.get(self.shield, 0)
        self.battle = None
        self.ai = ai
        self.buffs = []
        self.attack_bonus = 0
        self.damage_bonus = 0

    def __repr__(self):
        ai_name = self.ai.__class__.__name__ if hasattr(self.ai, '__class__') else str(self.ai)
        weapon_name = self.weapon.name if self.weapon else 'None'
        return f'{self.name} ({self.health}/{self.max_health}) [Level {self.level} {self.__class__.__name__}, {ai_name}, {weapon_name}, {self.armor}, {self.faction}]'

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
        if opponent is None or opponent.health <= 0:
            self.battle.log(f'{self.name} cannot attack because the opponent is not valid or is already dead.')
            return

        if self.weapon is None:
            self.battle.log(f'{self.name} has no weapon to attack with.')
            return

        if not self.battle.map.is_within_range(self.position, opponent.position, self.weapon.range):
            self.battle.log(f'{self.name} cannot attack {opponent.name} because they are out of range.')
            return

        attack_roll = roll(1, 20) + self.attack_bonus
        to_hit_target = 22 - opponent.armor_class - self.level

        if attack_roll >= to_hit_target:
            damage_dice = self.weapon.dice
            damage_size = self.weapon.sides
            bonus_damage = self.weapon.addend
            damage = roll(damage_dice, damage_size) + bonus_damage + self.damage_bonus
            opponent.take_damage(damage, self)
            self.battle.log(f'{self.name} attacks {opponent.name} with {self.weapon.name} for {damage} damage!')
        else:
            self.battle.log(f'{self.name} misses {opponent.name}')

    def take_damage(self, damage, attacker):
        self.battle.log(f'{attacker.name} attacks {self.name} for {damage} damage!')
        self.health -= damage
        if self.health <= 0:
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
        shield_wall_buff_active = any(buff.name == 'Shield Wall' and buff.remaining_cooldown == 0 for buff in self.buffs)
        if self.shield and not shield_wall_buff_active:
            self.apply_buff(BuffCreator.create_shield_wall())
        else:
            defensive_stance_buff_active = any(buff.name == 'Defensive Stance' and buff.remaining_cooldown == 0 for buff in self.buffs)
            if not defensive_stance_buff_active:
                self.apply_buff(BuffCreator.create_defensive_stance())

    def apply_buff(self, buff):
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
