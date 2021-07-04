from postDB import Model
from typing import List, Type

from .user import User
from .token import Token


models_ordered: List[Type[Model]] = [User, Token]
