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
    confidence: number;
    reason: string;
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
  };

  execution_result?: {
    symbol?: string;
    direction?: string;
    volume?: number;
    status?: string;
    broker_order_id?: string | null;
    execution_message?: string | null;
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
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username,
        password,
      }),
    },
  );

  if (!response.ok) {
    let message = "Login failed.";

    try {
      const data = await response.json();

      if (typeof data.detail === "string") {
        message = data.detail;
      }
    } catch {
      // Keep default error message.
    }

    throw new Error(message);
  }

  return response.json();
}


/* =========================================================
   TOKEN
   ========================================================= */

export function getAccessToken(): string | null {
  if (typeof window === "undefined") {
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


export function removeAccessToken(): void {
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

export async function getCurrentUserId(): Promise<number> {
  const cachedUserId = localStorage.getItem(
    "aladdin_user_id",
  );

  if (cachedUserId) {
    const parsedUserId = Number(cachedUserId);

    if (
      Number.isInteger(parsedUserId) &&
      parsedUserId > 0
    ) {
      return parsedUserId;
    }
  }

  const response = await authenticatedFetch(
    "/auth/me",
  );

  if (!response.ok) {
    throw new Error(
      `Failed to get current user (${response.status}).`,
    );
  }

  const data = await response.json();

  const userId = Number(
    data.id ?? data.user_id,
  );

  if (
    !Number.isInteger(userId) ||
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
  const token = getAccessToken();

  const headers = new Headers(
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

  const response = await fetch(
    `${API_URL}${endpoint}`,
    {
      ...options,
      headers,
      cache: "no-store",
    },
  );

  if (response.status === 401) {
    removeAccessToken();

    throw new Error(
      "Authentication required.",
    );
  }

  return response;
}


/* =========================================================
   GET ALL TRADES
   ========================================================= */

export async function getTrades(): Promise<
  Trade[]
> {
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
        body: JSON.stringify(tradeData),
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

      if (typeof data.detail === "string") {
        message = data.detail;
      } else if (Array.isArray(data.detail)) {
        message = data.detail
          .map((error: {
            loc?: unknown[];
            msg?: string;
          }) => {
            const location =
              Array.isArray(error.loc)
                ? error.loc.join(".")
                : "field";

            return `${location}: ${
              error.msg ?? "Invalid value"
            }`;
          })
          .join("; ");
      }
    } catch {
      // Keep default error message.
    }

    throw new Error(message);
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
        body: JSON.stringify({
          exit_price: exitPrice,
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
        typeof data.detail === "string"
      ) {
        message = data.detail;
      }
    } catch {
      // Keep default error message.
    }

    throw new Error(message);
  }

  return response.json();
}


/* =========================================================
   TRADE STATISTICS
   ========================================================= */

export async function getTradeStatistics(): Promise<
  TradeStatistics
> {
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

export async function getNotifications(): Promise<
  Notification[]
> {
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

export async function getUnreadNotifications(): Promise<
  Notification[]
> {
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

export async function getUnreadNotificationCount(): Promise<number> {
  const response =
    await authenticatedFetch(
      "/notifications/unread/count",
    );

  if (!response.ok) {
    throw new Error(
      `Failed to load notification count (${response.status}).`,
    );
  }

  const data = await response.json();

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

export async function markAllNotificationsAsRead(): Promise<{
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
  const normalizedSymbol = symbol
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
      const data = await response.json();

      if (typeof data.detail === "string") {
        message = data.detail;
      } else if (Array.isArray(data.detail)) {
        message = data.detail
          .map(
            (error: {
              loc?: unknown[];
              msg?: string;
            }) => {
              const location =
                Array.isArray(error.loc)
                  ? error.loc.join(".")
                  : "field";

              return `${location}: ${
                error.msg ?? "Invalid value"
              }`;
            },
          )
          .join("; ");
      }
    } catch {
      // Keep default error message.
    }

    throw new Error(message);
  }

  return response.json();
}

/* =========================================================
   AI TRADE ANALYSIS
   ========================================================= */

export async function analyzeAITrade(
  tradeData: AITradeAnalysisData,
): Promise<AITradeAnalysisResult> {
  const response =
    await authenticatedFetch(
      "/trading/ai-analyze",
      {
        method: "POST",
        body: JSON.stringify(tradeData),
      },
    );

  if (!response.ok) {
    let message =
      `AI analysis failed (${response.status}).`;

    try {
      const data =
        await response.json();

      if (
        typeof data.detail === "string"
      ) {
        message = data.detail;
      } else if (
        Array.isArray(data.detail)
      ) {
        message = data.detail
          .map(
            (error: {
              loc?: unknown[];
              msg?: string;
            }) => {
              const location =
                Array.isArray(error.loc)
                  ? error.loc.join(".")
                  : "field";

              return `${location}: ${
                error.msg ?? "Invalid value"
              }`;
            },
          )
          .join("; ");
      }
    } catch {
      // Keep default error message.
    }

    throw new Error(message);
  }

  return response.json();
}

export async function executeAITrade(
  tradeData: AITradeAnalysisData,
): Promise<AIExecutionResult> {
  const userId = await getCurrentUserId();

  const response = await authenticatedFetch(
    "/execution/ai-execute",
    {
      method: "POST",
      body: JSON.stringify({
        user_id: userId,
        ...tradeData,
      }),
    },
  );

  if (!response.ok) {
    let message =
      `AI execution failed (${response.status}).`;

    try {
      const data = await response.json();

      if (typeof data.detail === "string") {
        message = data.detail;
      } else if (Array.isArray(data.detail)) {
        message = data.detail
          .map(
            (error: {
              loc?: unknown[];
              msg?: string;
            }) => {
              const location =
                Array.isArray(error.loc)
                  ? error.loc.join(".")
                  : "field";

              return `${location}: ${
                error.msg ?? "Invalid value."
              }`;
            },
          )
          .join(", ");
      }
    } catch {
      // Keep default error message.
    }

    throw new Error(message);
  }

  return response.json();
}