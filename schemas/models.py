from typing import List, Optional
from sqlmodel import SQLModel, Field as SQLField, Relationship

class User(SQLModel, table=True):
    """Class representing a user table"""

    user_id: int = SQLField(default=None, nullable=False, primary_key=True)
    email: str = SQLField(nullable=True, unique_items=True)
    password: str | None
    name: str

class Core(SQLModel, table=True):
    """Class representing a core table"""

    core_id: int = SQLField(default=None, nullable=False, primary_key=True)
    core_name: str = SQLField(nullable=False)
    core_permittivity: float = SQLField(nullable=False)
    core_doi: str
    user_id: int = SQLField(foreign_key="user.user_id")

    analyses: List["Analysis"] = Relationship(back_populates="core")

class Medium(SQLModel, table=True):
    """Class representing a medium table"""

    medium_id: int = SQLField(default=None, nullable=False, primary_key=True)
    medium_name: str = SQLField(nullable=False)
    medium_permittivity: float = SQLField(nullable=False)
    medium_doi: str
    user_id: int = SQLField(foreign_key="user.user_id")

    analyses: List["Analysis"] = Relationship(back_populates="medium")

class Shell(SQLModel, table=True):
    """Class representing a shell table"""

    shell_id: int = SQLField(default=None, nullable=False, primary_key=True)
    shell_name: str = SQLField(nullable=False)
    plasm_frequency: float = SQLField(nullable=False)
    gamma: float = SQLField(nullable=False)
    inf_permittivity: float = SQLField(nullable=False)
    shell_doi: str
    user_id: int = SQLField(foreign_key="user.user_id")

    analyses: List["Analysis"] = Relationship(back_populates="shell")

class Analysis(SQLModel, table=True):
    """Class representing an analysis table"""

    analysis_id: int = SQLField(default=None, nullable=False, primary_key=True)
    core_radius: float = SQLField(nullable=False)
    radius: float = SQLField(nullable=False)
    first_resonance: float
    second_resonance: float
    first_transparency: float
    second_transparency: float
    core_id: int = SQLField(foreign_key="core.core_id")
    shell_id: int = SQLField(foreign_key="shell.shell_id")
    medium_id: int = SQLField(foreign_key="medium.medium_id")
    user_id: int = SQLField(foreign_key="user.user_id")

    core: Optional[Core] = Relationship(back_populates="analyses")
    shell: Optional[Shell] = Relationship(back_populates="analyses")
    medium: Optional[Medium] = Relationship(back_populates="analyses")
