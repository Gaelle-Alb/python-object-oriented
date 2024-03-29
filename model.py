from collections import defaultdict # for income graph
import json
import math

# If you are using Linux or Mac you can have bug when you launch the script
# To avoid this issue, execute the two following lines before importing matplotlib
import matplotlib as mil
mil.use('TkAgg') # add it before launching matplotlib
import matplotlib.pyplot as plt

class Agent:

    def __init__(self, position, **agent_attributes):
        self.position = position
        for attr_name, attr_value in agent_attributes.items():
            setattr(self, attr_name, attr_value)


class Position:

    def __init__(self, longitude_degrees, latitude_degrees):
        assert -180 <= longitude_degrees <= 180
        self.longitude_degrees = longitude_degrees

        assert -90 <= latitude_degrees <= 90
        self.latitude_degrees = latitude_degrees

    @property
    def longitude(self):
        return self.longitude_degrees * math.pi / 180

    @property
    def latitude(self):
        return self.latitude_degrees * math.pi / 180


class Zone:

    ZONES = []

    MIN_LONGITUDE_DEGREES = -180 # Attribut de classe
    MAX_LONGITUDE_DEGREES = 180
    MIN_LATITUDE_DEGREES = -90
    MAX_LATITUDE_DEGREES = 90
    WIDTH_DEGREES = 1
    HEIGHT_DEGREES = 1

    EARTH_RADIUS_KILOMETERS = 6371

    def __init__(self, corner1, corner2):
        self.corner1 = corner1 # Attribut d'instance (toujours dans __init__)
        self.corner2 = corner2
        self.inhabitants = []

    @property
    def population(self):
        return len(self.inhabitants)

    @property
    def width(self):
        return abs(self.corner1.longitude - self.corner2.longitude) * self.EARTH_RADIUS_KILOMETERS

    @property
    def height(self):
        return abs(self.corner1.latitude - self.corner2.latitude) * self.EARTH_RADIUS_KILOMETERS

    def add_inhabitant(self, inhabitant):
        self.inhabitants.append(inhabitant)

    def population_density(self):
        return self.population / self.area()

    def area(self):
        return self.height * self.width

    def average_agreeableness(self):
        if not self.inhabitants:
            return 0
        return sum([inhabitant.agreeableness for inhabitant in self.inhabitants]) / self.population

    def contains(self, position):
        """Return True if the zone contains this position"""
        return position.longitude >= min(self.corner1.longitude, self.corner2.longitude) and \
            position.longitude < max(self.corner1.longitude, self.corner2.longitude) and \
            position.latitude >= min(self.corner1.latitude, self.corner2.latitude) and \
            position.latitude < max(self.corner1.latitude, self.corner2.latitude)

    @classmethod
    def find_zone_that_contains(cls, position):

        if not cls.ZONES:
            cls._initialize_zones()

        longitude_index = int((position.longitude_degrees - cls.MIN_LONGITUDE_DEGREES) / cls.WIDTH_DEGREES)
        latitude_index = int((position.latitude_degrees - cls.MIN_LATITUDE_DEGREES) / cls.HEIGHT_DEGREES)
        longitude_bins = int((cls.MAX_LONGITUDE_DEGREES - cls.MIN_LONGITUDE_DEGREES) / cls.WIDTH_DEGREES)
        zone_index = latitude_index * longitude_bins + longitude_index

        zone = cls.ZONES[zone_index]

        assert zone.contains(position) # raise an exception when false

        return zone

    # Méthode globale à la classe (et non de l'instance)
    @classmethod
    def _initialize_zones(cls):

        cls.ZONES = []

        for latitude in range(cls.MIN_LATITUDE_DEGREES, cls.MAX_LATITUDE_DEGREES, cls.HEIGHT_DEGREES):
            for longitude in range(cls.MIN_LONGITUDE_DEGREES, cls.MAX_LONGITUDE_DEGREES, cls.WIDTH_DEGREES):
                bottom_left_corner = Position(longitude, latitude)
                top_right_corner = Position(longitude + cls.WIDTH_DEGREES, latitude + cls.HEIGHT_DEGREES)
                zone = Zone(bottom_left_corner, top_right_corner)
                cls.ZONES.append(zone)


class BaseGraph:

    def __init__(self):
        self.title = "Your graph title"
        self.x_label = "X-axis label"
        self.y_label = "Y-axis label"
        self.show_grid = True

    def show(self, zones):
        x_values, y_values = self.xy_values(zones)
        self.plot(x_values, y_values)

        plt.xlabel(self.x_label)
        plt.ylabel(self.y_label)
        plt.title(self.title)
        plt.grid(self.show_grid)
        plt.show()

    def plot(self, x_values, y_values):
        plt.plot(x_values, y_values, '.')

    def xy_values(self, zones):
        # You should implement this method in your children classes
        raise NotImplementedError

# Inheritance
class AgreeablenessGraph(BaseGraph):

    def __init__(self):
        super().__init__() # executes the parent's __init__() method
        # super(AgreeablenessGraph, self).__init__() # Call base constructor
        self.title = "Nice people live in the countryside"
        self.x_label = "population density"
        self.y_label = "agreeableness"

    def xy_values(self, zones):
        x_values = [zone.population_density() for zone in zones]
        y_values = [zone.average_agreeableness() for zone in zones]
        return x_values, y_values


class IncomeGraph(BaseGraph):
    # Inheritance, yay!

    def __init__(self):
        # Call base constructor
        super(IncomeGraph, self).__init__()

        self.title = "Older people have more money"
        self.x_label = "age"
        self.y_label = "income"

    def xy_values(self, zones):
        income_by_age = defaultdict(float)
        population_by_age = defaultdict(int)
        for zone in zones:
            for inhabitant in zone.inhabitants:
                income_by_age[inhabitant.age] += inhabitant.income
                population_by_age[inhabitant.age] += 1

        x_values = range(0, 100)
        # list comprehension (listcomps)
        y_values = [income_by_age[age] / (population_by_age[age] or 1) for age in range(0, 100)]
        return x_values, y_values


def main():

    for agent_attributes in json.load(open("agents-100k.json")):
        longitude = agent_attributes.pop("longitude")
        latitude = agent_attributes.pop("latitude")

        position = Position(longitude, latitude)

        agent = Agent(position, **agent_attributes)
        zone = Zone.find_zone_that_contains(position)
        zone.add_inhabitant(agent)

    agreeableness_graph = AgreeablenessGraph()
    agreeableness_graph.show(Zone.ZONES)

    income_graph = IncomeGraph()
    income_graph.show(Zone.ZONES)

if __name__ == "__main__":
    main()
