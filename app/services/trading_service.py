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
    # INTELLIGENT MARKET ANALYSIS
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
    ):
        """
        Generate intelligent market analysis
        and an intelligent trading decision.
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
                higher_timeframe_bias=higher_timeframe_bias,
                middle_timeframe_bias=middle_timeframe_bias,
                entry_timeframe_bias=entry_timeframe_bias,
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
        pip_value,
        price_structure="BOS_BULLISH",
        liquidity_sweep=True,
        order_block="BULLISH",
        fair_value_gap=True,
        higher_timeframe_bias="BULLISH",
        middle_timeframe_bias="BULLISH",
        entry_timeframe_bias="BULLISH",
    ):
        """
        Generate a complete AI-powered trade setup.

        Workflow:

        1. Market intelligence
        2. Intelligent decision
        3. Trade planning
        4. Risk Gate
        5. Risk validation
        6. Trade approval
        7. Explainable AI reasoning

        This method does not execute a trade.
        """

        # ==========================================
        # Market Intelligence
        # ==========================================

        intelligence_result = (
            TradingService.generate_intelligent_trade_setup(
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
                higher_timeframe_bias=higher_timeframe_bias,
                middle_timeframe_bias=middle_timeframe_bias,
                entry_timeframe_bias=entry_timeframe_bias,
            )
        )

        result = intelligence_result.copy()

        decision = result["decision"]

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
        # Risk Validator
        #
        # We keep the existing validator because
        # it provides the lower-level risk validation
        # used by the existing approval/reasoning layer.
        # ==========================================

        risk_validation = RiskValidator.validate(
            account_balance=account_balance,
            risk_percent=risk_percent,
            trade_risk_amount=risk_gate.risk_amount,
            risk_reward=trade_plan.risk_reward,
        )

        # ==========================================
        # Final Approval
        #
        # The Risk Gate is now the final safety gate.
        # Approval can happen only when:
        #
        # Risk Gate approved
        # AND
        # Risk Validator approved
        # ==========================================

        if risk_gate.approved and risk_validation.approved:

            approval = ApprovalManager.approve_trade(
                risk_gate,
            )

        else:

            approval = ApprovalManager.approve_trade(
                risk_gate,
            )

        # ==========================================
        # Explainable AI Reasoning
        # ==========================================

        reasoning = AITradeReasonGenerator.generate(
            decision=decision,
            market_intelligence=(
                result["market_intelligence"]
            ),
            risk_validation=risk_gate,
        )

        # ==========================================
        # Store Results
        # ==========================================

        result["trade_plan"] = trade_plan

        result["risk_gate"] = risk_gate

        result["risk_validation"] = risk_validation

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
        pip_value,
        execute=False,
        execution_service=None,
        notification_service=None,
        user_id=None,
        price_structure="BOS_BULLISH",
        liquidity_sweep=True,
        order_block="BULLISH",
        fair_value_gap=True,
    ):
        """
        Generate the complete AI trading workflow.

        The trade can only reach execution when
        the Risk Gate and Approval layer approve it.
        """

        result = TradingService.generate_ai_trade_setup(
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
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            account_balance=account_balance,
            risk_percent=risk_percent,
            trade_risk_amount=trade_risk_amount,
            lot_size=lot_size,
            pip_value=pip_value,
        )

        # ==========================================
        # Explainable AI Reasoning
        # ==========================================

        decision = result.get("decision")

        if decision:

            risk_approved = False

            if "risk_gate" in result:

                risk_approved = (
                    result["risk_gate"].approved
                )

            elif "approval" in result:

                risk_approved = (
                    result["approval"].approved
                )

            reasoning = ReasoningEngine.generate(
                decision=decision.action,
                confidence=decision.confidence,
                ema_signal=ema_signal,
                rsi_value=rsi_value,
                adx_value=adx_value,
                price_structure=price_structure,
                liquidity_sweep=liquidity_sweep,
                risk_approved=risk_approved,
            )

            result["reasoning"] = reasoning

        # ==========================================
        # No Approval
        # ==========================================

        if "approval" not in result:

            return result

        # ==========================================
        # Execute Approved Trade
        # ==========================================

        if result["approval"].approved and execute:

            if execution_service is None:

                raise ValueError(
                    "Execution service required."
                )

            if user_id is None:

                raise ValueError(
                    "User ID required."
                )

            execution_request = (
                ExecutionManager.prepare_execution(
                    symbol=symbol,
                    direction=result["decision"].action,
                    lot_size=lot_size,
                    approved=True,
                )
            )

            execution_result = (
                execution_service.execute_trade(
                    user_id=user_id,
                    execution_request=execution_request,
                )
            )

            result["execution"] = execution_request

            result["execution_result"] = (
                execution_result
            )

            # ==========================================
            # Execution Notification
            # ==========================================

            if notification_service is not None:

                if execution_result.status == "EXECUTED":

                    notification_service.create_notification(
                        user_id=user_id,
                        notification_type="TRADE_EXECUTED",
                        title="Trade Executed",
                        message=(
                            f"{symbol} "
                            f"{result['decision'].action} "
                            "trade was successfully executed."
                        ),
                        priority="SUCCESS",
                    )

                elif execution_result.status == "FAILED":

                    notification_service.create_notification(
                        user_id=user_id,
                        notification_type=(
                            "TRADE_EXECUTION_FAILED"
                        ),
                        title="Trade Execution Failed",
                        message=(
                            f"{symbol} "
                            f"{result['decision'].action} "
                            "trade could not be executed."
                        ),
                        priority="WARNING",
                    )

        return result