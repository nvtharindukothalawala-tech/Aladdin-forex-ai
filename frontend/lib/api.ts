const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8000";


/* =========================================================
   TYPES
   ========================================================= */

export type LoginResponse = {
  access_token: string;
  token_type: string;
};


export type Trade = {
  trade_id: string;
  symbol: string;
  direction: string;
  entry_price: number;
  exit_price: number | null;
  lot_size: number;
  stop_loss: number;
  take_profit: number;
  status: string;
  open_time: string;
  close_time: string | null;
  strategy: string;
  reason: string;
  emotion: string;
  lesson_learned: string;
};


export type TradeCreateData = {
  symbol: string;
  direction: string;
  entry_price: number;
  lot_size: number;
  stop_loss: number;
  take_profit: number;
};


export type AITradeAnalysisData = {
  symbol: string;

  ema_signal:
    | "BULLISH"
    | "BEARISH"
    | "NEUTRAL";

  rsi_value: number;

  adx_value: number;

  volatility:
    | "NORMAL"
    | "HIGH";

  currency: string;

  event_type: string;

  importance:
    | "HIGH"
    | "MEDIUM"
    | "LOW";

  sentiment:
    | "BULLISH"
    | "BEARISH"
    | "NEUTRAL";

  price_structure:
    | "BOS_BULLISH"
    | "BOS_BEARISH"
    | "CHOCH"
    | "RANGE";

  liquidity_sweep: boolean;

  order_block:
    | "BULLISH"
    | "BEARISH";

  fair_value_gap: boolean;

  entry_price: number;

  stop_loss: number;

  take_profit: number;

  account_balance: number;

  risk_percent: number;

  trade_risk_amount: number;

  lot_size: number;

  /*
   * Value of one pip for one standard lot.
   *
   * This is supplied to the backend Risk Gate.
   */
  pip_value: number;
};


export type AITradeAnalysisResult = {
  market_intelligence: {
    market_bias: string;
    confidence: number;
    technical_summary: string;
    news_summary: string;
    structure_summary: string;

    structure_direction: string;
    structure_confirmation: string;

    risk_level: string;
    recommendation: string;

    conflict_detected: boolean;
    conflict_summary: string;

    confidence_summary: string;

    timeframe_alignment: string;
    timeframe_confidence: number;
    timeframe_summary: string;

    market_session: string;
    session_activity: string;
    session_condition: string;
    session_summary: string;
  };

  decision: {
    action: string;
    approved: boolean;
    reason: string;

    market_confidence: number;
    timeframe_confidence: number;
    decision_confidence: number;

    gates_passed: string[];
    gates_failed: string[];
  };

  trade_plan?: {
    symbol: string;
    direction: string;
    entry_price: number;
    stop_loss: number;
    take_profit: number;
    risk_reward: number;
  };

  risk_gate?: {
    approved: boolean;
    risk_amount: number;
    risk_reward: number;
    reason: string;
    gates_passed: string[];
    gates_failed: string[];
  };

  risk_validation?: {
    approved: boolean;
    reason: string;
  };

  approval?: {
    approved: boolean;
    reason: string;
  };

  reasoning?: {
    decision: string;
    confidence: number;
    technical_reason: string;
    news_reason: string;
    structure_reason: string;
    risk_reason: string;
    final_reason: string;
  };
};


