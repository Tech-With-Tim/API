from typing import List, Type
from postDB import Model


from .token import Token
from .user import User
from .guild import Guild
from .role import Role
from .permission import Permission
from .guild_config import GuildConfig
from .user_role import UserRole


models_ordered: List[Type[Model]] = [
    User,
    Token,
    Guild,
    GuildConfig,
    Permission,
    Role,
    UserRole
]
