from typing import List, Type
from postDB import Model


from .token import Token
from .user import User
from .guild import Guild
from .guild_config import GuildConfig
from .weekly_challenge import Challenge


models_ordered: List[Type[Model]] = [User, Token, Guild, GuildConfig, Challenge]
