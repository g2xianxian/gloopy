
from ..color import Color
from ..geom.vector import Vector
from ..util.event import Event


class World(object):
    '''
    A collection of all the GameItems.
    '''
    def __init__(self):
        self.items = {}
        self.item_added = Event()
        self.item_removed = Event()
        self.update = Event()
        self.background_color = Color.Orange

    def __iter__(self):
        return self.items.itervalues()

    def __getitem__(self, itemid):
        return self.items[itemid]

    def add(self, item, position=None):
        if position is not None:
            if not isinstance(position, Vector):
                position = Vector(*position)
            item.position = position
        self.items[item.id] = item
        self.item_added.fire(item)

    def remove(self, item):
        del self.items[item.id]
        self.item_removed.fire(item)
        item.position = None

    def update_all(self, t, dt):
        self.update.fire(t, dt)
        for item in self:
            if item.update:
                item.update(item, t, dt)

