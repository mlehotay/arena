# test_buff.py
import unittest
from buff import Buff, BuffCreator
from fighter import Fighter
from map import Map, Position


class TestBuffs(unittest.TestCase):
    def setUp(self):
        test_roles = [
            {'name': 'Alice', 'faction': 'Order', 'level': 5, 'class': Fighter, 'ai': RandomAttackAI, 'weapon': 'long sword', 'armor': 'chain mail', 'shield': 'small shield'},
            {'name': 'Bob', 'faction': 'Order', 'level': 4, 'class': Fighter, 'ai': DefensiveAI, 'weapon': 'two-handed sword', 'armor': 'leather armor', 'shield': None},
        ]
        self.battle = Battle('Test Buffs Battle', test_roles, verbose=False)

    def test_defensive_stance_application(self):
        test_fighter = random.choice(self.battle.fighters)
        initial_armor_class = test_fighter.armor_class
        test_fighter.apply_buff(BuffCreator.create_defensive_stance())
        self.assertEqual(test_fighter.armor_class, initial_armor_class - 4, "Armor class did not increase correctly after applying Defensive Stance")

    def test_shield_wall_application(self):
        test_fighter = random.choice(self.battle.fighters)
        initial_armor_class = test_fighter.armor_class
        test_fighter.apply_buff(BuffCreator.create_shield_wall())
        self.assertEqual(test_fighter.armor_class, initial_armor_class - 6, "Armor class did not increase correctly after applying Shield Wall")

    def test_defensive_action_buff_with_shield(self):
        test_fighter = next(fighter for fighter in self.battle.fighters if fighter.shield is not None)
        initial_armor_class = test_fighter.armor_class
        test_fighter.take_defensive_action()
        self.assertEqual(test_fighter.armor_class, initial_armor_class - 6, "Defensive Action with shield did not apply Shield Wall buff")

    def test_defensive_action_buff_with_no_shield(self):
        test_fighter = next(fighter for fighter in self.battle.fighters if fighter.shield is None)
        initial_armor_class = test_fighter.armor_class
        test_fighter.take_defensive_action()
        self.assertEqual(test_fighter.armor_class, initial_armor_class - 4, "Defensive Action without shield did not apply Defensive Stance buff")

    def test_buff_duration(self):
        test_fighter = random.choice(self.battle.fighters)
        initial_armor_class = test_fighter.armor_class
        test_fighter.apply_buff(BuffCreator.create_defensive_stance())
        self.assertEqual(test_fighter.armor_class, initial_armor_class - 4, "Buff was not applied correctly")
        for _ in range(test_fighter.buffs[0].remaining_duration):
            test_fighter.take_turn()
        self.assertEqual(test_fighter.armor_class, initial_armor_class, "Buff should have expired")

    def test_buff_cooldown(self):
        test_fighter = random.choice(self.battle.fighters)
        buff = BuffCreator.create_shield_wall()
        test_fighter.apply_buff(buff)

        self.assertEqual(buff.remaining_cooldown, buff.cooldown, "Buff cooldown was not set correctly")

        # Process turns equal to the duration of the buff
        for _ in range(buff.duration):
            test_fighter.take_turn()

        # Cooldown should start only after the buff has expired
        self.assertEqual(buff.remaining_cooldown, buff.cooldown, "Buff cooldown should start after buff expires")

        for _ in range(buff.cooldown):
            test_fighter.take_turn()

        self.assertEqual(buff.remaining_cooldown, 0, "Buff cooldown did not decrease correctly")

    def test_berserk_rage_last_teammate(self):
        test_fighter = random.choice(self.battle.fighters)
        team_mate = next(fighter for fighter in self.battle.fighters if fighter != test_fighter)
        team_mate.die()  # Simulate teammate death
        self.assertIn('Berserk Rage', [buff.name for buff in test_fighter.buffs], "Berserk Rage buff was not applied correctly")

        # Check attack bonus progression
        expected_attack_bonus = 5
        for _ in range(5):
            self.assertEqual(test_fighter.attack_bonus, expected_attack_bonus, f"Attack bonus did not increase correctly after applying Berserk Rage")
            test_fighter.take_turn()
            expected_attack_bonus -= 1

    def test_heal_over_time_application(self):
        test_fighter = random.choice(self.battle.fighters)
        initial_health = test_fighter.health
        test_fighter.health -= 10  # Simulate damage
        test_fighter.apply_buff(BuffCreator.create_heal_over_time())
        for _ in range(2):  # Healing over two turns
            test_fighter.take_turn()
        self.assertGreater(test_fighter.health, initial_health - 10, "Health did not increase correctly after applying Heal Over Time")

    def test_heal_over_time_duration(self):
        test_fighter = random.choice(self.battle.fighters)
        initial_health = test_fighter.health
        test_fighter.health -= 10  # Simulate damage
        test_fighter.apply_buff(BuffCreator.create_heal_over_time())
        for _ in range(3):  # Healing over three turns
            test_fighter.take_turn()
        self.assertGreater(test_fighter.health, initial_health - 10, "Health should have increased over time")

    def test_heal_over_time_cooldown(self):
        test_fighter = random.choice(self.battle.fighters)
        buff = BuffCreator.create_heal_over_time()
        test_fighter.apply_buff(buff)
        for _ in range(buff.remaining_duration + buff.remaining_cooldown):  # Full duration plus cooldown
            test_fighter.take_turn()
        self.assertEqual(buff.remaining_cooldown, 0, "Buff cooldown did not decrease correctly")

