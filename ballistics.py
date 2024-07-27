# ballistics.py
from fighter import Fighter

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

class RangedWeapon:
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

class Bow(RangedWeapon):
    def __init__(self):
        super().__init__("Bow", range=10, damage=5, ammunition_type=Arrow)

class Crossbow(RangedWeapon):
    def __init__(self):
        super().__init__("Crossbow", range=8, damage=7, ammunition_type=Bolt)

class Sling(RangedWeapon):
    def __init__(self):
        super().__init__("Sling", range=5, damage=3, ammunition_type=Rock)

# Test the setup
# Create some ammunition
arrow = Arrow()
bolt = Bolt()
rock = Rock()
spear = Spear()

# Create ranged weapons
bow = Bow()
crossbow = Crossbow()
sling = Sling()

# Load ammunition
bow.load_ammunition(arrow)     # Should work
crossbow.load_ammunition(bolt) # Should work
sling.load_ammunition(rock)    # Should work
bow.load_ammunition(bolt)      # Should not work, different ammo type

# Display the ammunition loaded in each weapon
print(f"Bow ammunition: {[ammo.name for ammo in bow.ammunition]}")
print(f"Crossbow ammunition: {[ammo.name for ammo in crossbow.ammunition]}")
print(f"Sling ammunition: {[ammo.name for ammo in sling.ammunition]}")

# Test loading thrown weapon
sling.load_ammunition(spear) # Should not work, different ammo type
print(f"Sling ammunition after trying to load spear: {[ammo.name for ammo in sling.ammunition]}")
