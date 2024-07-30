# weapon.py
class Weapon:
    def __init__(self, name, damage, range=1):
        self.name = name
        self.damage = damage
        self.range = range

    def attack(self, attacker, target):
        raise NotImplementedError("This method should be overridden by subclasses")

class MeleeWeapon(Weapon):
    def __init__(self, name, damage):
        super().__init__(name, damage, range=1)

    def attack(self, attacker, target):
        if attacker.battle.map.is_adjacent(attacker.position, target.position):
            target.take_damage(self.damage, attacker)
        else:
            print(f"{attacker.name} is not adjacent to {target.name} and cannot attack with {self.name}")

class RangedWeapon(Weapon):
    def __init__(self, name, range, damage, ammunition_type, magical_effect=None):
        self.name = name
        self.range = range
        self.damage = damage
        self.ammunition_type = ammunition_type
        self.ammunition = []
        self.magical_effect = magical_effect

    def load_ammunition(self, ammo):
        if isinstance(ammo, self.ammunition_type):
            self.ammunition.append(ammo)

    def attack(self, attacker, target):
        if not self.ammunition:
            print("No ammunition loaded!")
            return False

        distance = attacker.battle.map.calculate_distance(attacker.position, target.position)
        if distance <= self.range:
            ammo = self.ammunition.pop(0)
            target.take_damage(self.damage, attacker)
            return True
        else:
            print(f"{target.name} is out of range for {self.name}")
            return False

    def fire(self, attacker, target, battlefield):
        if not self.ammunition:
            print("No ammunition loaded!")
            return False

        if not self.check_line_of_sight(attacker.position, target.position, battlefield):
            print("No clear line of sight!")
            return False

        ammo = self.ammunition.pop(0)
        self.hit(target, self.damage, ammo)
        return True

    def check_line_of_sight(self, start_pos, end_pos, battlefield):
        # Simple example assuming a clear path
        # Implement actual logic to check obstacles in `battlefield`
        return True

    def hit(self, target, damage, ammo):
        # Apply damage to target
        target.take_damage(damage)
        # Apply any magical effect if present
        if self.magical_effect:
            self.apply_magical_effect(target, self.magical_effect)

    def apply_magical_effect(self, target, effect):
        # Implement the logic for the magical effect
        pass

# Ammunition classes
class Ammunition:
    def __init__(self, name):
        self.name = name

class Arrow(Ammunition):
    def __init__(self):
        super().__init__("Arrow")

class Bolt(Ammunition):
    def __init__(self):
        super().__init__("Bolt")

class Rock(Ammunition):
    def __init__(self):
        super().__init__("Rock")

class ThrownWeapon(Ammunition):
    def __init__(self, name, damage):
        super().__init__(name)
        self.damage = damage

class Spear(ThrownWeapon):
    def __init__(self):
        super().__init__("Spear", damage=10)

class Bow(RangedWeapon):
    def __init__(self):
        super().__init__("Bow", range=10, damage=5, ammunition_type=Arrow)

class Crossbow(RangedWeapon):
    def __init__(self):
        super().__init__("Crossbow", range=8, damage=7, ammunition_type=Bolt)

class Sling(RangedWeapon):
    def __init__(self):
        super().__init__("Sling", range=5, damage=3, ammunition_type=Rock)

def resolve_ranged_attack(self, attacker, target):
    distance = self.map.calculate_distance(attacker.position, target.position)
    if attacker.ranged_weapon and attacker.ranged_weapon.ammunition:
        if distance <= attacker.ranged_weapon.range:
            ammo = attacker.ranged_weapon.ammunition.pop()
            # Implement attack logic here, e.g., reduce target's health
            print(f"{attacker.name} hits {target.name} with {ammo.name} for {attacker.ranged_weapon.damage} damage")

def resolve_throw(self, attacker, target):
    if attacker.wielded_weapon:
        attacker.throw_weapon(target)
        # Implement throw logic here, e.g., reduce target's health
        print(f"{attacker.name} throws {attacker.wielded_weapon.name} at {target.name} for {attacker.wielded_weapon.damage} damage")