export type AIExecutionResult = {
  decision?: {
    action?: string;
    approved?: boolean;
    reason?: string;
    market_confidence?: number;
    timeframe_confidence?: number;
    decision_confidence?: number;
    gates_passed?: string[];
    gates_failed?: string[];
  };

  market_intelligence?: {
    market_bias?: string;
    confidence?: number;
    technical_summary?: string;
    news_summary?: string;
    structure_summary?: string;
    structure_direction?: string;
    structure_confirmation?: string;
    risk_level?: string;
    recommendation?: string;
    conflict_detected?: boolean;
    conflict_summary?: string;
    confidence_summary?: string;
    timeframe_alignment?: string;
    timeframe_confidence?: number;
    timeframe_summary?: string;
    market_session?: string;
    session_activity?: string;
    session_condition?: string;
    session_summary?: string;
  };

  trade_plan?: {
    symbol?: string;
    direction?: string;
    entry_price?: number;
    stop_loss?: number;
    take_profit?: number;
    risk_reward?: number;
  };

  risk_validation?: {
    approved?: boolean;
    reason?: string;
  };

  approval?: {
    approved?: boolean;
    reason?: string;
  };

  reasoning?: {
    decision?: string;
    confidence?: number;
    technical_reason?: string;
    news_reason?: string;
    structure_reason?: string;
    risk_reason?: string;
    timeframe_reason?: string;
    session_reason?: string;
    final_reason?: string;
    gate_reason?: string;
    gates_passed?: string[];
    gates_failed?: string[];
  };

  execution?: {
    symbol?: string;
    order_type?: string;
    volume?: number;
    status?: string;
    entry_price?: number | null;
    stop_loss?: number | null;
    take_profit?: number | null;
  };

  execution_result?: {
    symbol?: string;
    direction?: string;
    volume?: number;
    status?: string;
    broker_order_id?: string | null;
    execution_message?: string | null;

    execution_mode?:
      | "MOCK"
      | "DEMO"
      | string
      | null;

    demo_execution_enabled?:
      | boolean
      | null;
  };
};


export type TradeStatistics = {
  total_trades: number;
  open_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  total_profit: number;
  average_profit: number;
  profit_factor: number;
};


export type Notification = {
  id: number;
  user_id: number;
  notification_type: string;
  title: string;
  message: string;
  trade_id: string | null;
  priority: string;
  is_read: number;
  created_at: string;
};


/* =========================================================
   LIVE DECISION GATE
   ========================================================= */

export type LiveDecisionGateResult = {
  symbol: string;

  decision: {
    action: "BUY" | "SELL" | "HOLD";
    approved: boolean;

    market_confidence: number;
    timeframe_confidence: number;
    decision_confidence: number;

    reason: string;

    gates_passed: string[];
    gates_failed: string[];
  };

  market_intelligence: {
    market_bias: string;
    confidence: number;

    risk_level: string;
    recommendation: string;

    structure_direction: string;
    structure_confirmation: string;

    timeframe_alignment: string;
    timeframe_confidence: number;
    timeframe_summary: string;

    market_session: string;
    session_activity: string;
    session_condition: string;
    session_summary: string;

    technical_summary: string;
    news_summary: string;
    structure_summary: string;

    conflict_detected: boolean;
    conflict_summary: string;

    confidence_summary: string;
  };
};


/* =========================================================
   MT5 BROKER MONITORING
   ========================================================= */

export type BrokerAccount = {
  execution_mode:
    | "MOCK"
    | "DEMO"
    | string;

  connected: boolean;

  account_connected: boolean;

  account_type:
    | "MOCK"
    | "DEMO"
    | string;

  login: number | null;
  server: string | null;
  name: string | null;
  currency: string | null;

  balance: number | null;
  equity: number | null;
  profit: number | null;

  margin: number | null;
  free_margin: number | null;
  margin_level: number | null;

  leverage: number | null;

  trade_allowed: boolean;
  expert_trading_allowed: boolean;

  demo_execution_enabled: boolean;

  message: string;
};


export type BrokerPosition = {
  ticket: number;
  symbol: string;

  direction:
    | "BUY"
    | "SELL"
    | string;

  volume: number;

  open_price: number;
  current_price: number;

  stop_loss: number;
  take_profit: number;

  profit: number;
  swap: number;

  magic: number;
  comment: string;

  identifier?: number;
};


export type BrokerStatus = {
  execution_mode:
    | "MOCK"
    | "DEMO"
    | string;

  account: BrokerAccount;

  position_count: number;

  total_open_profit: number;

  positions: BrokerPosition[];
};


export type BrokerClosedTrade = {
  deal_ticket: number;

  order_ticket: number;

  position_id: number;

  symbol: string;

  direction:
    | "BUY"
    | "SELL"
    | string;

  volume: number;

  close_price: number;

  profit: number;

  commission: number;

  swap: number;

  fee: number;

  net_profit: number;

  time: string;

  magic: number;

  comment: string;

  is_aladdin_trade: boolean;
};


export type BrokerTradeHistory = {
  execution_mode:
    | "MOCK"
    | "DEMO"
    | string;

  connected: boolean;

  history_days: number;

  closed_trade_count: number;

  total_profit: number;

  total_commission: number;

  total_swap: number;

  total_fee: number;

  total_net_profit: number;

  closed_trades: BrokerClosedTrade[];

  message: string;
};


