
import lodestone
from rich.console import Console
from rich.progress import Progress
import ast
import inspect
from javascript import require
import math
Vec3  = require('vec3').Vec3

class CubeMiner:
    def __init__(self, bot:lodestone.Bot, topCorner, bottomCorner, expectedBlockIds, options = {}):
        self.bot = bot
        self.topRight = Vec3(
            max(topCorner.x, bottomCorner.x),
            max(topCorner.y, bottomCorner.y),
            max(topCorner.z, bottomCorner.z)
        )
        self.bottomLeft = Vec3(
            min(topCorner.x, bottomCorner.x),
            min(topCorner.y, bottomCorner.y),
            min(topCorner.z, bottomCorner.z)
        )
        self.possiblePositions = []
        self.mining = False
        self.expectedBlockIds = expectedBlockIds
        self.options = {
            'distanceDivider': 5,
            'yawDivider': math.pi / 2,
            'pitchDivider': math.pi / 2,
            'reach': 4.5,
            **options
        }
    
    async def mine(self):
        self.mining = True
        self.possiblePositions = self.getBlockPositions()
        while self.mining:
            position = self.nextPosition()
            if not position:
                break
            block = self.bot.blockAt(position)
            if block is None or block.id not in self.expectedBlockIds:
                self.removePosition(position)
                continue
            if block.position.distanceTo(self.bot.entity.position) > self.options['reach']:
                await self.bot.pathfinder.goto(
                    self.bot.goals.GoalLookAtBlock(block.position, self.bot.world, {
                        'reach': max(1, self.options['reach'] - 1)  # leeway in reach
                    })
                )
            else:
                await self.bot.lookAt(block.position.offset(0.5, 0.5, 0.5))
            await self.digInLine()  # try to dig in straight line
            # await self.bot.dig(block)
            # self.removePosition(position)
    
    async def digInLine(self):
        while self.mining:
            blockToDig = self.bot.blockAtCursor(self.options['reach'])
            if blockToDig is None or blockToDig.id not in self.expectedBlockIds:
                break
            await self.bot.dig(blockToDig)
            self.removePosition(blockToDig.position)
    
    def stop(self):
        self.mining = False
    
    def hasPosition(self, position):
        return any(pos.equals(position) for pos in self.possiblePositions)
    
    def removePosition(self, position):
        index = next((i for i, pos in enumerate(self.possiblePositions) if pos.equals(position)), -1)
        if index != -1:
            self.possiblePositions.pop(index)
    
    def getBlockPositions(self):
        positions = []
        for x in range(self.bottomLeft.x, self.topRight.x + 1):
            for y in range(self.bottomLeft.y, self.topRight.y + 1):
                for z in range(self.bottomLeft.z, self.topRight.z + 1):
                    positions.append(Vec3(x, y, z))
        return positions
    
    def nextPosition(self):
        lowestScore = 1000
        bestPosition = None
        for position in self.possiblePositions:
            score = self.positionScore(position)
            if score < lowestScore:
                lowestScore = score
                bestPosition = position
        return bestPosition
    
    def positionScore(self, position):
        distanceScore = position.distanceTo(self.bot.entity.position) / 5  # i chose 5 to help normalize the data
        yawPitchResults = self.yawPitchTo(position)
        yawScore = abs(self.deltaYaw(yawPitchResults[0])) / (math.pi / 2)  # 45 degrees is score of 1
        pitchScore = abs(self.bot.entity.pitch - yawPitchResults[1]) / (math.pi / 2)
        return distanceScore + (yawScore + pitchScore) / 2
    
    def yawPitchTo(self, point):
        # taken from physics.js in mineflayer
        delta = point.minus(self.bot.entity.position.offset(0, self.bot.entity.height, 0))
        yaw = math.atan2(-delta.x, -delta.z)
        groundDistance = math.sqrt(delta.x * delta.x + delta.z * delta.z)
        pitch = math.atan2(delta.y, groundDistance)
        return yaw, pitch
    
    def euclideanMod(self, numerator, denominator):
        # from math.js in mineflayer
        result = numerator % denominator
        return result + denominator if result < 0 else result
    
    def deltaYaw(self, targetYaw):
        return self.euclideanMod(targetYaw - self.bot.entity.yaw + math.pi, math.pi * 2) - math.pi


class ChunkMiner:
    """
    Mine a chunk
    """
    def __init__(self, bot: lodestone.Bot):
        "The injection method"
        self.bot:lodestone.Bot = bot
        self.mcData = require('minecraft-data')(bot.bot.version)
        self.Item = require('prismarine-item')(bot.bot.version)
        self.console = Console(force_terminal=True)
        self.code = inspect.getsource(inspect.getmodule(self.__class__))
        self.tree = ast.parse(self.code)
        self.events = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call) and hasattr(node.func, 'attr') and node.func.attr == 'on':
                event = node.args[0].s
                self.events.append(event)
        events_loaded = list(bot.loaded_events.keys())
        events_loaded.append(self.events) # add the event to the list
        bot.emit('event_loaded', *events_loaded)
        plugins_loaded = list(bot.loaded_plugins.keys())
        plugins_loaded.append(self.__class__.__name__) # add the plugin to the list
        bot.emit('plugin_loaded', *plugins_loaded)
        self.building_up = False
        self.bot.mine_chunk:callable = self.start
    def start(self, topCorner, bottomCorner, expectedBlockIds):
        woolCube = CubeMiner(self.bot, Vec3(0, 0, 0), Vec3(10, 10, 10), [self.bot.registry.blocksByName['white_wool'].id])
        woolCube.mine()



