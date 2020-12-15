from .modlog import ModLog
from .member import Member
from .wallet import Wallet
from .token import Token
from .guild import Guild
from .asset import Asset
from .timer import Timer
from .badge import Badge
from .user import User
from .log import Log

# Models will be created in this order to prevent relation "<tablename>" does not exist.
all_models = [User, Guild, Token, Member, Wallet, Asset, Badge, Timer, ModLog, Log]