/* =========================================================
   JOURNAL
   ========================================================= */

export type JournalTrade = {
  symbol: string;

  direction: string;

  result: string;

  profit_loss: number;

  risk_reward: number | null;

  source: string | null;

  mt5_deal_ticket: number | null;

  mt5_order_ticket: number | null;

  mt5_position_id: number | null;

  close_price: number | null;

  commission: number | null;

  swap: number | null;

  fee: number | null;

  closed_at: string | null;

  is_aladdin_trade: number | null;
};


export type MT5JournalSyncResult = {
  execution_mode:
    | "MOCK"
    | "DEMO"
    | string;

  history_days: number;

  broker_closed_trade_count: number;

  imported_count: number;

  duplicate_count: number;

  skipped_count: number;

  include_other_trades: boolean;

  imported_trades: unknown[];

  skipped_trades: unknown[];

  message: string;
};


/* =========================================================
   PERFORMANCE ANALYTICS
   ========================================================= */

export type PerformanceResponse = {
  total_trades: number;

  winning_trades: number;

  losing_trades: number;

  win_rate: number;

  total_profit: number;

  average_risk_reward: number;
};


/* =========================================================
   AI COACHING
   ========================================================= */

export type CoachingResponse = {
  summary: string;

  strengths: string[];

  weaknesses: string[];

  recommendations: string[];
};


/* =========================================================
   MARKET DATA
   ========================================================= */

export type MarketTimeframe =
  | "M1"
  | "M5"
  | "M15"
  | "M30"
  | "H1"
  | "H4"
  | "D1"
  | "W1";


export type MarketCandle = {
  time: number;

  open: number;

  high: number;

  low: number;

  close: number;

  volume: number;
};


export type MarketCandlesResponse = {
  symbol: string;

  broker_symbol: string;

  timeframe: MarketTimeframe;

  count: number;

  candles: MarketCandle[];
};


export type MarketQuote = {
  symbol: string;

  display_symbol: string;

  broker_symbol: string | null;

  bid: number | null;

  ask: number | null;

  spread: number | null;

  spread_points: number | null;

  digits: number | null;

  point: number | null;

  time: number | null;

  available: boolean;

  error: string | null;
};


export type MarketQuotesResponse = {
  count: number;

  available_count: number;

  unavailable_count: number;

  quotes: MarketQuote[];
};



/* =========================================================
   AUTHENTICATION
   ========================================================= */

export async function login(
  username: string,
  password: string,
): Promise<LoginResponse> {
  const response = await fetch(
    `${API_URL}/auth/login`,
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json",
      },

      body: JSON.stringify({
        username,
        password,
      }),
    },
  );

  if (!response.ok) {
    let message =
      "Login failed.";

    try {
      const data =
        await response.json();

      if (
        typeof data.detail ===
        "string"
      ) {
        message =
          data.detail;
      }
    } catch {
      // Keep default error message.
    }

    throw new Error(
      message
    );
  }

  return response.json();
}


/* =========================================================
   TOKEN
   ========================================================= */

export function getAccessToken():
  | string
  | null {
  if (
    typeof window ===
    "undefined"
  ) {
    return null;
  }

  return localStorage.getItem(
    "aladdin_access_token",
  );
}


export function saveAccessToken(
  token: string,
): void {
  localStorage.setItem(
    "aladdin_access_token",
    token,
  );
}


export function removeAccessToken():
  void {
  localStorage.removeItem(
    "aladdin_access_token",
  );

  localStorage.removeItem(
    "aladdin_user_id",
  );
}


/* =========================================================
   CURRENT USER
   ========================================================= */

