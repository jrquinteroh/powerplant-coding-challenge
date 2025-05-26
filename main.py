from fastapi import FastAPI, HTTPException
from models import Payload
import logging
import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Production Plan API")

@app.get("/")
async def root():
    return {"message": "Welcome to the Powerplant Production Plan API. Use POST /productionplan to compute a production plan."}

def calculate_marginal_cost(powerplant: dict, fuels: dict, include_co2: bool = True) -> float:
    if powerplant["type"] == "windturbine":
        return 0.0
    elif powerplant["type"] == "gasfired":
        fuel_cost = (1 / powerplant["efficiency"]) * fuels["gas_euro_per_mwh"]
        if include_co2:
            co2_cost = 0.3 * fuels["co2_euro_per_ton"]
            return fuel_cost + co2_cost
        return fuel_cost
    elif powerplant["type"] == "turbojet":
        return (1 / powerplant["efficiency"]) * fuels["kerosine_euro_per_mwh"]
    else:
        raise ValueError(f"Unknown powerplant type: {powerplant['type']}")

def allocate_power(load: float, fuels: dict, powerplants: list, include_co2: bool = True) -> list:
    SCALE = 10
    load_scaled = int(load * SCALE)
    total_max_scaled = 0

    for p in powerplants:
        p["marginal_cost"] = calculate_marginal_cost(p, fuels, include_co2)
        p["pmin_scaled"] = int(p["pmin"] * SCALE)
        if p["type"] == "windturbine":
            p["pmax_scaled"] = int(p["pmax"] * (fuels["wind_percentage"] / 100) * SCALE)
        else:
            p["pmax_scaled"] = int(p["pmax"] * SCALE)
        total_max_scaled += p["pmax_scaled"]
        if p["pmin_scaled"] > p["pmax_scaled"]:
            raise ValueError(f"Powerplant {p['name']}: pmin > pmax")

    if total_max_scaled < load_scaled:
        raise ValueError("Total maximum power capacity insufficient for load")

    sorted_plants = sorted(powerplants, key=lambda p: p["marginal_cost"])
    allocated_power = {p["name"]: 0 for p in powerplants}
    remaining_load = load_scaled

    logger.info(f"Starting allocation for load: {load} MW")

    for plant in sorted_plants:
        if remaining_load >= plant["pmin_scaled"]:
            power = min(plant["pmax_scaled"], remaining_load)
            allocated_power[plant["name"]] = power
            remaining_load -= power
            logger.debug(f"Allocated {power/SCALE} MW to {plant['name']}")
        elif remaining_load > 0:
            if plant["pmin_scaled"] <= remaining_load <= plant["pmax_scaled"]:
                allocated_power[plant["name"]] = remaining_load
                remaining_load = 0

    while remaining_load != 0:
        if remaining_load > 0:
            candidates = [
                p for p in sorted_plants
                if allocated_power[p["name"]] < p["pmax_scaled"]
            ]
            if not candidates:
                raise ValueError("Cannot increase power to match load")
            plant = min(candidates, key=lambda p: p["marginal_cost"])
            allocated_power[plant["name"]] += 1
            remaining_load -= 1
        else:
            candidates = [
                p for p in sorted_plants
                if allocated_power[p["name"]] > p["pmin_scaled"]
            ]
            if not candidates:
                raise ValueError("Cannot decrease power to match load")
            plant = max(candidates, key=lambda p: p["marginal_cost"])
            allocated_power[plant["name"]] -= 1
            remaining_load += 1

    response = [{"name": name, "p": allocated_power[name] / SCALE} for name in allocated_power]
    logger.info("Allocation completed successfully")
    return response

@app.post("/productionplan")
async def production_plan(payload: Payload):
    try:
        load = payload.load
        fuels = payload.fuels.dict()
        powerplants = [p.dict() for p in payload.powerplants]
        result = allocate_power(load, fuels, powerplants, include_co2=True)
        return result
    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)