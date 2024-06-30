import unittest
from arena import *

test_roles = [
    {'name': 'Alice', 'faction': 'Order', 'level': 5, 'class': Fighter, 'ai': RandomAttackAI, 'weapon': 'long sword', 'armor': 'chain mail', 'shield': 'small shield'},
    {'name': 'Bob', 'faction': 'Order', 'level': 4, 'class': Fighter, 'ai': GreatestThreatAI, 'weapon': 'two-handed sword', 'armor': 'leather armor', 'shield': None},
    {'name': 'Eve', 'faction': 'Chaos', 'level': 5, 'class': Fighter, 'ai': LowestHealthAI, 'weapon': 'flail', 'armor': 'padded armor', 'shield': 'large shield'},
    {'name': 'Mallory', 'faction': 'Chaos', 'level': 3, 'class': Fighter, 'ai': RandomAttackAI, 'weapon': 'morning star', 'armor': 'banded mail', 'shield': None},
    {'name': 'Carol', 'faction': 'Order', 'level': 3, 'class': Fighter, 'ai': DefensiveAI, 'weapon': 'spear', 'armor': 'leather armor', 'shield': 'small shield'},
    {'name': 'Dave', 'faction': 'Chaos', 'level': 3, 'class': Fighter, 'ai': DefensiveAI, 'weapon': 'quarterstaff', 'armor': 'ring mail', 'shield': None},
]

class TestFighter(unittest.TestCase):

    def setUp(self):
        self.battle = Battle('TestFighter Battle', test_roles, verbose=False)

    def test_initial_health(self):
        self.assertGreaterEqual(self.battle.fighters[0].health, 5)
        self.assertLessEqual(self.battle.fighters[0].health, 50)
        self.assertGreaterEqual(self.battle.fighters[1].health, 4)
        self.assertLessEqual(self.battle.fighters[1].health, 40)
        self.assertGreaterEqual(self.battle.fighters[2].health, 5)
        self.assertLessEqual(self.battle.fighters[2].health, 50)
        self.assertGreaterEqual(self.battle.fighters[3].health, 3)
        self.assertLessEqual(self.battle.fighters[3].health, 30)
        self.assertGreaterEqual(self.battle.fighters[4].health, 3)
        self.assertLessEqual(self.battle.fighters[4].health, 30)
        self.assertGreaterEqual(self.battle.fighters[5].health, 3)
        self.assertLessEqual(self.battle.fighters[5].health, 30)

    def test_armor_class(self):
        self.assertEqual(self.battle.fighters[0].armor_class, 4)  # chain mail (5) + small shield (1)
        self.assertEqual(self.battle.fighters[1].armor_class, 8)  # leather armor (2)
        self.assertEqual(self.battle.fighters[2].armor_class, 6)  # padded armor (2) + large shield (2)
        self.assertEqual(self.battle.fighters[3].armor_class, 4)  # banded mail (6)
        self.assertEqual(self.battle.fighters[4].armor_class, 7)  # leather armor (2) + small shield (1)
        self.assertEqual(self.battle.fighters[5].armor_class, 7)  # ring mail (3)

    def test_calculate_threat(self):
        self.assertAlmostEqual(GreatestThreatAI.calculate_threat(self.battle.fighters[0]), 4.5)  # long sword 1d8
        self.assertAlmostEqual(GreatestThreatAI.calculate_threat(self.battle.fighters[1]), 5.5)  # two-handed sword 1d10
        self.assertAlmostEqual(GreatestThreatAI.calculate_threat(self.battle.fighters[2]), 4.5)  # flail 1d6+1
        self.assertAlmostEqual(GreatestThreatAI.calculate_threat(self.battle.fighters[3]), 5.0)  # morning star 2d4
        self.assertAlmostEqual(GreatestThreatAI.calculate_threat(self.battle.fighters[4]), 3.5)  # spear 1d6
        self.assertAlmostEqual(GreatestThreatAI.calculate_threat(self.battle.fighters[5]), 3.5)  # quarterstaff 1d6

    def test_take_damage(self):
        self.battle.fighters[0].take_damage(5, self.battle.fighters[1])
        self.assertEqual(self.battle.fighters[0].health, self.battle.fighters[0].max_health - 5)

    def test_die(self):
        fighter = self.battle.fighters[0];
        self.battle.fighters[0].take_damage(fighter.health, self.battle.fighters[1])
        self.assertIsNone(fighter.battle)
        self.assertNotIn(fighter, self.battle.fighters)
        self.assertNotIn(fighter, self.battle.fighters[1].battle.fighters)

    def test_repr(self):
        self.assertIn('Alice', repr(self.battle.fighters[0]))
        self.assertIn('long sword', repr(self.battle.fighters[0]))
        self.assertIn('RandomAttackAI', repr(self.battle.fighters[0]))

