import unittest
from weapon import MeleeWeapon, Bow, Crossbow, Sling, Arrow, Bolt, Rock
from fighter import Fighter
from map import Map

class TestMeleeWeapons(unittest.TestCase):

    def setUp(self):
        self.map = Map(10, 10)
        self.fighter1 = Fighter(name="Warrior", level=5, ai=None, faction="Red", weapon=MeleeWeapon("Sword", damage=10))
        self.fighter2 = Fighter(name="Target", level=5, ai=None, faction="Blue", weapon=None)
        self.map.occupy_position(self.fighter1, self.map.get_position(0, 0))
        self.map.occupy_position(self.fighter2, self.map.get_position(0, 1))

    def test_melee_attack_adjacent(self):
        weapon = self.fighter1.weapon
        weapon.attack(self.fighter1, self.fighter2)
        self.assertEqual(self.fighter2.health, self.fighter2.max_health - weapon.damage, "Target should take damage from the melee attack")

    def test_melee_attack_not_adjacent(self):
        self.map.move_fighter(self.fighter2, self.map.get_position(5, 5))  # Move target out of adjacency
        weapon = self.fighter1.weapon
        weapon.attack(self.fighter1, self.fighter2)
        self.assertEqual(self.fighter2.health, self.fighter2.max_health, "Target should not take damage if not adjacent")

    def test_melee_attack_with_shield(self):
        self.fighter2.shield = 'small shield'
        self.fighter2.armor_class = 10 - shield_list[self.fighter2.shield]
        weapon = self.fighter1.weapon
        weapon.attack(self.fighter1, self.fighter2)
        expected_damage = max(0, weapon.damage - shield_list[self.fighter2.shield])
        self.assertEqual(self.fighter2.health, self.fighter2.max_health - expected_damage, "Target should take reduced damage due to shield")

class TestRangedWeapons(unittest.TestCase):

    def setUp(self):
        self.map = Map(10, 10)
        self.fighter1 = Fighter(name="Archer", level=5, ai=None, faction="Red", weapon=None, armor=None, shield=None, ranged_weapon=Bow())
        self.fighter2 = Fighter(name="Target", level=5, ai=None, faction="Blue", weapon=None, armor=None, shield=None)
        self.map.occupy_position(self.fighter1, self.map.get_position(0, 0))
        self.map.occupy_position(self.fighter2, self.map.get_position(5, 5))

    def test_load_ammunition(self):
        bow = self.fighter1.ranged_weapon
        arrow = Arrow()
        bow.load_ammunition(arrow)
        self.assertIn(arrow, bow.ammunition, "Arrow should be loaded into the bow")

    def test_fire_with_ammunition(self):
        bow = self.fighter1.ranged_weapon
        arrow = Arrow()
        bow.load_ammunition(arrow)
        result = bow.fire(self.fighter1, self.fighter2, self.map)
        self.assertTrue(result, "Bow should fire successfully with ammunition")
        self.assertEqual(self.fighter2.health, self.fighter2.max_health - bow.damage, "Target should take damage from the arrow")

    def test_fire_without_ammunition(self):
        bow = self.fighter1.ranged_weapon
        result = bow.fire(self.fighter1, self.fighter2, self.map)
        self.assertFalse(result, "Bow should not fire without ammunition")

    def test_fire_out_of_range(self):
        self.map.move_fighter(self.fighter2, self.map.get_position(9, 9))  # Move target out of range
        bow = self.fighter1.ranged_weapon
        arrow = Arrow()
        bow.load_ammunition(arrow)
        result = bow.fire(self.fighter1, self.fighter2, self.map)
        self.assertFalse(result, "Bow should not fire if the target is out of range")

    def test_crossbow_fire(self):
        crossbow = Crossbow()
        bolt = Bolt()
        crossbow.load_ammunition(bolt)
        self.fighter1.equip_ranged_weapon(crossbow)
        result = crossbow.fire(self.fighter1, self.fighter2, self.map)
        self.assertTrue(result, "Crossbow should fire successfully with ammunition")
        self.assertEqual(self.fighter2.health, self.fighter2.max_health - crossbow.damage, "Target should take damage from the bolt")

    def test_sling_fire(self):
        sling = Sling()
        rock = Rock()
        sling.load_ammunition(rock)
        self.fighter1.equip_ranged_weapon(sling)
        result = sling.fire(self.fighter1, self.fighter2, self.map)
        self.assertTrue(result, "Sling should fire successfully with ammunition")
        self.assertEqual(self.fighter2.health, self.fighter2.max_health - sling.damage, "Target should take damage from the rock")

if __name__ == '__main__':
    unittest.main()
