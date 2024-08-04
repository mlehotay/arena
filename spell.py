class Spell:
    def __init__(self, name, damage, range, effect=None):
        self.name = name
        self.damage = damage
        self.range = range
        self.effect = effect  # Additional effects like healing, debuffs, etc.

    def cast(self, caster, target):
        if caster.position.map.is_within_range(caster.position, target.position, self.range):
            target.take_damage(self.damage)
            if self.effect:
                self.effect.apply(caster, target)
        else:
            print(f"Target is out of range for spell {self.name}")

    def __repr__(self):
        return f"{self.name} (Damage: {self.damage}, Range: {self.range})"
