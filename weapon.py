# weapon.py

weapon_list = {
    # melee weapons
    None: (1, 2, 0, 1),  # 1d2, range 1
    'axe': (1, 6, 0, 1),  # 1d6, range 1
    'battle axe': (1, 8, 0, 1),  # 1d8, range 1
    'club': (1, 6, 0, 1),
    'dagger': (1, 4, 0, 1),
    'flail': (1, 6, 1, 1),  # 1d6+1, range 1
    'hammer': (1, 4, 1, 1),
    'mace': (1, 6, 1, 1),
    'morning star': (2, 4, 0, 1),  # 2d4, range 1
    'scimitar': (1, 8, 0, 1),
    'spear': (1, 6, 0, 1),
    'quarterstaff': (1, 6, 0, 1),
    'broad sword': (2, 4, 0, 1),
    'long sword': (1, 8, 0, 1),
    'short sword': (1, 6, 0, 1),
    'trident': (1, 6, 1, 1),
    'two-handed sword': (1, 10, 0, 1),

    # ranged weapons
    'bow': (1, 6, 0, 5),  # 1d6, range 5
    'crossbow': (1, 4, 1, 5),  # 1d4+1, range 5
    'sling': (1, 4, 0, 3)  # 1d4, range 3
}

class Weapon:
    def __init__(self, name, dice, sides, addend, range=1):
        self.name = name
        self.dice = dice
        self.sides = sides
        self.addend = addend
        self.range = range

# Weapon instances for easy use
def create_weapon(name):
    if name in weapon_list:
        dice, sides, addend, range = weapon_list[name]
        return Weapon(name, dice, sides, addend, range)
    else:
        print("Weapon not found.")
        return None
