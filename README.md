# 🚀 Aladdin Forex AI

> **AI-Powered Multi-Agent Forex Trading Assistant**

Aladdin Forex AI is a portfolio-quality final-year project built to demonstrate modern software engineering, artificial intelligence concepts, and Forex trading workflows.

The system helps traders analyze the market, manage risk, plan trades, record trading activity, and support better decision-making using AI-assisted workflows.

> **Note:** Aladdin is an AI trading assistant. It is **not** a guaranteed-profit trading bot and does not execute trades without user control.

---

# 📖 Project Overview

Aladdin is designed using a modular architecture so that each part of the trading workflow can evolve independently.

The project combines:

- Artificial Intelligence concepts
- Multi-agent architecture
- Market analysis
- Risk management
- Trade planning
- Trading journal
- Performance analytics
- REST API development
- Docker deployment
- PostgreSQL integration

The long-term goal is to build an intelligent trading assistant that helps traders make structured and explainable decisions.

---

# ✨ Key Features

## 🧠 AI Market Analysis

- Technical market analysis
- Trend detection
- Momentum evaluation
- Market structure analysis
- Liquidity concepts
- News sentiment support

---

## 📊 AI Decision Engine

Generates trading recommendations:

- BUY
- SELL
- HOLD

using market conditions and confidence scoring.

---

## 🛡️ Risk Management

Supports:

- Risk percentage calculation
- Position sizing
- Stop-loss validation
- Risk-reward calculation

---

## 📋 Trade Planning

Provides:

- Entry price
- Stop loss
- Take profit
- Lot size calculation
- Risk validation

---

## ⚡ Trade Execution

Supports:

- Execution workflow
- Broker integration architecture
- MT5-ready design
- Execution history

---

## 📖 Trading Journal

Stores:

- Trade history
- Strategy
- Trading reasons
- Lessons learned
- Performance records

---

## 🤖 Explainable AI

Provides:

- Decision explanations
- Confidence scores
- Trade reasoning
- Future AI coaching support

---

---
# 🚀 Aladdin Forex AI

> **AI-Powered Multi-Agent Forex Trading Assistant**

Aladdin Forex AI is a portfolio-quality final-year project built to demonstrate modern software engineering, artificial intelligence concepts, and Forex trading workflows.

The system helps traders analyze the market, manage risk, plan trades, record trading activity, and support better decision-making using AI-assisted workflows.

> **Note:** Aladdin is an AI trading assistant. It is **not** a guaranteed-profit trading bot and does not execute trades without user control.

---

# 📖 Project Overview

Aladdin is designed using a modular architecture so that each part of the trading workflow can evolve independently.

The project combines:

- Artificial Intelligence concepts
- Multi-agent architecture
- Market analysis
- Risk management
- Trade planning
- Trading journal
- Performance analytics
- REST API development
- Docker deployment
- PostgreSQL integration

The long-term goal is to build an intelligent trading assistant that helps traders make structured and explainable decisions.

---

# ✨ Key Features

# 🛠️ Technology Stack

## Backend

- Python 3.14
- FastAPI
- SQLAlchemy
- Pydantic v2

## Database

- SQLite (Development)
- PostgreSQL (Production)
- JSON Repository

## DevOps

- Docker
- Docker Compose
- GitHub Actions CI

## Testing

- Pytest

## Future AI

- LangGraph
- OpenAI API
- MetaTrader 5
- Machine Learning

---

## 🧠 AI Market Analysis

- Technical market analysis
- Trend detection
- Momentum evaluation
- Market structure analysis
- Liquidity concepts
- News sentiment support

---

## 📊 AI Decision Engine

Generates trading recommendations:

- BUY
- SELL
- HOLD

using market conditions and confidence scoring.

---

## 🛡️ Risk Management

Supports:

- Risk percentage calculation
- Position sizing
- Stop-loss validation
- Risk-reward calculation

---

## 📋 Trade Planning

Provides:

- Entry price
- Stop loss
- Take profit
- Lot size calculation
- Risk validation

---

## ⚡ Trade Execution

Supports:

- Execution workflow
- Broker integration architecture
- MT5-ready design
- Execution history

---

## 📖 Trading Journal

Stores:

- Trade history
- Strategy
- Trading reasons
- Lessons learned
- Performance records

---

## 🤖 Explainable AI

Provides:

- Decision explanations
- Confidence scores
- Trade reasoning
- Future AI coaching support

---

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/nvtharindukothalawala-tech/Aladdin-forex-ai.git
cd Aladdin-forex-ai
```

---

## 2. Create a Virtual Environment

```bash
python -m venv .venv
```

---

## 3. Activate the Virtual Environment

### Windows

```powershell
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

---

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 5. Configure Environment Variables

Create a `.env` file.

Example:

```env
APP_NAME=Aladdin Forex AI
ENVIRONMENT=development
DATABASE_URL=sqlite:///./aladdin.db
LOG_LEVEL=INFO
```

---

## 6. Run the Application

```bash
uvicorn app.api.main:app --reload
```

The API will be available at:

```
http://localhost:8000
```

Swagger UI:

```
http://localhost:8000/docs
```

Health Check:

```
http://localhost:8000/health
```

---

# 🐳 Docker Deployment

## Development

Build and start:

```bash
docker compose up --build
```

Stop:

```bash
docker compose down
```

---

## Production

Build and start:

```bash
docker compose -f docker-compose.prod.yml up --build
```

Stop:

```bash
docker compose -f docker-compose.prod.yml down
```

The production environment includes:

- FastAPI
- PostgreSQL
- Docker networking
- Health checks
- Environment-based configuration

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/nvtharindukothalawala-tech/Aladdin-forex-ai.git
cd Aladdin-forex-ai
```

---

## 2. Create a Virtual Environment

```bash
python -m venv .venv
```

---

## 3. Activate the Virtual Environment

### Windows

```powershell
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

---

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 5. Configure Environment Variables

Create a `.env` file.

Example:

```env
APP_NAME=Aladdin Forex AI
ENVIRONMENT=development
DATABASE_URL=sqlite:///./aladdin.db
LOG_LEVEL=INFO
```

---

## 6. Run the Application

```bash
uvicorn app.api.main:app --reload
```

The API will be available at:

```
http://localhost:8000
```

Swagger UI:

```
http://localhost:8000/docs
```

Health Check:

```
http://localhost:8000/health
```

---

# 🐳 Docker Deployment

## Development

Build and start:

```bash
docker compose up --build
```

Stop:

```bash
docker compose down
```

---

## Production

Build and start:

```bash
docker compose -f docker-compose.prod.yml up --build
```

Stop:

```bash
docker compose -f docker-compose.prod.yml down
```

The production environment includes:

- FastAPI
- PostgreSQL
- Docker networking
- Health checks
- Environment-based configuration

---

# 🚀 Aladdin Forex AI

> **AI-Powered Multi-Agent Forex Trading Assistant**

Aladdin Forex AI is a portfolio-quality final-year project built to demonstrate modern software engineering, artificial intelligence concepts, and Forex trading workflows.

The system helps traders analyze the market, manage risk, plan trades, record trading activity, and support better decision-making using AI-assisted workflows.

> **Note:** Aladdin is an AI trading assistant. It is **not** a guaranteed-profit trading bot and does not execute trades without user control.

---

# 📖 Project Overview

Aladdin is designed using a modular architecture so that each part of the trading workflow can evolve independently.

The project combines:

- Artificial Intelligence concepts
- Multi-agent architecture
- Market analysis
- Risk management
- Trade planning
- Trading journal
- Performance analytics
- REST API development
- Docker deployment
- PostgreSQL integration

The long-term goal is to build an intelligent trading assistant that helps traders make structured and explainable decisions.

---

# ✨ Key Features

# 🛠️ Technology Stack

## Backend

- Python 3.14
- FastAPI
- SQLAlchemy
- Pydantic v2

## Database

- SQLite (Development)
- PostgreSQL (Production)
- JSON Repository

## DevOps

- Docker
- Docker Compose
- GitHub Actions CI

## Testing

- Pytest

## Future AI

- LangGraph
- OpenAI API
- MetaTrader 5
- Machine Learning

---

## 🧠 AI Market Analysis

- Technical market analysis
- Trend detection
- Momentum evaluation
- Market structure analysis
- Liquidity concepts
- News sentiment support

---

## 📊 AI Decision Engine

Generates trading recommendations:

- BUY
- SELL
- HOLD

using market conditions and confidence scoring.

---

## 🛡️ Risk Management

Supports:

- Risk percentage calculation
- Position sizing
- Stop-loss validation
- Risk-reward calculation

---

## 📋 Trade Planning

Provides:

- Entry price
- Stop loss
- Take profit
- Lot size calculation
- Risk validation

---

## ⚡ Trade Execution

Supports:

- Execution workflow
- Broker integration architecture
- MT5-ready design
- Execution history

---

## 📖 Trading Journal

Stores:

- Trade history
- Strategy
- Trading reasons
- Lessons learned
- Performance records

---

## 🤖 Explainable AI

Provides:

- Decision explanations
- Confidence scores
- Trade reasoning
- Future AI coaching support

---

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/nvtharindukothalawala-tech/Aladdin-forex-ai.git
cd Aladdin-forex-ai
```

---

## 2. Create a Virtual Environment

```bash
python -m venv .venv
```

---

## 3. Activate the Virtual Environment

### Windows

```powershell
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

---

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 5. Configure Environment Variables

Create a `.env` file.

Example:

```env
APP_NAME=Aladdin Forex AI
ENVIRONMENT=development
DATABASE_URL=sqlite:///./aladdin.db
LOG_LEVEL=INFO
```

---

## 6. Run the Application

```bash
uvicorn app.api.main:app --reload
```

The API will be available at:

```
http://localhost:8000
```

Swagger UI:

```
http://localhost:8000/docs
```

Health Check:

```
http://localhost:8000/health
```

---

# 🐳 Docker Deployment

## Development

Build and start:

```bash
docker compose up --build
```

Stop:

```bash
docker compose down
```

---

## Production

Build and start:

```bash
docker compose -f docker-compose.prod.yml up --build
```

Stop:

```bash
docker compose -f docker-compose.prod.yml down
```

The production environment includes:

- FastAPI
- PostgreSQL
- Docker networking
- Health checks
- Environment-based configuration

---

# 🧪 Running Tests

Run the complete test suite:

```bash
pytest
```

Current project status:

- ✅ 155 tests passing

---

# 🔄 Continuous Integration

The project uses GitHub Actions to automatically:

- Run the complete Pytest test suite
- Verify Docker image builds
- Validate every push to the `main` branch

---

# 🗺️ Roadmap

Planned future enhancements include:

- Multi-agent orchestration
- MT5 live trading integration
- Economic news analysis
- AI coaching assistant
- Trading performance dashboard
- Web-based frontend
- User authentication improvements
- Machine learning enhancements

---

# 👨‍💻 Author

**Tharindu Kothalwala**

Bachelor of Science (Honours) in Information Technology  
Sri Lanka Technological Campus (SLTC)

Project: **Aladdin Forex AI**

---