import logging
import sys

from .eventloop import Eventloop
from .gameitem import GameItem
from .geom.vector import Vector
from .model.world import World
from .util.log import init_log
from .util.options import Options
from .version import RELEASE


log = None


class Gloopy(object):

    def __init__(self):
        global log
        init_log()
        log = logging.getLogger(__name__)

        self.options = None
        self.world = None
        self.camera = None
        self.eventloop = None

    def init(self):
        log.info('v%s' % (RELEASE,))
        self.options = Options(sys.argv)
        self.world = World()
        self.camera = GameItem(
            position=Vector(0, 0, 10),
            look_at=Vector.Origin,
        )
        self.world.add(self.camera)
        self.eventloop = Eventloop(self.world, self.camera, self.options)
        self.eventloop.init()

    def run(self):
        self.eventloop.start()