class TestBattle(unittest.TestCase):

    def setUp(self):
        self.battle = Battle('Test Battle', test_roles, verbose=False)

    def test_battle_initialization(self):
        self.assertEqual(len(self.battle.fighters), 6)

    def test_fighter_factions(self):
        factions = {fighter.faction for fighter in self.battle.fighters}
        self.assertEqual(factions, {'Order', 'Chaos'})

    def test_play_round(self):
        initial_fighters_count = len(self.battle.fighters)
        self.battle.play_round()
        self.assertLessEqual(len(self.battle.fighters), initial_fighters_count)

    def test_fight_battle(self):
        initial_fighters_count = len(self.battle.fighters)
        self.battle.fight_battle()
        self.assertLess(len(self.battle.fighters), initial_fighters_count)

class TestAI(unittest.TestCase):

    def setUp(self):
        self.battle = Battle('Test Battle', test_roles, verbose=False)

    def test_random_attack_ai(self):
        fighters_with_random_ai = [fighter for fighter in self.battle.fighters if fighter.ai == RandomAttackAI]
        self.assertGreater(len(fighters_with_random_ai), 0, "No fighters with RandomAttackAI found")

        # Perform the battle
        self.battle.fight_battle()

        # Filter logs to include only attacks by fighters with random AI
        attacked_opponents = set()
        for log in self.battle.logs:
            if 'attacks' in log:
                attacker_name = log.split()[0]
                if any(attacker_name == fighter.name for fighter in fighters_with_random_ai):
                    attacked_opponents.add(log.split()[2])

        # Ensure that the number of unique attacked opponents is greater than 1
        self.assertTrue(len(set(attacked_opponents)) > 1, "Random AI fighters should attack more than one unique opponent")

    def test_lowest_health_attack_ai(self):
        fighters_with_lowest_health_ai = [fighter for fighter in self.battle.fighters if fighter.ai == LowestHealthAI]
        self.assertGreater(len(fighters_with_lowest_health_ai), 0)

        self.battle.fight_battle()
        lowest_health_fighters = sorted([fighter for fighter in self.battle.fighters if fighter.faction != 'Order'], key=lambda f: f.health)
        for fighter in fighters_with_lowest_health_ai:
            target = min(lowest_health_fighters, key=lambda f: f.health)
            self.assertIn(target.name, [log.split()[2] for log in self.battle.logs if 'attacks' in log])

    def test_greatest_threat_ai(self):
        fighters_with_greatest_threat_ai = [fighter for fighter in self.battle.fighters if fighter.ai == GreatestThreatAI]
        self.assertGreater(len(fighters_with_greatest_threat_ai), 0)

        self.battle.fight_battle()
        threat_fighters = sorted([fighter for fighter in self.battle.fighters if fighter.faction != 'Order'], key=lambda f: GreatestThreatAI.calculate_threat(f))
        for fighter in fighters_with_greatest_threat_ai:
            target = max(threat_fighters, key=lambda f: GreatestThreatAI.calculate_threat(f))
            self.assertIn(target.name, [log.split()[2] for log in self.battle.logs if 'attacks' in log])

    def test_defensive_ai(self):
        fighters_with_defensive_ai = [fighter for fighter in self.battle.fighters if fighter.ai == DefensiveAI]
        self.assertGreater(len(fighters_with_defensive_ai), 0)

        self.battle.fight_battle()
        for fighter in fighters_with_defensive_ai:
            if fighter.health < fighter.max_health / 4:
                self.assertTrue(any('Shield Wall' in log or 'Defensive Stance' in log for log in self.battle.logs))
            else:
                self.assertTrue(any('Shield Wall' not in log and 'Defensive Stance' not in log for log in self.battle.logs))

class TestBuff(unittest.TestCase):
    def setUp(self):
        self.fighter = Fighter('Test Fighter', 5, GreatestThreatAI, 'Order', 'long sword', 'chain mail', 'small shield')

    def test_apply_buff(self):
        self.fighter.apply_buff(berserk_rage)
        self.assertIn(berserk_rage, self.fighter.buffs)
        self.assertEqual(self.fighter.attack_bonus, 3)

    def test_buff_duration_and_cooldown(self):
        berserk_rage.apply(self.fighter)
        for _ in range(6):
            for buff in self.fighter.buffs:
                buff.tick

if __name__ == '__main__':
    unittest.main()