class TestBuffs2(unittest.TestCase):

    def setUp(self):
        self.map = Map(10, 10, 'grid8')
        self.position = Position(1, 1, 'grass')
        self.map.occupy_position(None, self.position)

        self.fighter = Fighter(
            name='Fighter1', level=5, ai=None, faction='Red',
            weapon='long sword', armor='chain mail', shield='small shield'
        )
        self.fighter.position = self.position
        self.map.occupy_position(self.fighter, self.position)
        self.fighter.battle = self.map

    def test_berserk_rage(self):
        buff = BuffCreator.create_berserk_rage()
        self.fighter.attack_bonus = 10
        buff.apply(self.fighter)
        self.assertEqual(self.fighter.attack_bonus, 15)
        for _ in range(buff.duration):
            buff.tick(self.fighter)
        self.assertEqual(self.fighter.attack_bonus, 10)
        self.assertEqual(buff.remaining_cooldown, 0)

    def test_defensive_stance(self):
        buff = BuffCreator.create_defensive_stance()
        self.fighter.armor_class = 20
        buff.apply(self.fighter)
        self.assertEqual(self.fighter.armor_class, 16)
        buff.tick(self.fighter)
        self.assertEqual(self.fighter.armor_class, 16)  # No change after tick
        buff.tick(self.fighter)  # Should expire now
        self.assertEqual(self.fighter.armor_class, 20)

    def test_shield_wall(self):
        buff = BuffCreator.create_shield_wall()
        self.fighter.armor_class = 20
        buff.apply(self.fighter)
        self.assertEqual(self.fighter.armor_class, 14)
        for _ in range(buff.duration):
            buff.tick(self.fighter)
        self.assertEqual(self.fighter.armor_class, 14)  # Should still be active
        buff.tick(self.fighter)  # Should now start cooldown
        self.assertEqual(self.fighter.armor_class, 20)  # Buff effect removed
        self.assertEqual(buff.remaining_cooldown, 4)  # Cooldown starts now

    def test_heal_over_time(self):
        buff = BuffCreator.create_heal_over_time()
        self.fighter.health = 50
        buff.apply(self.fighter)
        self.assertEqual(self.fighter.health, 55)
        for _ in range(buff.duration):
            buff.tick(self.fighter)
        self.assertEqual(self.fighter.health, 80)  # Heal over time applied
        self.assertEqual(buff.remaining_cooldown, 0)  # No cooldown for heal over time

    def tearDown(self):
        # Clean up after each test
        self.map.vacate_position(self.fighter)
        self.fighter = None
        self.map = None
        self.position = None

if __name__ == '__main__':
    unittest.main()