export async function getCurrentUserId():
  Promise<number> {
  const cachedUserId =
    localStorage.getItem(
      "aladdin_user_id",
    );

  if (cachedUserId) {
    const parsedUserId =
      Number(cachedUserId);

    if (
      Number.isInteger(
        parsedUserId
      ) &&
      parsedUserId > 0
    ) {
      return parsedUserId;
    }
  }

  const response =
    await authenticatedFetch(
      "/auth/me",
    );

  if (!response.ok) {
    throw new Error(
      `Failed to get current user (${response.status}).`,
    );
  }

  const data =
    await response.json();

  const userId =
    Number(
      data.id ??
      data.user_id,
    );

  if (
    !Number.isInteger(
      userId
    ) ||
    userId <= 0
  ) {
    throw new Error(
      "Authenticated user ID was not returned by the server.",
    );
  }

  localStorage.setItem(
    "aladdin_user_id",
    String(userId),
  );

  return userId;
}


/* =========================================================
   AUTHENTICATED REQUEST
   ========================================================= */

async function authenticatedFetch(
  endpoint: string,
  options: RequestInit = {},
): Promise<Response> {
  const token =
    getAccessToken();

  const headers =
    new Headers(
      options.headers,
    );

  headers.set(
    "Content-Type",
    "application/json",
  );

  if (token) {
    headers.set(
      "Authorization",
      `Bearer ${token}`,
    );
  }

  const response =
    await fetch(
      `${API_URL}${endpoint}`,
      {
        ...options,
        headers,
        cache: "no-store",
      },
    );

  if (
    response.status === 401
  ) {
    removeAccessToken();

    throw new Error(
      "Authentication required.",
    );
  }

  return response;
}


/* =========================================================
   MT5 MARKET DATA CANDLES
   ========================================================= */

export async function getMarketCandles(
  symbol: string,
  timeframe: MarketTimeframe = "H1",
  count = 300,
): Promise<MarketCandlesResponse> {
  const normalizedSymbol =
    symbol
      .replace("/", "")
      .trim()
      .toUpperCase();

  if (normalizedSymbol.length === 0) {
    throw new Error(
      "Market-data symbol is required.",
    );
  }

  const safeCount =
    Math.max(
      50,
      Math.min(
        Math.trunc(count),
        5000,
      ),
    );

  const response =
    await authenticatedFetch(
      `/market-data/candles?symbol=${encodeURIComponent(
        normalizedSymbol,
      )}&timeframe=${encodeURIComponent(
        timeframe,
      )}&count=${encodeURIComponent(
        String(safeCount),
      )}`,
    );

  if (!response.ok) {
    let message =
      `Failed to load MT5 market candles (${response.status}).`;

    try {
      const data =
        await response.json();

      if (
        typeof data.detail ===
        "string"
      ) {
        message =
          data.detail;
      } else if (
        Array.isArray(
          data.detail
        )
      ) {
        message =
          data.detail
            .map(
              (
                error: {
                  loc?: unknown[];
                  msg?: string;
                }
              ) => {
                const location =
                  Array.isArray(
                    error.loc
                  )
                    ? error.loc.join(
                        "."
                      )
                    : "field";

                return `${location}: ${
                  error.msg ??
                  "Invalid value"
                }`;
              },
            )
            .join("; ");
      }
    } catch {
      // Keep default error message.
    }

    throw new Error(
      message
    );
  }

  return response.json();
}



/* =========================================================
   MT5 MARKET WATCH QUOTES
   ========================================================= */

export async function getMarketQuotes():
  Promise<MarketQuotesResponse> {
  const response =
    await authenticatedFetch(
      "/market-data/quotes",
    );

  if (!response.ok) {
    let message =
      `Failed to load MT5 market quotes (${response.status}).`;

    try {
      const data =
        await response.json();

      if (
        typeof data.detail ===
        "string"
      ) {
        message =
          data.detail;
      } else if (
        Array.isArray(
          data.detail
        )
      ) {
        message =
          data.detail
            .map(
              (
                error: {
                  loc?: unknown[];
                  msg?: string;
                }
              ) => {
                const location =
                  Array.isArray(
                    error.loc
                  )
                    ? error.loc.join(
                        "."
                      )
                    : "field";

                return `${location}: ${
                  error.msg ??
                  "Invalid value"
                }`;
              },
            )
            .join("; ");
      }
    } catch {
      // Keep default error message.
    }

    throw new Error(
      message
    );
  }

  return response.json();
}



/* =========================================================
   GET ALL TRADES
   ========================================================= */

export async function getTrades():
  Promise<Trade[]> {
  const response =
    await authenticatedFetch(
      "/trades/",
    );

  if (!response.ok) {
    throw new Error(
      `Failed to load trades (${response.status}).`,
    );
  }

  return response.json();
}


