class WtUnit:
    # Basic information
    hash_name = ""
    arcade_br = 1.0
    realistic_br = 1.0
    realistic_ground_br = 1.0
    simulator_br = 1.0
    simulator_ground_br= 1.0

    # Counters
    full_uptier_cnt = 0
    full_downtier_cnt = 0
    less_uptier_cnt = 0
    less_downtier_cnt = 0

    def __init__(self, hash_name: str,
                 arcade_br: float = 1.0, realistic_br: float = 1.0,
                 realistic_ground_br: float = 1.0, simulator_br: float = 1.0,
                 simulator_ground_br: float = 1.0):
        self.hash_name = hash_name
        self.arcade_br = arcade_br
        self.realistic_br = realistic_br
        self.realistic_ground_br = realistic_ground_br
        self.simulator_br = simulator_br
        self.simulator_ground_br = simulator_ground_br

class WtUnitManager:
    def __init__(self):
        self.units = {}
        self.player_units = {}

    def add_player_unit(self, unit: WtUnit):
        if unit.hash_name not in self.player_units:
            self.player_units[unit.hash_name] = unit
        # else:
        #     print(f"Player unit {unit.hash_name} already exists.")
        self.add_unit(unit)

    def add_unit(self, unit: WtUnit):
        if unit.hash_name not in self.units:
            self.units[unit.hash_name] = unit
        # else:
        #     print(f"Unit {unit.hash_name} already exists.")

    def get_unit(self, hash_name: str) -> WtUnit:
        return self.units.get(hash_name, None)

    def get_player_unit(self, hash_name: str) -> WtUnit:
        return self.units.get(hash_name, None)

    def get_all_units(self):
        return list(self.units.values())