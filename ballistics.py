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

# Extended RangedWeapon class to handle magical effects
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

class Bow(RangedWeapon):
    def __init__(self):
        super().__init__("Bow", range=10, damage=5, ammunition_type=Arrow)

class Crossbow(RangedWeapon):
    def __init__(self):
        super().__init__("Crossbow", range=8, damage=7, ammunition_type=Bolt)

class Sling(RangedWeapon):
    def __init__(self):
        super().__init__("Sling", range=5, damage=3, ammunition_type=Rock)
