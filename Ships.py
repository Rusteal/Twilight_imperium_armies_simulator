class Ship:
    def __init__(self, name: str, combat: int, cost: float, move: int, hits: int = 1, capacity: int= 0, 
                 sustain_damage: bool = False, 
                 bombardment: bool = False, 
                 bombardment_hits: int = 0, bombardment_combat: int = 0,
                 anti_fighter_barrage: bool = False, 
                 anti_fighter_hits: int = 0, anti_fighter_combat: int = 0):
        self.name = name
        self.cost = cost
        self.hits = hits
        self.combat = combat
        self.move = move
        self.capacity = capacity
        self.sustain_damage = sustain_damage
        self.bombardment = bombardment
        self.bombardment_hits = bombardment_hits
        self.bombardment_combat = bombardment_combat
        self.anti_fighter_barrage = anti_fighter_barrage
        self.anti_fighter_hits = anti_fighter_hits
        self.anti_fighter_combat = anti_fighter_combat

    def upgrade(self, upgrade_factor):
        # Default upgrade behavior (can be overwritten by subclasses)
        self.hit_value += upgrade_factor

class DefaultCruiser(Ship):
    def __init__(self):
        # Predefined attributes for a cruiser
        super().__init__(name="Cruiser I", combat=7, cost=2, move=2)

    def upgrade(self, upgrade_factor):
        # Custom upgrade behavior for a cruiser 
        self.move += 1
        self.capacity += 1
        self.combat -= 1
        self.name += "I"

class DefaultDreadnought(Ship):
    def __init__(self):
        # Predefined attributes for a dreadnought
        super().__init__(name="Dreadnought I", combat=5, cost=4, move=1, sustain_damage=True, 
                         bombardment=True, bombardment_hits=1, bombardment_combat=5)

    def upgrade(self, upgrade_factor):
        # Custom upgrade behavior for a dreadnought
        self.move += 1
        self.name += "I"

        
class DefaultFlagship(Ship):
    def __init__(self):
        # Predefined attributes for a flagship
        super().__init__(name="Flagship I", hits=2, combat=5, cost=12, move=1, capacity=3, sustain_damage=True)
        
class DefaultCarrier(Ship):
    def __init__(self):
        super().__init__(
            name="Carrier I",
            combat=9,
            cost=9,
            move=1,
            capacity=4
        )

    def upgrade(self, upgrade_factor=1):
        self.move += 1  # +1 move
        self.capacity += 2
        self.name += "I"  # Naming convention for upgraded ship

class DefaultFighter(Ship):
    def __init__(self):
        super().__init__(
            name="Fighter I",
            combat=9,
            cost=0.5,
            move=0
        )
        
    def upgrade(self, upgrade_factor):
        self.combat -= 1
        self.move += 2


class DefaultDestroyer(Ship):
    def __init__(self):
        super().__init__(
            name="Destroyer I",
            combat=9,
            cost=5,
            move=2,
            anti_fighter_barrage=True,
            anti_fighter_hits=2,
            anti_fighter_combat=9
        )
    
    def upgrade(self, upgrade_factor=1):
        self.combat -= 1  # +1 combat
        self.anti_fighter_hits += 1  # +1 anti-fighter hits
        self.anti_fighter_combat -= 3  
        self.name += "I"  # Naming convention for upgraded ship

class DefaultWarSun(Ship):
    def __init__(self):
        super().__init__(
            name="War Sun",
            combat=3,
            cost=12,
            move=2,
            capacity=6,
            sustain_damage=True,
            bombardment=True,
            bombardment_hits=3,
            bombardment_combat=3
        )

    


