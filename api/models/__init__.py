from typing import List, Type
from postDB import Model


from .user import User


models_ordered: List[Type[Model]] = [User]