/* =========================================================
   CREATE TRADE
   ========================================================= */

export async function createTrade(
  tradeData: TradeCreateData,
): Promise<Trade> {
  const response =
    await authenticatedFetch(
      "/trades/",
      {
        method: "POST",

        body:
          JSON.stringify(
            tradeData
          ),
      },
    );

  if (!response.ok) {
    let message =
      `Failed to create trade (${response.status}).`;

    try {
      const data =
        await response.json();

      console.error(
        "Create trade backend response:",
        data,
      );

      if (
        typeof data.detail ===
        "string"
      ) {
        message =
          data.detail;
      } else if (
        Array.isArray(
          data.detail
        )
      ) {
        message =
          data.detail
            .map(
              (
                error: {
                  loc?: unknown[];
                  msg?: string;
                }
              ) => {
                const location =
                  Array.isArray(
                    error.loc
                  )
                    ? error.loc.join(
                        "."
                      )
                    : "field";

                return `${location}: ${
                  error.msg ??
                  "Invalid value"
                }`;
              },
            )
            .join("; ");
      }
    } catch {
      // Keep default error message.
    }

    throw new Error(
      message
    );
  }

  return response.json();
}


/* =========================================================
   CLOSE TRADE
   ========================================================= */

export async function closeTrade(
  tradeId: string,
  exitPrice: number,
): Promise<Trade> {
  const response =
    await authenticatedFetch(
      `/trades/${tradeId}/close`,
      {
        method: "PUT",

        body:
          JSON.stringify({
            exit_price:
              exitPrice,
          }),
      },
    );

  if (!response.ok) {
    let message =
      `Failed to close trade (${response.status}).`;

    try {
      const data =
        await response.json();

      if (
        typeof data.detail ===
        "string"
      ) {
        message =
          data.detail;
      }
    } catch {
      // Keep default error message.
    }

    throw new Error(
      message
    );
  }

  return response.json();
}


/* =========================================================
   TRADE STATISTICS
   ========================================================= */

export async function getTradeStatistics():
  Promise<TradeStatistics> {
  const response =
    await authenticatedFetch(
      "/trades/statistics",
    );

  if (!response.ok) {
    throw new Error(
      `Failed to load trade statistics (${response.status}).`,
    );
  }

  return response.json();
}


/* =========================================================
   GET ALL NOTIFICATIONS
   ========================================================= */

export async function getNotifications():
  Promise<Notification[]> {
  const response =
    await authenticatedFetch(
      "/notifications",
    );

  if (!response.ok) {
    throw new Error(
      `Failed to load notifications (${response.status}).`,
    );
  }

  return response.json();
}


/* =========================================================
   GET UNREAD NOTIFICATIONS
   ========================================================= */

export async function getUnreadNotifications():
  Promise<Notification[]> {
  const response =
    await authenticatedFetch(
      "/notifications/unread",
    );

  if (!response.ok) {
    throw new Error(
      `Failed to load unread notifications (${response.status}).`,
    );
  }

  return response.json();
}


/* =========================================================
   UNREAD NOTIFICATION COUNT
   ========================================================= */

export async function getUnreadNotificationCount():
  Promise<number> {
  const response =
    await authenticatedFetch(
      "/notifications/unread/count",
    );

  if (!response.ok) {
    throw new Error(
      `Failed to load notification count (${response.status}).`,
    );
  }

  const data =
    await response.json();

  return Number(
    data.unread_count ?? 0,
  );
}


/* =========================================================
   MARK NOTIFICATION AS READ
   ========================================================= */

export async function markNotificationAsRead(
  notificationId: number,
): Promise<Notification> {
  const response =
    await authenticatedFetch(
      `/notifications/${notificationId}/read`,
      {
        method: "PATCH",
      },
    );

  if (!response.ok) {
    throw new Error(
      `Failed to mark notification as read (${response.status}).`,
    );
  }

  return response.json();
}


/* =========================================================
   MARK ALL NOTIFICATIONS AS READ
   ========================================================= */

