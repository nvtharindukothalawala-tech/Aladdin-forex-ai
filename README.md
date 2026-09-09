# Aladdin Forex AI

## AI-Powered Multi-Agent Forex Trading Assistant

Aladdin is a final-year university software project designed as an AI-powered Forex trading assistant.

The system combines technical analysis, market structure analysis, multi-timeframe analysis, market session analysis, economic news analysis, decision gating, risk management, explainable reasoning, trade planning, journaling, performance analytics, coaching, and a controlled trade execution workflow.

Aladdin is designed to support trading decisions. It is not a guaranteed-profit trading bot and should not be considered financial advice.

> Important: The current project uses a controlled development news provider for economic news analysis and simulated MT5 order execution for safe testing. It does not currently submit real-money broker orders.


---

# 1. Project Overview

Forex trading decisions normally depend on several different types of information.

A trader may need to consider:

- Market trend
- RSI and momentum
- Trend strength
- Volatility
- Market structure
- Break of Structure (BOS)
- Change of Character (CHoCH)
- Liquidity
- Order blocks
- Fair Value Gaps (FVG)
- Multiple timeframes
- Trading sessions
- Economic news
- Risk level
- Stop loss
- Take profit
- Risk-to-reward ratio

Instead of using only one indicator, Aladdin separates these responsibilities into different analysis components.

The results are combined by the Market Intelligence layer before the Decision Gate determines whether a trade is safe enough to continue.

The possible final decisions are:

- BUY
- SELL
- HOLD

A BUY or SELL signal does not automatically mean that a trade will be executed.

The trade must pass several safety layers first.


---

# 2. Main Objective

The main objective of Aladdin is to develop a modular Forex trading assistant that can:

1. Analyze market data.
2. Understand technical conditions.
3. Identify market structure.
4. Compare multiple timeframes.
5. Consider the current Forex market session.
6. Include economic news information.
7. Combine different analysis results.
8. Make an explainable BUY, SELL, or HOLD decision.
9. Block unsafe trading opportunities.
10. Create a trade plan.
11. Validate risk.
12. Require final approval before execution.
13. Maintain trading records and performance information.
14. Provide explainable feedback to the user.


---

# 3. System Architecture

The current Aladdin trading workflow follows this architecture:

```text
                   MT5 Market Data
                         |
                         v
        +--------------------------------+
        |      Market Analysis Layer     |
        +--------------------------------+
          |        |        |       |
          v        v        v       v
      Technical  Market     MTF   Market
      Analysis   Structure        Session
          |        |        |       |
          +--------+--------+-------+
                   |
                   |       Development
                   |       News Provider
                   |             |
                   +-------------+
                         |
                         v
              Market Intelligence
                         |
                         v
                  Decision Gate
                         |
            +------------+------------+
            |                         |
            v                         v
          HOLD                  BUY / SELL
                                      |
                                      v
                               Trade Planning
                                      |
                                      v
                                  Risk Gate
                                      |
                                      v
                               Risk Validation
                                      |
                                      v
                                Final Approval
                                      |
                                      v
                                Explainability
                                      |
                                      v
                          Simulated MT5 Execution

The important design principle is that market analysis and trade execution are separated.

A market signal alone cannot directly execute a trade.

4. Multi-Agent Intelligence Architecture

Aladdin uses multiple specialized analysis components instead of putting all responsibilities inside one large class.

Important intelligence modules include:

app/intelligence/
|
|-- technical_agent.py
|-- market_structure_agent.py
|-- multi_timeframe_agent.py
|-- market_session_agent.py
|-- news_agent.py
|-- market_intelligence.py
|-- reasoning_engine.py

Each component has a different responsibility.

Technical Agent

The Technical Agent analyzes technical market information such as:

Market trend
EMA-based direction
RSI
ADX
Volatility

Its purpose is to identify whether technical conditions are bullish, bearish, or weak.

Market Structure Agent

The Market Structure Agent examines price-action structure.

It supports concepts such as:

Swing highs
Swing lows
Break of Structure (BOS)
Change of Character (CHoCH)
Liquidity sweeps
Order blocks
Fair Value Gaps

These features help the system understand how price is behaving instead of depending only on indicators.

Multi-Timeframe Agent

Aladdin compares three important Forex timeframes:

H4  -> Higher timeframe
H1  -> Main analysis timeframe
M15 -> Entry timeframe

The system classifies timeframe alignment as:

FULL
PARTIAL
WEAK
NONE

Example:

H4  = BULLISH
H1  = BULLISH
M15 = BULLISH

Alignment = FULL

Strong timeframe agreement gives more confidence to the trading setup.

Weak or conflicting timeframe conditions may cause the Decision Gate to block the trade.

Market Session Agent

Forex market conditions can change depending on the trading session.

Aladdin identifies market sessions such as:

Asian
London
New York
London/New York overlap

It also evaluates session activity.

Low-activity market conditions can block a trade.

News Agent

The News Agent evaluates economic-event information and produces market sentiment information.

It considers factors such as:

Currency
Event type
Importance
Actual value
Forecast value
Market sentiment
Current News Limitation

The current version uses:

DevelopmentNewsProvider

This contains controlled sample economic events for development and testing.

Therefore:

The current economic-news data must not be described as live news.

A real external economic-calendar provider can be integrated in a future version.

5. Market Intelligence

The Market Intelligence layer combines the outputs produced by the different analysis components.

The current main weighting is:

Technical Analysis       = 40%
Market Structure         = 40%
Economic News            = 20%

The combined result produces information such as:

Market bias
Market confidence
Risk level
Structure direction
Structure confirmation
Multi-timeframe alignment
Timeframe confidence
Market session
Session activity
Recommendation

Possible market biases include:

BULLISH
BEARISH
NEUTRAL

The Market Intelligence layer does not directly execute trades.

Its result must first be evaluated by the Decision Gate.

6. Decision Gate

The Decision Gate is one of the most important safety components in Aladdin.

It prevents a strong-looking market signal from automatically becoming a trade.

The Decision Gate checks several conditions.

Gate 1 - Multi-Timeframe Alignment

Accepted:

FULL
PARTIAL

Blocked:

WEAK
NONE
Gate 2 - Market Session

A LOW-activity market session blocks the trade.

Gate 3 - Decision Confidence

Aladdin calculates decision confidence using:

Market Intelligence Confidence = 70%
Multi-Timeframe Confidence      = 30%

The minimum required confidence is:

70%
Gate 4 - Market Bias

The final market bias must be clearly:

BULLISH

or:

BEARISH
Gate 5 - Market Structure Direction

The structure direction must agree with the market bias.

Example:

Market Bias = BULLISH
Structure   = BULLISH

PASS

Example:

Market Bias = BULLISH
Structure   = BEARISH

BLOCK
Gate 6 - Break of Structure Confirmation

For a bullish trade:

BOS_BULLISH

must confirm the structure.

For a bearish trade:

BOS_BEARISH

must confirm the structure.

Gate 7 - Risk Level

Only:

LOW

risk is allowed through the Decision Gate.

Example:

Bias       = BULLISH
Confidence = 84%
MTF        = FULL
Structure  = BULLISH
BOS        = BOS_BULLISH
Risk       = MEDIUM

Final result:

HOLD

The trade is blocked because the risk level is not LOW.

High Opportunity Session Bonus

A high-opportunity trading session can add:

+5 confidence

to the final decision confidence.

7. Decision Flow

The general decision process is:

Market Intelligence
        |
        v
Decision Gate
        |
        +---- Unsafe Conditions ----> HOLD
        |
        v
BUY / SELL
        |
        v
Trade Planner
        |
        v
Risk Gate
        |
        v
Risk Validator
        |
        v
Final Approval
        |
        v
Explainability
        |
        v
Execution Layer

This design provides multiple safety checkpoints before execution.

8. Risk Management

Risk management is a major part of Aladdin.

Important modules include:

app/risk/
|
|-- risk_manager.py
|-- risk_validator.py
|-- risk_gate.py
|-- risk_gate_result.py

The risk system supports calculations and checks such as:

Account balance
Risk percentage
Trade risk amount
Stop-loss distance
Position size
Forex lot size
Pip size
Risk-to-reward ratio
Trade-risk validation
Example

For an account balance of:

$10,000

with:

Risk = 1%

the theoretical maximum risk amount is:

$100

The risk layer checks whether the proposed trade follows the configured safety rules.

9. Trade Planning

The Trade Planner creates a structured trading setup after the Decision Gate approves the market opportunity.

Important modules:

app/planning/
|
|-- trade_plan.py
|-- trade_planner.py

A trade plan can include:

Trading symbol
BUY or SELL direction
Entry price
Stop loss
Take profit
Risk-to-reward information

An invalid trade plan can be rejected before execution.

10. Approval Layer

Aladdin includes a dedicated approval stage.

This helps maintain separation between:

Analysis

and:

Execution

The final trade must satisfy the required decision and risk conditions before approval.

11. Explainable AI Reasoning

Aladdin does not only return:

BUY
SELL
HOLD

The project includes reasoning components that explain why a decision was generated.

The reasoning layer can describe:

Technical reasons
Market-structure reasons
Risk reasons
Multi-timeframe reasons
Session reasons
Passed Decision Gates
Failed Decision Gates
Final decision reason

Example:

Decision: HOLD

Reason:
Trade blocked because risk level is MEDIUM.

Passed Gates:
- Multi-timeframe alignment
- Market session
- Confidence
- Market bias
- Market structure direction
- BOS confirmation

Failed Gates:
- Risk level

This is important because financial decision-support systems should provide understandable reasoning instead of only displaying a final prediction.

12. MT5 Integration

Aladdin contains an MT5 integration layer:

app/mt5/
|
|-- mt5_connector.py
|-- models.py

The wider project can obtain Forex market information through the market-data pipeline.

However, the current dedicated order execution connector is intentionally simulated for development safety.

Current Execution Status

When a simulated order is successful, the development connector can return an order ID such as:

MOCK_ORDER_001

This means the current version demonstrates the complete software execution workflow without submitting real-money broker orders.

Future Integration

A future production version could replace the simulated connector with actual MetaTrader 5 order submission.

Real execution should only be enabled after adding additional safeguards, testing, configuration management, and broker-specific validation.

13. Economic News Status

Aladdin currently includes:

app/news/
|
|-- development_news_provider.py
|-- economic_news_provider.py

The development provider allows the complete intelligence pipeline to be tested without requiring a paid news API.

Current development events are controlled sample data.

Therefore the current project demonstrates:

Economic News Analysis Architecture

but does not claim:

Live Economic News Feed

Future versions can connect the same service architecture to a real economic-calendar provider.

14. Supported Trading Instruments

The project is designed to support major Forex pairs and gold, including:

EURUSD
GBPUSD
AUDUSD
NZDUSD
USDCAD
USDCHF
USDJPY
XAUUSD

Symbol formatting may vary depending on the service or broker.

For example:

EURUSD

and:

EUR/USD

may be normalized internally.

15. Additional System Features

Aladdin contains modules for more than market prediction.

The project also includes functionality for:

User authentication
Accounts
Trade management
Trade journaling
Performance analytics
Execution history
Execution statistics
Notifications
AI trading coaching
Risk analytics
Trade analytics
16. Backend Technology

The backend is primarily developed using:

Python
FastAPI
Pydantic
SQLAlchemy
Pytest
MetaTrader 5 integration architecture

FastAPI provides the REST API between the Aladdin backend and the frontend.

17. Frontend Technology

The frontend is developed using:

Next.js
React
TypeScript
Tailwind CSS

Important frontend files include:

frontend/
|
|-- app/
|   |-- page.tsx
|   |-- layout.tsx
|   |-- globals.css
|
|-- lib/
    |-- api.ts

page.tsx contains the primary application interface.

api.ts handles communication between the frontend and FastAPI backend.

18. Decision Gate Dashboard

The frontend displays important information generated by the backend, including:

BUY / SELL / HOLD decision
Approval status
Market bias
Risk level
Market confidence
Decision confidence
Multi-timeframe alignment
Market structure
BOS confirmation
Market session
Passed Decision Gates
Failed Decision Gates
Entry price
Stop loss
Take profit
Risk-to-reward information
Execution result

The important design principle is:

The backend makes the market decision. The frontend displays the result.

The frontend does not independently create the final trading direction.

19. Project Structure

A simplified version of the project structure is:

Aladdin-forex-ai/
|
|-- .github/
|
|-- app/
|   |-- ai/
|   |-- analysis/
|   |-- analytics/
|   |-- api/
|   |-- approval/
|   |-- auth/
|   |-- broker/
|   |-- coaching/
|   |-- config/
|   |-- core/
|   |-- database/
|   |-- decision/
|   |-- dependencies/
|   |-- execution/
|   |-- intelligence/
|   |-- journal/
|   |-- market/
|   |-- models/
|   |-- mt5/
|   |-- news/
|   |-- planning/
|   |-- repositories/
|   |-- risk/
|   |-- schemas/
|   |-- services/
|   `-- utils/
|
|-- data/
|
|-- docs/
|
|-- frontend/
|
|-- tests/
|
|-- pytest.ini
`-- README.md
20. Backend Installation
Step 1 - Clone the Repository
git clone <repository-url>
cd Aladdin-forex-ai
Step 2 - Create a Virtual Environment

Windows:

python -m venv .venv
Step 3 - Activate the Virtual Environment

PowerShell:

.venv\Scripts\Activate.ps1

After activation:

(.venv)

should appear in the terminal.

Step 4 - Install Dependencies
pip install -r requirements.txt
Step 5 - Start the FastAPI Backend
uvicorn app.api.main:app --reload

The backend normally becomes available at:

http://127.0.0.1:8000
FastAPI Documentation

Swagger documentation:

http://127.0.0.1:8000/docs
21. Frontend Installation

Open another terminal:

cd frontend

Install frontend dependencies:

npm install

Start the development server:

npm run dev

The frontend normally becomes available at:

http://localhost:3000
22. Important API Workflows

Examples of important Aladdin endpoints include:

POST /trading/ai-analyze

Generates the AI-assisted trading analysis workflow.

POST /execution/ai-execute

Runs the server-side analysis, approval, risk, and controlled execution workflow.

GET /decision/intelligent/live/{symbol}

Generates the intelligent market decision for a supported symbol.

Additional API endpoints are available for:

Authentication
Market analysis
Risk calculations
Trading
Journaling
Performance
Coaching
Notifications
Execution history
Execution statistics

The complete current API can be viewed through:

http://127.0.0.1:8000/docs
23. Testing

Aladdin uses Pytest for automated backend testing.

Run the complete test suite with:

pytest -q

Final project verification:

258 tests collected
258 tests passed

The verified test suite includes coverage for areas such as:

Account management
Authentication
Technical analysis
Market intelligence
Market structure
Multi-timeframe analysis
Market-session analysis
Decision Engine
Decision Gate
Risk management
Risk validation
Trade planning
AI reasoning
AI execution workflow
Execution API
MT5 connector
Journaling
Performance analytics
Coaching
Notifications
Input validation
Safety-Critical Tests

Specific automated tests verify that:

Weak timeframe alignment -> HOLD
Low market activity      -> HOLD
Low confidence           -> HOLD
Structure conflict       -> HOLD
Wrong BOS confirmation   -> HOLD
Medium risk              -> HOLD
Failed risk gate         -> No execution
Failed final approval    -> No execution
Blocked decision         -> No execution

This is important because Aladdin follows a defensive execution design.

24. Example Safe Decision

A market setup may contain:

Market Bias          = BULLISH
Market Confidence    = 78%
Structure            = BULLISH
BOS Confirmation     = BOS_BULLISH
MTF Alignment        = FULL
MTF Confidence       = 100%
Market Session       = LONDON
Session Activity     = HIGH
Risk Level           = MEDIUM

Even though most signals are strong, the final decision is:

HOLD

because:

Risk Level = MEDIUM

The Decision Gate requires:

Risk Level = LOW

before BUY or SELL can continue.

This demonstrates that Aladdin prioritizes risk control over simply generating more trades.

25. Development Safety

Aladdin is built as an educational and decision-support project.

Current safety principles include:

No guaranteed-profit claims
Risk-based Decision Gate
Multiple validation layers
HOLD as a valid final decision
Backend-controlled decision making
Risk validation before execution
Final approval before execution
Simulated broker order submission
Explainable decision reasoning
Automated safety tests
26. Current Limitations

The current version has several known limitations.

Economic News

Economic news is currently development/sample data and is not a real-time economic calendar.

Broker Execution

Dedicated MT5 order submission is currently simulated.

The project does not currently submit real-money broker trades through MetaTrader5.order_send().

News Interpretation

Economic-event interpretation is currently simplified and can be improved for indicators where a lower value may be positive or where interpretation depends on economic context.

Currency-Pair News

The current news workflow can be improved by analyzing both currencies in a Forex pair instead of using only one selected currency.

Machine Learning

The current system primarily uses rule-based and multi-agent intelligence. More advanced machine-learning models can be evaluated in future research instead of being added only for complexity.

Profitability

Passing software tests does not demonstrate trading profitability.

Trading strategy performance requires separate historical backtesting, forward testing, statistical evaluation, and risk analysis.

27. Future Development

Possible future improvements include:

Real-time economic calendar integration.
Pair-level economic-news aggregation.
Real MetaTrader 5 broker execution with strict safeguards.
Historical strategy backtesting.
Walk-forward testing.
Trading-performance evaluation.
Machine-learning experiments for market classification.
Improved explainable AI.
More advanced liquidity analysis.
Portfolio-level risk management.
Deployment and production monitoring.
Additional frontend visualization.
28. Why Aladdin Uses Multiple Agents

A single trading model can become difficult to understand and maintain.

Aladdin separates different responsibilities.

For example:

Technical Agent
    -> What is the technical trend?

Structure Agent
    -> What is price structure doing?

MTF Agent
    -> Do different timeframes agree?

Session Agent
    -> Is the current trading session suitable?

News Agent
    -> What does the economic event indicate?

Market Intelligence
    -> What is the combined market view?

Decision Gate
    -> Is the opportunity safe enough?

Risk Layer
    -> Is the planned trade acceptable?

Execution Layer
    -> Can the approved trade be executed?

This modular architecture improves:

Maintainability
Testing
Explainability
Safety
Extensibility
Debugging
29. Academic Purpose

Aladdin was developed as a final-year Information Technology project.

The project demonstrates practical knowledge in areas including:

Software engineering
Artificial intelligence architecture
Multi-agent systems
Forex market analysis
Algorithmic decision systems
Risk management
Explainable AI
REST API development
Frontend development
Automated testing
Database integration
Modular system design
30. Disclaimer

Aladdin is an educational and research-oriented software project.

It is not financial advice.

Forex trading involves significant financial risk, and no AI system can guarantee profitable trading results.

The current execution environment uses simulated order submission for safe development and demonstration purposes.

Author

Tharindu Kothalwala

BSc (Hons) in Information Technology
Sri Lanka Technological Campus (SLTC)

Final-Year Project: Aladdin - AI-Powered Multi-Agent Forex Trading Assistant


