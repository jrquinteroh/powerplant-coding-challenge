from pydantic import BaseModel, Field
from typing import List

class Fuel(BaseModel):
    gas_euro_per_mwh: float = Field(..., ge=0, description="Gas price in €/MWh", alias="gas(euro/MWh)")
    kerosine_euro_per_mwh: float = Field(..., ge=0, description="Kerosine price in €/MWh", alias="kerosine(euro/MWh)")
    co2_euro_per_ton: float = Field(..., ge=0, description="CO2 price in €/ton", alias="co2(euro/ton)")
    wind_percentage: float = Field(..., ge=0, le=100, description="Wind availability in %", alias="wind(%)")

class Powerplant(BaseModel):
    name: str = Field(..., description="Name of the powerplant")
    type: str = Field(..., description="Type: gasfired, turbojet, or windturbine")
    efficiency: float = Field(..., gt=0, le=1, description="Efficiency of the powerplant")
    pmin: float = Field(..., ge=0, description="Minimum power output in MW")
    pmax: float = Field(..., ge=0, description="Maximum power output in MW")

class Payload(BaseModel):
    load: float = Field(..., gt=0, description="Total power to generate in MWh")
    fuels: Fuel = Field(..., description="Fuel prices and wind availability")
    powerplants: List[Powerplant] = Field(..., description="List of powerplants")