export async function markAllNotificationsAsRead():
  Promise<{
    message: string;
    count: number;
  }> {
  const response =
    await authenticatedFetch(
      "/notifications/read-all",
      {
        method: "PATCH",
      },
    );

  if (!response.ok) {
    throw new Error(
      `Failed to mark notifications as read (${response.status}).`,
    );
  }

  return response.json();
}


/* =========================================================
   LIVE INTELLIGENT DECISION
   ========================================================= */

export async function getLiveIntelligentDecision(
  symbol: string,
): Promise<LiveDecisionGateResult> {
  const normalizedSymbol =
    symbol
      .replace("/", "")
      .trim()
      .toUpperCase();

  const response =
    await authenticatedFetch(
      `/decision/intelligent/live/${encodeURIComponent(
        normalizedSymbol,
      )}`,
    );

  if (!response.ok) {
    let message =
      `Live intelligent decision failed (${response.status}).`;

    try {
      const data =
        await response.json();

      if (
        typeof data.detail ===
        "string"
      ) {
        message =
          data.detail;
      } else if (
        Array.isArray(
          data.detail
        )
      ) {
        message =
          data.detail
            .map(
              (
                error: {
                  loc?: unknown[];
                  msg?: string;
                }
              ) => {
                const location =
                  Array.isArray(
                    error.loc
                  )
                    ? error.loc.join(
                        "."
                      )
                    : "field";

                return `${location}: ${
                  error.msg ??
                  "Invalid value"
                }`;
              },
            )
            .join("; ");
      }
    } catch {
      // Keep default error message.
    }

    throw new Error(
      message
    );
  }

  return response.json();
}


/* =========================================================
   AI TRADE ANALYSIS
   ========================================================= */

export async function analyzeAITrade(
  tradeData:
    AITradeAnalysisData,
): Promise<
  AITradeAnalysisResult
> {
  const response =
    await authenticatedFetch(
      "/trading/ai-analyze",
      {
        method: "POST",

        body:
          JSON.stringify(
            tradeData
          ),
      },
    );

  if (!response.ok) {
    let message =
      `AI analysis failed (${response.status}).`;

    try {
      const data =
        await response.json();

      if (
        typeof data.detail ===
        "string"
      ) {
        message =
          data.detail;
      } else if (
        Array.isArray(
          data.detail
        )
      ) {
        message =
          data.detail
            .map(
              (
                error: {
                  loc?: unknown[];
                  msg?: string;
                }
              ) => {
                const location =
                  Array.isArray(
                    error.loc
                  )
                    ? error.loc.join(
                        "."
                      )
                    : "field";

                return `${location}: ${
                  error.msg ??
                  "Invalid value"
                }`;
              },
            )
            .join("; ");
      }
    } catch {
      // Keep default error message.
    }

    throw new Error(
      message
    );
  }

  return response.json();
}


/* =========================================================
   AI TRADE EXECUTION
   ========================================================= */

export async function executeAITrade(
  tradeData:
    AITradeAnalysisData,
  idempotencyKey: string,
): Promise<
  AIExecutionResult
> {
  const userId =
    await getCurrentUserId();

  const normalizedIdempotencyKey =
    idempotencyKey.trim();

  if (
    normalizedIdempotencyKey.length === 0
  ) {
    throw new Error(
      "Execution idempotency key is required.",
    );
  }

  if (
    normalizedIdempotencyKey.length > 128
  ) {
    throw new Error(
      "Execution idempotency key cannot exceed 128 characters.",
    );
  }

  const response =
    await authenticatedFetch(
      "/execution/ai-execute",
      {
        method: "POST",

        body:
          JSON.stringify({
            user_id:
              userId,

            ...tradeData,

            idempotency_key:
              normalizedIdempotencyKey,
          }),
      },
    );

  if (!response.ok) {
    let message =
      `AI execution failed (${response.status}).`;

    try {
      const data =
        await response.json();

      if (
        typeof data.detail ===
        "string"
      ) {
        message =
          data.detail;
      } else if (
        Array.isArray(
          data.detail
        )
      ) {
        message =
          data.detail
            .map(
              (
                error: {
                  loc?: unknown[];
                  msg?: string;
                }
              ) => {
                const location =
                  Array.isArray(
                    error.loc
                  )
                    ? error.loc.join(
                        "."
                      )
                    : "field";

                return `${location}: ${
                  error.msg ??
                  "Invalid value."
                }`;
              },
            )
            .join(", ");
      }
    } catch {
      // Keep default error message.
    }

    throw new Error(
      message
    );
  }

  return response.json();
}


