from typing import List, Type
from postDB import Model

from .guild_config import GuildConfig
from .permission import Permission
from .user_role import UserRole
from .token import Token
from .guild import Guild
from .user import User
from .role import Role


models_ordered: List[Type[Model]] = [
    User,
    Token,
    Guild,
    GuildConfig,
    Permission,
    Role,
    UserRole,
]
