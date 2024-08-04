# arena.py
from battle import Battle
from fighter import Fighter
from ai import RandomAttackAI

VERSION = '0.6'

class Arena:
    def __init__(self, roles, iterations=1000, verbose=False):
        self.roles = roles
        self.iterations = iterations
        self.verbose = verbose
        self.factions = {role['faction'] for role in roles}
        self.wins = {faction: 0 for faction in self.factions}
        self.winner = None

    def simulate_battle(self):
        for i in range(self.iterations):
            winner = Battle(f'Battle {i + 1}', self.roles, self.verbose).fight_battle()
            if winner:
                self.wins[winner] += 1

    def print_probabilities(self):
        print('Estimated Probabilities of Victory:')
        for faction in sorted(self.factions):
            print(f'{faction}: {self.wins[faction] / self.iterations:.2%}')


#############################################################################
# start here

class Game:
    def run(self):
        print('Arena version ' + VERSION)

        #roles = [
        #    {'name': 'Glenda', 'faction': 'Red', 'level': 6, 'class': Fighter, 'weapon': 'long sword', 'armor': 'chain mail', 'shield': None, 'ai': GreatestThreatAI()},
        #    {'name': 'Hiro', 'faction': 'Blue', 'level': 3, 'class': Fighter, 'weapon': 'two-handed sword', 'armor': 'leather armor', 'shield': None, 'ai': LowestHealthAI()},
        #    {'name': 'Alice', 'faction': 'Blue', 'level': 4, 'class': Fighter, 'weapon': 'trident', 'armor': 'ring mail', 'shield': 'small shield', 'ai': DefensiveAI()},
        #]

        roles = [
            {'class': Fighter, 'name': 'Warrior', 'level': 1, 'ai': RandomAttackAI(), 'faction': 'Faction1', 'weapon': 'axe', 'armor': 'chain mail', 'shield': 'small shield'},
            {'class': Fighter, 'name': 'Archer', 'level': 1, 'ai': RandomAttackAI(), 'faction': 'Faction2', 'weapon': 'bow', 'armor': 'ring mail', 'shield': None}
        ]

        battle = Arena(roles, iterations=1, verbose=True)
        battle.simulate_battle()
        battle.print_probabilities()

Game().run()