/* =========================================================
   MT5 BROKER STATUS
   ========================================================= */

export async function getBrokerStatus():
  Promise<BrokerStatus> {
  const response =
    await authenticatedFetch(
      "/broker/status",
    );

  if (!response.ok) {
    let message =
      `Failed to load MT5 broker status (${response.status}).`;

    try {
      const data =
        await response.json();

      if (
        typeof data.detail ===
        "string"
      ) {
        message =
          data.detail;
      }
    } catch {
      // Keep default error message.
    }

    throw new Error(
      message
    );
  }

  return response.json();
}


/* =========================================================
   MT5 BROKER TRADE HISTORY
   ========================================================= */

export async function getBrokerTradeHistory(
  days = 30,
): Promise<
  BrokerTradeHistory
> {
  const safeDays =
    Math.max(
      1,
      Math.min(
        Math.trunc(days),
        3650,
      ),
    );

  const response =
    await authenticatedFetch(
      `/broker/history?days=${encodeURIComponent(
        String(safeDays),
      )}`,
    );

  if (!response.ok) {
    let message =
      `Failed to load MT5 trade history (${response.status}).`;

    try {
      const data =
        await response.json();

      if (
        typeof data.detail ===
        "string"
      ) {
        message =
          data.detail;
      }
    } catch {
      // Keep default error message.
    }

    throw new Error(
      message
    );
  }

  return response.json();
}


/* =========================================================
   GET JOURNAL TRADES
   ========================================================= */

export async function getJournalTrades():
  Promise<JournalTrade[]> {
  const response =
    await authenticatedFetch(
      "/journal/trades",
    );

  if (!response.ok) {
    let message =
      `Failed to load journal trades (${response.status}).`;

    try {
      const data =
        await response.json();

      if (
        typeof data.detail ===
        "string"
      ) {
        message =
          data.detail;
      }
    } catch {
      // Keep default error message.
    }

    throw new Error(
      message
    );
  }

  return response.json();
}


/* =========================================================
   SYNC MT5 COMPLETED TRADES TO JOURNAL
   ========================================================= */

export async function syncMT5Journal(
  days = 30,
  includeOtherTrades = false,
): Promise<
  MT5JournalSyncResult
> {
  const safeDays =
    Math.max(
      1,
      Math.min(
        Math.trunc(days),
        3650,
      ),
    );

  const response =
    await authenticatedFetch(
      `/journal/sync-mt5?days=${encodeURIComponent(
        String(safeDays),
      )}&include_other_trades=${encodeURIComponent(
        String(includeOtherTrades),
      )}`,
      {
        method: "POST",
      },
    );

  if (!response.ok) {
    let message =
      `Failed to synchronize MT5 journal (${response.status}).`;

    try {
      const data =
        await response.json();

      if (
        typeof data.detail ===
        "string"
      ) {
        message =
          data.detail;
      }
    } catch {
      // Keep default error message.
    }

    throw new Error(
      message
    );
  }

  return response.json();
}


/* =========================================================
   PERFORMANCE ANALYTICS
   ========================================================= */

export async function getPerformanceReport():
  Promise<PerformanceResponse> {
  const response =
    await authenticatedFetch(
      "/performance/",
    );

  if (!response.ok) {
    let message =
      `Failed to load performance analytics (${response.status}).`;

    try {
      const data =
        await response.json();

      if (
        typeof data.detail ===
        "string"
      ) {
        message =
          data.detail;
      }
    } catch {
      // Keep default error message.
    }

    throw new Error(
      message
    );
  }

  return response.json();
}


/* =========================================================
   AI COACHING REPORT
   ========================================================= */

export async function getCoachingReport():
  Promise<CoachingResponse> {
  const response =
    await authenticatedFetch(
      "/coaching/report",
    );

  if (!response.ok) {
    let message =
      `Failed to load AI coaching report (${response.status}).`;

    try {
      const data =
        await response.json();

      if (
        typeof data.detail ===
        "string"
      ) {
        message =
          data.detail;
      }
    } catch {
      // Keep default error message.
    }

    throw new Error(
      message
    );
  }

  return response.json();
}