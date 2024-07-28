# buff.py

class Buff:
    def __init__(self, name, duration, apply_fn, tick_fn, remove_fn=None, cooldown=0):
        self.name = name
        self.duration = duration
        self.remaining_duration = duration
        self.cooldown = cooldown
        self.remaining_cooldown = cooldown  # Cooldown starts only after the buff expires
        self.apply_fn = apply_fn
        self.tick_fn = tick_fn
        self.remove_fn = remove_fn

    def apply(self, fighter):
        self.remaining_duration = self.duration  # Set duration
        self.apply_fn(fighter)

    def tick(self, fighter):
        if self.remaining_duration > 0:
            self.remaining_duration -= 1
            fighter.battle.log(f"{self.name} duration: {self.remaining_duration} for {fighter.name}")
            self.tick_fn(fighter)
            if self.remaining_duration == 0:
                self.start_cooldown(fighter)
        elif self.remaining_cooldown > 0:
            self.remaining_cooldown -= 1
            fighter.battle.log(f"{self.name} cooldown: {self.remaining_cooldown} for {fighter.name}")

    def start_cooldown(self, fighter):
        if self.remove_fn:
            self.remove_fn(fighter)
        self.remaining_cooldown = self.cooldown  # Set cooldown
        fighter.battle.log(f"Buff {self.name} expired for {fighter.name}, cooldown started")

class BuffCreator:
    @staticmethod
    def create_berserk_rage():
        def apply_fn(fighter):
            fighter.attack_bonus += 5

        def tick_fn(fighter):
            fighter.attack_bonus -= 1

        def remove_fn(fighter):
            pass  # No removal effect

        return Buff('Berserk Rage', duration=5, apply_fn=apply_fn, tick_fn=tick_fn, remove_fn=remove_fn)

    @staticmethod
    def create_defensive_stance():
        def apply_fn(fighter):
            fighter.armor_class -= 4

        def tick_fn(fighter):
            pass  # No ticking effect

        def remove_fn(fighter):
            fighter.armor_class += 4  # Remove buff effect after expiration

        return Buff('Defensive Stance', duration=1, apply_fn=apply_fn, tick_fn=tick_fn, remove_fn=remove_fn)

    @staticmethod
    def create_shield_wall():
        def apply_fn(fighter):
            fighter.armor_class -= 6

        def tick_fn(fighter):
            pass  # No ticking effect

        def remove_fn(fighter):
            fighter.armor_class += 6  # Remove buff effect after expiration

        return Buff('Shield Wall', duration=2, apply_fn=apply_fn, tick_fn=tick_fn, remove_fn=remove_fn, cooldown=5)

    @staticmethod
    def create_heal_over_time():
        def apply_fn(fighter):
            fighter.health += 5  # Heal 5 HP immediately

        def tick_fn(fighter):
            fighter.health += 5  # Heal 5 HP each turn

        def remove_fn(fighter):
            pass  # No removal effect

        return Buff('Heal Over Time', duration=3, apply_fn=apply_fn, tick_fn=tick_fn, remove_fn=remove_fn)
