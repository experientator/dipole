from pydantic import BaseModel

class Material(BaseModel):
    """Class representing a material in general"""

    material_name: str
    doi: str

class MetalData(Material):
    """Class representing a metal"""

    plasm_frequency: float
    gamma: float
    inf_permittivity: float

class OtherData(Material):
    """Class representing a dielectric or semiconductor"""

    permittivity: float

class NewAnalysis(BaseModel):
    """Class representing an analysis"""

    core_name: str
    shell_name: str
    medium_name: str
    radius: float
    core_radius: float

class User(BaseModel):
    """Class representing a user"""

    name: str
    email: str
    password: str
