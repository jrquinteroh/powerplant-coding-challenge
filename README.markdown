# Powerplant Production Plan API

REST API to calculate powerplant production plans based on load, fuel costs, and powerplant characteristics for the powerplant-coding-challenge.

## Prerequisites
- Python 3.8+
- pip
- Git
- Docker (optional)

## Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/powerplant-coding-challenge.git
   cd powerplant-coding-challenge
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Mac/Linux
   venv\Scripts\activate     # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the API:
   ```bash
   python main.py
   ```
   API runs on `http://0.0.0.0:8888`.

## Usage
- **Endpoint**: `POST /productionplan`
- **Payload**: JSON from `example_payloads/` (e.g., `payload3.json`).
- **Example**:
   ```bash
   curl -X POST "http://localhost:8888/productionplan" -H "Content-Type: application/json" -d @example_payloads/payload3.json
   ```
   Response:
   ```json
   [
     {"name": "gasfiredbig1", "p": 460.0},
     {"name": "gasfiredbig2", "p": 338.4},
     {"name": "gasfiredsomewhatsmaller", "p": 0.0},
     {"name": "tj1", "p": 0.0},
     {"name": "windpark1", "p": 90.0},
     {"name": "windpark2", "p": 21.6}
   ]
   ```

## Notes
- CO2 costs: 0.3 ton/MWh for gas-fired plants.
- Errors: Logged to console; HTTP 422 for validation, 500 for internal.
- Use virtual environment to avoid conflicts.

## Docker
1. Build image:
   ```bash
   docker build -t production-plan-api .
   ```
2. Run container:
   ```bash
   docker run -p 8888:8888 production-plan-api
   ```

## License
MIT