"""
trading_service.py

Combines AI intelligence,
decision making,
trade planning,
risk validation,
risk gating,
approval,
execution,
and AI reasoning.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from app.decision.decision_engine import (
    DecisionEngine,
)

from app.planning.trade_planner import (
    TradePlanner,
)

from app.risk.risk_validator import (
    RiskValidator,
)

from app.risk.risk_gate import (
    RiskGate,
)

from app.approval.approval_manager import (
    ApprovalManager,
)

from app.execution.execution_manager import (
    ExecutionManager,
)

from app.intelligence.intelligence_service import (
    IntelligenceService,
)

from app.journal.ai_trade_reason import (
    AITradeReasonGenerator,
)

from app.intelligence.reasoning_engine import (
    ReasoningEngine,
)

from app.services.market_intelligence_service import (
    MarketIntelligenceService,
)


class TradingService:
    """
    Coordinates the complete Aladdin trading workflow.
    """

    # ======================================================
    # BASIC TRADE SETUP
    # ======================================================

    @staticmethod
    def generate_trade_setup(
        symbol,
        trend,
        momentum,
        risk_reward,
        entry_price,
        stop_loss,
        take_profit,
        account_balance,
        risk_percent,
        trade_risk_amount,
        lot_size,
        execute=False,
        execution_service=None,
        user_id=None,
    ):
        """
        Generate a basic trade setup.

        This method is kept backward compatible with
        the existing basic trading workflow.
        """

        # ==========================================
        # Basic Decision
        # ==========================================

        decision = DecisionEngine.make_decision(
            trend=trend,
            momentum=momentum,
            risk_reward=risk_reward,
        )

        result = {
            "decision": decision,
        }

        # ==========================================
        # HOLD
        # ==========================================

        if decision.action == "HOLD":
            return result

        # ==========================================
        # Trade Plan
        # ==========================================

        trade_plan = TradePlanner.create_plan(
            symbol=symbol,
            direction=decision.action,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )

        # ==========================================
        # Existing Basic Risk Validation
        # ==========================================

        risk_validation = RiskValidator.validate(
            account_balance=account_balance,
            risk_percent=risk_percent,
            trade_risk_amount=trade_risk_amount,
            risk_reward=trade_plan.risk_reward,
        )

        approval = ApprovalManager.approve_trade(
            risk_validation,
        )

        result["trade_plan"] = trade_plan
        result["risk_validation"] = risk_validation
        result["approval"] = approval

        # ==========================================
        # Execution
        # ==========================================

        if approval.approved:

            execution_request = (
                ExecutionManager.prepare_execution(
                    symbol=symbol,
                    direction=decision.action,
                    lot_size=lot_size,
                    approved=True,
                )
            )

            result["execution"] = execution_request

            if execute:

                if execution_service is None:
                    raise ValueError(
                        "Execution service required."
                    )

                if user_id is None:
                    raise ValueError(
                        "User ID required."
                    )

                execution_result = (
                    execution_service.execute_trade(
                        user_id=user_id,
                        execution_request=execution_request,
                    )
                )

                result["execution_result"] = (
                    execution_result
                )

        return result

    # ======================================================
    # LEGACY INTELLIGENT MARKET ANALYSIS
    # ======================================================

    @staticmethod
    def generate_intelligent_trade_setup(
        ema_signal,
        rsi_value,
        adx_value,
        volatility,
        currency,
        event_type,
        importance,
        sentiment,
        price_structure="BOS_BULLISH",
        liquidity_sweep=True,
        order_block="BULLISH",
        fair_value_gap=True,
        higher_timeframe_bias="BULLISH",
        middle_timeframe_bias="BULLISH",
        entry_timeframe_bias="BULLISH",
        hour_utc=None,
    ):
        """
        Generate intelligent market analysis
        using manually supplied analysis values.

        This method is kept for backward compatibility.

        The main live AI workflow should use
        MarketIntelligenceService instead.
        """

        market_intelligence = (
            IntelligenceService.analyze_market(
                ema_signal=ema_signal,
                rsi_value=rsi_value,
                adx_value=adx_value,
                volatility=volatility,
                currency=currency,
                event_type=event_type,
                importance=importance,
                sentiment=sentiment,
                price_structure=price_structure,
                liquidity_sweep=liquidity_sweep,
                order_block=order_block,
                fair_value_gap=fair_value_gap,
                higher_timeframe_bias=(
                    higher_timeframe_bias
                ),
                middle_timeframe_bias=(
                    middle_timeframe_bias
                ),
                entry_timeframe_bias=(
                    entry_timeframe_bias
                ),
                hour_utc=hour_utc,
            )
        )

        decision = (
            DecisionEngine.make_intelligent_decision(
                market_intelligence,
            )
        )

        return {
            "market_intelligence": market_intelligence,
            "decision": decision,
        }

    # ======================================================
    # AI TRADE SETUP
    # ======================================================

    @staticmethod
    def generate_ai_trade_setup(
        symbol,
        ema_signal,
        rsi_value,
        adx_value,
        volatility,
        currency,
        event_type,
        importance,
        sentiment,
        entry_price,
        stop_loss,
        take_profit,
        account_balance,
        risk_percent,
        trade_risk_amount,
        lot_size,
        pip_value=10.0,
        price_structure="BOS_BULLISH",
        liquidity_sweep=True,
        order_block="BULLISH",
        fair_value_gap=True,
        higher_timeframe_bias="BULLISH",
        middle_timeframe_bias="BULLISH",
        entry_timeframe_bias="BULLISH",
        hour_utc=None,
    ):
        """
        Generate a complete AI-powered trade setup.

        IMPORTANT:
        The trading decision is generated from the
        backend live market intelligence pipeline.

        The legacy frontend analysis parameters are
        still accepted temporarily for API compatibility,
        but they do NOT control the live trading decision.

        Workflow:

        1. Live market intelligence
        2. Decision Gate
        3. Trade planning
        4. Risk Gate
        5. Risk validation
        6. Trade approval
        7. Explainable AI reasoning

        This method does not execute a trade.
        """

        # ==========================================
        # Real Backend Market Intelligence
        # ==========================================
        #
        # Do NOT build the live decision using:
        #
        # ema_signal
        # rsi_value
        # adx_value
        # volatility
        # sentiment
        # price_structure
        # higher_timeframe_bias
        #
        # Those parameters remain only for temporary
        # backward compatibility with the frontend.
        #
        # Real analysis comes from:
        #
        # MT5
        # Technical Analysis
        # Market Structure
        # Multi-Timeframe Analysis
        # Market Session
        # News Analysis
        # Market Intelligence Agent
        # ==========================================

        market_service = MarketIntelligenceService()

        try:

            market_result = market_service.analyze(
                symbol=symbol,
            )

            market_intelligence = (
                market_result["intelligence"]
            )

            # ======================================
            # Detailed Decision Gate
            # ======================================

            decision = (
                DecisionEngine.evaluate_gate(
                    market_intelligence,
                )
            )

            result = {
                "market_intelligence": (
                    market_intelligence
                ),
                "decision": decision,
            }

        finally:

            market_service.close()

        # ==========================================
        # Decision Gate Returned HOLD
        # ==========================================
        #
        # If the intelligent safety gate does not
        # approve the market conditions, no trade
        # planning or execution preparation occurs.
        # ==========================================

        if (
            decision.action == "HOLD"
            or not decision.approved
        ):
            return result

        # ==========================================
        # Trade Plan
        # ==========================================

        trade_plan = TradePlanner.create_plan(
            symbol=symbol,
            direction=decision.action,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )

        # ==========================================
        # Risk Gate
        # ==========================================

        risk_gate = RiskGate.evaluate(
            symbol=symbol,
            account_balance=account_balance,
            risk_percent=risk_percent,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            lot_size=lot_size,
            pip_value=pip_value,
        )

        # ==========================================
        # Risk Validation
        # ==========================================
        #
        # The Risk Gate and Risk Validator are
        # separate safety checks.
        #
        # Keep trade_risk_amount supplied to this
        # workflow for RiskValidator.
        # ==========================================

        risk_validation = RiskValidator.validate(
            account_balance=account_balance,
            risk_percent=risk_percent,
            trade_risk_amount=trade_risk_amount,
            risk_reward=trade_plan.risk_reward,
        )

        # ==========================================
        # Approval Layer
        # ==========================================

        approval = ApprovalManager.approve_trade(
            risk_validation,
        )

        # ==========================================
        # Explainable AI Reasoning
        # ==========================================

        reasoning = AITradeReasonGenerator.generate(
            decision=decision,
            market_intelligence=(
                result["market_intelligence"]
            ),
            risk_validation=risk_validation,
        )

        # ==========================================
        # Store Results
        # ==========================================

        result["trade_plan"] = trade_plan

        result["risk_gate"] = risk_gate

        result["risk_validation"] = (
            risk_validation
        )

        result["approval"] = approval

        result["reasoning"] = reasoning

        return result

    # ======================================================
    # AI EXECUTION WORKFLOW
    # ======================================================

    @staticmethod
    def generate_ai_execution_workflow(
        symbol,
        ema_signal,
        rsi_value,
        adx_value,
        volatility,
        currency,
        event_type,
        importance,
        sentiment,
        entry_price,
        stop_loss,
        take_profit,
        account_balance,
        risk_percent,
        trade_risk_amount,
        lot_size,
        pip_value=10.0,
        execute=False,
        execution_service=None,
        notification_service=None,
        user_id=None,
        price_structure="BOS_BULLISH",
        liquidity_sweep=True,
        order_block="BULLISH",
        fair_value_gap=True,
        higher_timeframe_bias="BULLISH",
        middle_timeframe_bias="BULLISH",
        entry_timeframe_bias="BULLISH",
        hour_utc=None,
    ):
        """
        Generate the complete AI trading workflow.

        A trade can only reach MT5 execution when:

        1. Decision Gate approves the trade.
        2. Risk Gate approves the trade.
        3. Risk Validation approves the trade.
        4. Approval layer approves the trade.
        5. Execution is explicitly requested.
        """

        # ==========================================
        # Generate AI Trade Setup
        # ==========================================

        result = (
            TradingService.generate_ai_trade_setup(
                symbol=symbol,
                ema_signal=ema_signal,
                rsi_value=rsi_value,
                adx_value=adx_value,
                volatility=volatility,
                currency=currency,
                event_type=event_type,
                importance=importance,
                sentiment=sentiment,
                price_structure=price_structure,
                liquidity_sweep=liquidity_sweep,
                order_block=order_block,
                fair_value_gap=fair_value_gap,
                higher_timeframe_bias=(
                    higher_timeframe_bias
                ),
                middle_timeframe_bias=(
                    middle_timeframe_bias
                ),
                entry_timeframe_bias=(
                    entry_timeframe_bias
                ),
                hour_utc=hour_utc,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                account_balance=account_balance,
                risk_percent=risk_percent,
                trade_risk_amount=(
                    trade_risk_amount
                ),
                lot_size=lot_size,
                pip_value=pip_value,
            )
        )

        decision = result.get(
            "decision"
        )

        # ==========================================
        # Explainable AI Reasoning Fallback
        # ==========================================
        #
        # BUY/SELL setups normally receive the
        # richer AITradeReasonGenerator reasoning
        # inside generate_ai_trade_setup().
        #
        # HOLD returns before risk processing, so
        # ReasoningEngine is used as a fallback.
        # ==========================================

        if (
            decision is not None
            and "reasoning" not in result
        ):

            risk_approved = False

            if "risk_gate" in result:

                risk_approved = bool(
                    result["risk_gate"].approved
                )

            elif "approval" in result:

                risk_approved = bool(
                    result["approval"].approved
                )

            # ======================================
            # Confidence Compatibility
            # ======================================
            #
            # Old DecisionResult:
            #     decision.confidence
            #
            # New Decision Gate result:
            #     decision.decision_confidence
            #
            # Support both safely.
            # ======================================

            decision_confidence = getattr(
                decision,
                "decision_confidence",
                None,
            )

            if decision_confidence is None:

                decision_confidence = getattr(
                    decision,
                    "confidence",
                    0.0,
                )

            reasoning = ReasoningEngine.generate(
                decision=decision.action,
                confidence=decision_confidence,
                ema_signal=ema_signal,
                rsi_value=rsi_value,
                adx_value=adx_value,
                price_structure=price_structure,
                liquidity_sweep=liquidity_sweep,
                risk_approved=risk_approved,
            )

            result["reasoning"] = reasoning

        # ==========================================
        # No Trade Approval
        # ==========================================

        if "approval" not in result:
            return result

        # ==========================================
        # Decision Gate Safety Check
        # ==========================================

        if (
            decision is None
            or decision.action == "HOLD"
            or not getattr(
                decision,
                "approved",
                False,
            )
        ):
            return result

        # ==========================================
        # Risk Gate Safety Check
        # ==========================================

        risk_gate = result.get(
            "risk_gate"
        )

        if (
            risk_gate is None
            or not risk_gate.approved
        ):
            return result

        # ==========================================
        # Final Approval Safety Check
        # ==========================================

        approval = result.get(
            "approval"
        )

        if (
            approval is None
            or not approval.approved
        ):
            return result

        # ==========================================
        # Do Not Execute Unless Requested
        # ==========================================

        if not execute:
            return result

        # ==========================================
        # Validate Execution Dependencies
        # ==========================================

        if execution_service is None:
            raise ValueError(
                "Execution service required."
            )

        if user_id is None:
            raise ValueError(
                "User ID required."
            )

        # ==========================================
        # Prepare Approved Execution
        # ==========================================

        execution_request = (
            ExecutionManager.prepare_execution(
                symbol=symbol,
                direction=decision.action,
                lot_size=lot_size,
                approved=True,
            )
        )

        # ==========================================
        # Execute Through Execution Service
        # ==========================================

        execution_result = (
            execution_service.execute_trade(
                user_id=user_id,
                execution_request=(
                    execution_request
                ),
            )
        )

        result["execution"] = (
            execution_request
        )

        result["execution_result"] = (
            execution_result
        )

        # ==========================================
        # Execution Notification
        # ==========================================

        if notification_service is not None:

            if (
                execution_result.status
                == "EXECUTED"
            ):

                notification_service.create_notification(
                    user_id=user_id,
                    notification_type=(
                        "TRADE_EXECUTED"
                    ),
                    title="Trade Executed",
                    message=(
                        f"{symbol} "
                        f"{decision.action} "
                        "trade was successfully executed."
                    ),
                    priority="SUCCESS",
                )

            elif (
                execution_result.status
                == "FAILED"
            ):

                notification_service.create_notification(
                    user_id=user_id,
                    notification_type=(
                        "TRADE_EXECUTION_FAILED"
                    ),
                    title=(
                        "Trade Execution Failed"
                    ),
                    message=(
                        f"{symbol} "
                        f"{decision.action} "
                        "trade could not be executed."
                    ),
                    priority="WARNING",
                )

        return result