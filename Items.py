"""
Items
"""
from settings import *

class WITEM:
    def __init__(self, game):
        self.game = game
        self.name = "Uknown Item"
        self.consumable = True
    
    def use(self):
        pass

class HealingPotion(WITEM):
    def __init__(self, game):
        super().__init__(game)
        self.name = "Healing Potion"
    
    def use(self):
        """
        Heal the player HP_POT % of their health 
        rounded to the nearest integer
        """
        max_health = self.game.player.state.max_health
        cur_health = self.game.player.state.health
        gained = int(max_health * HP_POT)
        if cur_health + gained <= max_health:
            new_health = cur_health + gained
        else:
            new_health = max_health
        new_health = int(new_health)
        self.game.player.state.health = new_health
        self.game.log.info(f"I drank a healing potion gaining {gained} life (current health {new_health})")

