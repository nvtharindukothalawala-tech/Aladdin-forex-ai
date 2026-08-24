"use client";

import Image from "next/image";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Bell,
  BrainCircuit,
  Check,
  CheckCircle2,
  CheckCheck,
  ChevronDown,
  CircleAlert,
  CircleDollarSign,
  Clock3,
  Info,
  Menu,
  RefreshCw,
  ShieldCheck,
  TrendingUp,
  X,
} from "lucide-react";

import {
  closeTrade,
  createTrade,
  getAccessToken,
  getLiveIntelligentDecision,
  getNotifications,
  getTradeStatistics,
  getTrades,
  getUnreadNotificationCount,
  markAllNotificationsAsRead,
  markNotificationAsRead,
  removeAccessToken,
  type LiveDecisionGateResult,
  type Notification,
  type Trade,
  type TradeCreateData,
  type TradeStatistics,
} from "../lib/api";

import {
  useEffect,
  useState,
  type ReactNode,
} from "react";


/* =========================================================
   DEFAULT STATISTICS
   ========================================================= */

const defaultStatistics: TradeStatistics = {
  total_trades: 0,
  open_trades: 0,
  winning_trades: 0,
  losing_trades: 0,
  win_rate: 0,
  total_profit: 0,
  average_profit: 0,
  profit_factor: 0,
};


/* =========================================================
   HELPER FUNCTIONS
   ========================================================= */

function formatMoney(value: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}


function formatNumber(
  value: number,
  digits = 2,
) {
  return Number(value || 0).toFixed(digits);
}


function formatDate(value: string) {
  if (!value) {
    return "-";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}


function formatNotificationTime(
  value: string,
) {
  if (!value) {
    return "";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  const now = new Date();

  const difference =
    now.getTime() - date.getTime();

  const seconds = Math.floor(
    difference / 1000,
  );

  const minutes = Math.floor(
    seconds / 60,
  );

  const hours = Math.floor(
    minutes / 60,
  );

  const days = Math.floor(
    hours / 24,
  );

  if (seconds < 60) {
    return "Just now";
  }

  if (minutes < 60) {
    return `${minutes}m ago`;
  }

  if (hours < 24) {
    return `${hours}h ago`;
  }

  if (days < 7) {
    return `${days}d ago`;
  }

  return date.toLocaleDateString();
}


/* =========================================================
   NOTIFICATION ICON
   ========================================================= */

function NotificationIcon({
  type,
  priority,
}: {
  type: string;
  priority: string;
}) {
  const combined =
    `${type} ${priority}`.toLowerCase();

  if (
    combined.includes("risk") ||
    combined.includes("warning") ||
    combined.includes("danger")
  ) {
    return (
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-amber-400/10 text-amber-400">
        <AlertTriangle size={17} />
      </div>
    );
  }

  if (
    combined.includes("error") ||
    combined.includes("critical")
  ) {
    return (
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-red-400/10 text-red-400">
        <CircleAlert size={17} />
      </div>
    );
  }

  if (
    combined.includes("trade") ||
    combined.includes("signal") ||
    combined.includes("execution")
  ) {
    return (
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-emerald-400/10 text-emerald-400">
        <TrendingUp size={17} />
      </div>
    );
  }

  return (
    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-blue-400/10 text-blue-400">
      <Info size={17} />
    </div>
  );
}


/* =========================================================
   DASHBOARD
   ========================================================= */

export default function DashboardPage() {

  /* =======================================================
     DASHBOARD STATE
     ======================================================= */

  const [statistics, setStatistics] =
    useState<TradeStatistics>(
      defaultStatistics,
    );

  const [trades, setTrades] =
    useState<Trade[]>([]);

  const [tradeForm, setTradeForm] =
    useState<TradeCreateData>({
      symbol: "EUR/USD",
      direction: "Buy",
      entry_price: 1.08,
      lot_size: 0.1,
      stop_loss: 1.075,
      take_profit: 1.09,
    });

  const [creatingTrade, setCreatingTrade] =
    useState(false);

  const [tradeActionError, setTradeActionError] =
    useState("");

  const [tradeActionMessage, setTradeActionMessage] =
    useState("");

  const [aiAnalysis, setAiAnalysis] =
    useState<LiveDecisionGateResult | null>(null);

  const [aiAnalyzing, setAiAnalyzing] =
    useState(false);

  const [aiAnalysisError, setAiAnalysisError] =
    useState("");

  const [notificationCount, setNotificationCount] =
    useState(0);

  const [notifications, setNotifications] =
    useState<Notification[]>([]);

  const [notificationOpen, setNotificationOpen] =
    useState(false);

  const [notificationLoading, setNotificationLoading] =
    useState(false);

  const [notificationActionLoading, setNotificationActionLoading] =
    useState(false);

  const [loading, setLoading] =
    useState(true);

  const [refreshing, setRefreshing] =
    useState(false);

  const [error, setError] =
    useState("");

  const [sidebarOpen, setSidebarOpen] =
    useState(false);


  /* =======================================================
     AI TRADE ANALYSIS
     ======================================================= */

  async function handleAIAnalysis() {
    try {
      setAiAnalyzing(true);
      setAiAnalysisError("");
      setAiAnalysis(null);

      const accessToken = getAccessToken();

      if (!accessToken) {
        window.location.href = "/login";
        return;
      }

      // MT5/backend symbols normally use EURUSD instead of EUR/USD.
      const symbol = tradeForm.symbol.replace("/", "").toUpperCase();

      const result = await getLiveIntelligentDecision(symbol);

      console.log("ALADDIN LIVE DECISION GATE RESULT:", result);

      setAiAnalysis(result);
    } catch (err) {
      console.error("AI analysis error:", err);

      if (
        err instanceof Error &&
        err.message === "Authentication required."
      ) {
        window.location.href = "/login";
        return;
      }

      setAiAnalysisError(
        err instanceof Error
          ? err.message
          : "Unable to generate live Aladdin decision.",
      );
    } finally {
      setAiAnalyzing(false);
    }
  }


  /* =======================================================
     LOAD DASHBOARD
     ======================================================= */
  async function loadDashboard() {
    try {
      setError("");

      const token =
        getAccessToken();

      if (!token) {
        window.location.href =
          "/login";

        return;
      }

      const [
        statisticsData,
        tradesData,
        unreadCount,
      ] = await Promise.all([
        getTradeStatistics(),
        getTrades(),
        getUnreadNotificationCount(),
      ]);

      setStatistics(
        statisticsData,
      );

      setTrades(
        tradesData,
      );

      setNotificationCount(
        unreadCount,
      );

    } catch (err) {
      console.error(
        "Dashboard loading error:",
        err,
      );

      if (
        err instanceof Error &&
        err.message ===
          "Authentication required."
      ) {
        window.location.href =
          "/login";

        return;
      }

      setError(
        err instanceof Error
          ? err.message
          : "Unable to load dashboard data.",
      );

    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }


  /* =========================================================
    CREATE TRADE
    ========================================================= */

  async function handleCreateTrade() {
    try {
      setCreatingTrade(true);
      setTradeActionError("");
      setTradeActionMessage("");

      if (
        tradeForm.entry_price <= 0 ||
        tradeForm.lot_size <= 0 ||
        tradeForm.stop_loss <= 0 ||
        tradeForm.take_profit <= 0
      ) {
        setTradeActionError(
          "Please enter valid values for entry price, lot size, stop loss, and take profit.",
        );

        return;
      }

      const createdTrade =
        await createTrade(tradeForm);

      setTradeActionMessage(
        `${createdTrade.symbol} ${createdTrade.direction} trade created successfully.`,
      );

      await loadDashboard();

      if (notificationOpen) {
        await loadNotifications();
      }
    } catch (err) {
      console.error("Create trade error:", err);

      if (
        err instanceof Error &&
        err.message === "Authentication required."
      ) {
        window.location.href = "/login";
        return;
      }

      setTradeActionError(
        err instanceof Error
          ? err.message
          : "Unable to create trade.",
      );
    } finally {
      setCreatingTrade(false);
    }
  }

  async function handleCloseTrade(
    tradeId: string,
    exitPrice: number,
  ) {
    try {
      setTradeActionError("");
      setTradeActionMessage("");

      if (exitPrice <= 0) {
        setTradeActionError(
          "Please enter a valid exit price.",
        );

        return;
      }

      const closedTrade = await closeTrade(
        tradeId,
        exitPrice,
      );

      setTradeActionMessage(
        `${closedTrade.symbol} ${closedTrade.direction} trade closed successfully.`,
      );

      await loadDashboard();

      if (notificationOpen) {
        await loadNotifications();
      }
    } catch (err) {
      console.error(
        "Close trade error:",
        err,
      );

      if (
        err instanceof Error &&
        err.message ===
          "Authentication required."
      ) {
        window.location.href =
          "/login";

        return;
      }

      setTradeActionError(
        err instanceof Error
          ? err.message
          : "Unable to close trade.",
      );
    }
  }
  /* =======================================================
     LOAD NOTIFICATIONS
     ======================================================= */

  async function loadNotifications() {
    try {
      setNotificationLoading(true);

      const data =
        await getNotifications();

      setNotifications(data);

      const unread =
        data.filter(
          (notification) =>
            Number(
              notification.is_read,
            ) === 0,
        ).length;

      setNotificationCount(
        unread,
      );

    } catch (err) {
      console.error(
        "Notification loading error:",
        err,
      );

      if (
        err instanceof Error &&
        err.message ===
          "Authentication required."
      ) {
        window.location.href =
          "/login";
      }

    } finally {
      setNotificationLoading(false);
    }
  }


  /* =======================================================
     INITIAL LOAD
     ======================================================= */

  useEffect(() => {
    loadDashboard();
  }, []);


  /* =======================================================
     REFRESH DASHBOARD
     ======================================================= */

  async function handleRefresh() {
    setRefreshing(true);

    await loadDashboard();

    if (notificationOpen) {
      await loadNotifications();
    }
  }


  /* =======================================================
     OPEN NOTIFICATIONS
     ======================================================= */

  async function handleNotificationToggle() {
    const nextState =
      !notificationOpen;

    setNotificationOpen(
      nextState,
    );

    if (nextState) {
      await loadNotifications();
    }
  }


  /* =======================================================
     MARK ONE NOTIFICATION READ
     ======================================================= */

  async function handleNotificationClick(
    notification: Notification,
  ) {
    if (
      Number(
        notification.is_read,
      ) === 1
    ) {
      return;
    }

    try {
      setNotificationActionLoading(
        true,
      );

      const updated =
        await markNotificationAsRead(
          notification.id,
        );

      setNotifications(
        (current) =>
          current.map(
            (item) =>
              item.id ===
              notification.id
                ? updated
                : item,
          ),
      );

      setNotificationCount(
        (current) =>
          Math.max(
            0,
            current - 1,
          ),
      );

    } catch (err) {
      console.error(
        "Failed to mark notification as read:",
        err,
      );

    } finally {
      setNotificationActionLoading(
        false,
      );
    }
  }


  /* =======================================================
     MARK ALL READ
     ======================================================= */

  async function handleMarkAllRead() {
    if (
      notifications.length ===
      0
    ) {
      return;
    }

    try {
      setNotificationActionLoading(
        true,
      );

      await markAllNotificationsAsRead();

      setNotifications(
        (current) =>
          current.map(
            (notification) => ({
              ...notification,
              is_read: 1,
            }),
          ),
      );

      setNotificationCount(0);

    } catch (err) {
      console.error(
        "Failed to mark all notifications as read:",
        err,
      );

    } finally {
      setNotificationActionLoading(
        false,
      );
    }
  }


  /* =======================================================
     LOGOUT
     ======================================================= */

  function handleLogout() {
    removeAccessToken();

    window.location.href =
      "/login";
  }


  /* =======================================================
     RENDER
     ======================================================= */

  return (
    <main className="min-h-screen bg-[#07090d] text-white">


      {/* =================================================
          MOBILE SIDEBAR OVERLAY
          ================================================= */}

      {sidebarOpen && (
        <button
          type="button"
          aria-label="Close sidebar"
          onClick={() =>
            setSidebarOpen(false)
          }
          className="fixed inset-0 z-40 bg-black/70 lg:hidden"
        />
      )}


      {/* =================================================
          SIDEBAR
          ================================================= */}

      <aside
        className={`
          fixed
          left-0
          top-0
          z-50
          flex
          h-screen
          w-[270px]
          flex-col
          border-r
          border-white/10
          bg-[#090c11]
          transition-transform
          duration-200
          lg:translate-x-0
          ${
            sidebarOpen
              ? "translate-x-0"
              : "-translate-x-full"
          }
        `}
      >

        {/* Logo */}

        <div className="flex h-[92px] items-center border-b border-white/10 px-6">

          <div className="relative h-12 w-12 overflow-hidden rounded-xl border border-white/10 bg-black">

            <Image
              src="/aladdin-logo.png"
              alt="Aladdin"
              fill
              priority
              sizes="48px"
              className="object-cover"
            />

          </div>

          <div className="ml-3">

            <h1 className="text-[17px] font-semibold tracking-[0.22em]">
              ALADDIN
            </h1>

            <p className="mt-1 text-[9px] uppercase tracking-[0.18em] text-gray-600">
              Forex Intelligence
            </p>

          </div>

          <button
            type="button"
            onClick={() =>
              setSidebarOpen(false)
            }
            className="ml-auto rounded-lg p-2 text-gray-500 hover:bg-white/5 hover:text-white lg:hidden"
          >
            <X size={18} />
          </button>

        </div>


        {/* Navigation */}

        <div className="flex-1 px-4 py-7">

          <p className="mb-4 px-4 text-[10px] font-semibold uppercase tracking-[0.2em] text-gray-600">
            Workspace
          </p>


          <nav className="space-y-1">

            <SidebarItem
              icon={
                <BarChart3
                  size={18}
                />
              }
              label="Dashboard"
              active
            />

            <SidebarItem
              icon={
                <TrendingUp
                  size={18}
                />
              }
              label="Markets"
            />

            <SidebarItem
              icon={
                <BrainCircuit
                  size={18}
                />
              }
              label="AI Analysis"
            />

            <SidebarItem
              icon={
                <Activity
                  size={18}
                />
              }
              label="Trade Setup"
            />

            <SidebarItem
              icon={
                <Clock3
                  size={18}
                />
              }
              label="Trade Journal"
            />

            <SidebarItem
              icon={
                <BarChart3
                  size={18}
                />
              }
              label="Performance"
            />

            <SidebarItem
              icon={
                <BrainCircuit
                  size={18}
                />
              }
              label="AI Coaching"
            />

            {/* Notification navigation */}

            <button
              type="button"
              onClick={() => {
                setNotificationOpen(
                  true,
                );

                loadNotifications();
              }}
              className="flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm text-gray-500 transition hover:bg-white/5 hover:text-white"
            >

              <Bell size={18} />

              <span className="flex-1 text-left">
                Notifications
              </span>

              {notificationCount >
                0 && (
                <span className="flex min-w-5 items-center justify-center rounded-full bg-emerald-400 px-1.5 py-0.5 text-[9px] font-bold text-black">
                  {notificationCount >
                  99
                    ? "99+"
                    : notificationCount}
                </span>
              )}

            </button>

          </nav>

        </div>


        {/* Account */}

        <div className="border-t border-white/10 p-4">

          <div className="mb-3 flex items-center gap-3 rounded-xl p-3">

            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white/10 text-sm font-semibold">
              T
            </div>

            <div className="min-w-0 flex-1">

              <p className="truncate text-sm font-medium text-white">
                Tharindu
              </p>

              <p className="truncate text-[10px] text-gray-600">
                Trader account
              </p>

            </div>

          </div>

          <button
            type="button"
            onClick={handleLogout}
            className="w-full rounded-lg px-3 py-2 text-left text-xs text-gray-500 transition hover:bg-white/5 hover:text-white"
          >
            Sign out
          </button>

        </div>

      </aside>


      {/* =================================================
          MAIN CONTENT
          ================================================= */}

      <div className="lg:pl-[270px]">


        {/* =================================================
            HEADER
            ================================================= */}

        <header className="flex h-[92px] items-center border-b border-white/10 bg-[#080b10] px-5 sm:px-8">

          <button
            type="button"
            onClick={() =>
              setSidebarOpen(true)
            }
            className="rounded-lg p-2 text-gray-400 hover:bg-white/5 hover:text-white lg:hidden"
          >
            <Menu size={22} />
          </button>


          <div className="ml-3 lg:ml-0">

            <p className="text-[11px] text-gray-600">
              Aladdin Forex AI
            </p>

            <h2 className="text-sm font-medium text-gray-200">
              AI Trading Workspace
            </h2>

          </div>


          <div className="ml-auto flex items-center gap-3">


            {/* =================================================
                NOTIFICATION BELL + DROPDOWN
                ================================================= */}

            <div className="relative">


              <button
                type="button"
                aria-label="Notifications"
                onClick={
                  handleNotificationToggle
                }
                className={`
                  relative
                  rounded-xl
                  p-2.5
                  transition
                  ${
                    notificationOpen
                      ? "bg-white/10 text-white"
                      : "text-gray-400 hover:bg-white/5 hover:text-white"
                  }
                `}
              >

                <Bell size={20} />

                {notificationCount >
                  0 && (
                  <span className="absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-emerald-400 px-1 text-[9px] font-bold text-black">
                    {notificationCount >
                    99
                      ? "99+"
                      : notificationCount}
                  </span>
                )}

              </button>


              {/* =================================================
                  NOTIFICATION DROPDOWN
                  ================================================= */}

              {notificationOpen && (
                <div className="absolute right-0 top-12 z-[100] w-[380px] max-w-[calc(100vw-32px)] overflow-hidden rounded-2xl border border-white/10 bg-[#0b0f15] shadow-2xl shadow-black/50">


                  {/* Header */}

                  <div className="flex items-center justify-between border-b border-white/10 px-4 py-4">

                    <div>

                      <div className="flex items-center gap-2">

                        <h3 className="text-sm font-semibold text-white">
                          Notifications
                        </h3>

                        {notificationCount >
                          0 && (
                          <span className="rounded-full bg-emerald-400/10 px-2 py-0.5 text-[9px] font-semibold text-emerald-400">
                            {notificationCount} unread
                          </span>
                        )}

                      </div>

                      <p className="mt-1 text-[10px] text-gray-600">
                        Aladdin system alerts and
                        trading updates
                      </p>

                    </div>


                    <button
                      type="button"
                      onClick={() =>
                        setNotificationOpen(
                          false,
                        )
                      }
                      className="rounded-lg p-1.5 text-gray-600 transition hover:bg-white/5 hover:text-white"
                    >
                      <X size={16} />
                    </button>

                  </div>


                  {/* Action bar */}

                  <div className="flex items-center justify-between border-b border-white/5 px-4 py-2.5">

                    <button
                      type="button"
                      onClick={
                        loadNotifications
                      }
                      disabled={
                        notificationLoading
                      }
                      className="flex items-center gap-1.5 text-[10px] text-gray-500 transition hover:text-white disabled:opacity-50"
                    >

                      <RefreshCw
                        size={12}
                        className={
                          notificationLoading
                            ? "animate-spin"
                            : ""
                        }
                      />

                      Refresh

                    </button>


                    <button
                      type="button"
                      onClick={
                        handleMarkAllRead
                      }
                      disabled={
                        notificationActionLoading ||
                        notificationCount ===
                          0
                      }
                      className="flex items-center gap-1.5 text-[10px] text-emerald-400 transition hover:text-emerald-300 disabled:cursor-not-allowed disabled:text-gray-700"
                    >

                      <CheckCheck
                        size={13}
                      />

                      Mark all as read

                    </button>

                  </div>


                  {/* Notification content */}

                  <div className="max-h-[430px] overflow-y-auto">


                    {/* Loading */}

                    {notificationLoading && (
                      <div className="flex flex-col items-center justify-center px-6 py-12">

                        <RefreshCw
                          size={22}
                          className="animate-spin text-gray-600"
                        />

                        <p className="mt-3 text-xs text-gray-600">
                          Loading notifications...
                        </p>

                      </div>
                    )}


                    {/* Empty */}

                    {!notificationLoading &&
                      notifications.length ===
                        0 && (
                        <div className="flex flex-col items-center justify-center px-6 py-12 text-center">

                          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/5 text-gray-600">

                            <Bell size={21} />

                          </div>

                          <p className="mt-4 text-sm font-medium text-gray-400">
                            No notifications
                          </p>

                          <p className="mt-1 max-w-[230px] text-[10px] leading-5 text-gray-700">
                            You're all caught up.
                            New Aladdin alerts will
                            appear here.
                          </p>

                        </div>
                      )}


                    {/* Notifications */}

                    {!notificationLoading &&
                      notifications.length >
                        0 && (
                        <div>

                          {notifications.map(
                            (
                              notification,
                            ) => {

                              const isUnread =
                                Number(
                                  notification.is_read,
                                ) === 0;

                              return (
                                <button
                                  type="button"
                                  key={
                                    notification.id
                                  }
                                  onClick={() =>
                                    handleNotificationClick(
                                      notification,
                                    )
                                  }
                                  disabled={
                                    notificationActionLoading
                                  }
                                  className={`
                                    group
                                    flex
                                    w-full
                                    gap-3
                                    border-b
                                    border-white/5
                                    px-4
                                    py-4
                                    text-left
                                    transition
                                    hover:bg-white/[0.035]
                                    ${
                                      isUnread
                                        ? "bg-emerald-400/[0.025]"
                                        : ""
                                    }
                                  `}
                                >

                                  <NotificationIcon
                                    type={
                                      notification.notification_type
                                    }
                                    priority={
                                      notification.priority
                                    }
                                  />


                                  <div className="min-w-0 flex-1">

                                    <div className="flex items-start justify-between gap-3">

                                      <div className="flex min-w-0 items-center gap-2">

                                        {isUnread && (
                                          <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-400" />
                                        )}

                                        <p
                                          className={`
                                            truncate
                                            text-xs
                                            ${
                                              isUnread
                                                ? "font-semibold text-white"
                                                : "font-medium text-gray-400"
                                            }
                                          `}
                                        >
                                          {
                                            notification.title
                                          }
                                        </p>

                                      </div>

                                      <span className="shrink-0 text-[9px] text-gray-700">
                                        {formatNotificationTime(
                                          notification.created_at,
                                        )}
                                      </span>

                                    </div>


                                    <p className="mt-1.5 line-clamp-2 text-[10px] leading-5 text-gray-600">
                                      {
                                        notification.message
                                      }
                                    </p>


                                    <div className="mt-2 flex items-center gap-2">

                                      {notification.priority && (
                                        <span
                                          className={`
                                            rounded-md
                                            px-1.5
                                            py-0.5
                                            text-[8px]
                                            font-semibold
                                            uppercase
                                            tracking-wider
                                            ${
                                              notification.priority
                                                .toLowerCase()
                                                .includes(
                                                  "high",
                                                ) ||
                                              notification.priority
                                                .toLowerCase()
                                                .includes(
                                                  "critical",
                                                )
                                                ? "bg-red-400/10 text-red-400"
                                                : "bg-white/5 text-gray-600"
                                            }
                                          `}
                                        >
                                          {
                                            notification.priority
                                          }
                                        </span>
                                      )}


                                      {notification.trade_id && (
                                        <span className="rounded-md bg-white/5 px-1.5 py-0.5 text-[8px] text-gray-600">
                                          Trade{" "}
                                          {
                                            notification.trade_id
                                          }
                                        </span>
                                      )}

                                    </div>

                                  </div>


                                  {isUnread && (
                                    <div className="flex shrink-0 items-center opacity-0 transition group-hover:opacity-100">

                                      <Check
                                        size={14}
                                        className="text-emerald-400"
                                      />

                                    </div>
                                  )}

                                </button>
                              );
                            },
                          )}

                        </div>
                      )}

                  </div>


                  {/* Footer */}

                  {notifications.length >
                    0 && (
                    <div className="border-t border-white/10 px-4 py-3">

                      <div className="flex items-center justify-between">

                        <p className="text-[9px] text-gray-700">
                          {notifications.length} notification
                          {notifications.length ===
                          1
                            ? ""
                            : "s"}
                        </p>

                        <div className="flex items-center gap-1.5 text-[9px] text-gray-700">

                          <ShieldCheck
                            size={12}
                          />

                          Aladdin secure alerts

                        </div>

                      </div>

                    </div>
                  )}

                </div>
              )}

            </div>


            {/* User */}

            <div className="hidden items-center gap-3 border-l border-white/10 pl-4 sm:flex">

              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white/10 text-sm font-semibold">
                T
              </div>

              <div>

                <p className="text-xs font-medium text-white">
                  Tharindu
                </p>

                <p className="text-[10px] text-gray-600">
                  Administrator
                </p>

              </div>

              <ChevronDown
                size={15}
                className="text-gray-600"
              />

            </div>

          </div>

        </header>


        {/* =================================================
            CONTENT
            ================================================= */}

        <section className="px-5 py-8 sm:px-8 lg:px-10">


          {/* =================================================
              TITLE
              ================================================= */}

          <div className="mb-8 flex flex-col gap-5 xl:flex-row xl:items-end xl:justify-between">

            <div>

              <div className="mb-3 flex items-center gap-2">

                <span className="h-2.5 w-2.5 rounded-full bg-emerald-400" />

                <span className="text-[11px] font-medium uppercase tracking-[0.2em] text-emerald-400">
                  Backend Connected
                </span>

              </div>

              <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
                Trading Dashboard
              </h1>

              <p className="mt-2 max-w-2xl text-sm text-gray-500">
                Monitor live trading statistics and
                Aladdin trading activity.
              </p>

            </div>


            {/* Refresh */}

            <button
              type="button"
              onClick={
                handleRefresh
              }
              disabled={
                refreshing
              }
              className="flex w-fit items-center gap-2 rounded-xl border border-white/10 bg-[#0b0f15] px-4 py-3 text-sm font-medium text-gray-300 transition hover:border-white/20 hover:bg-white/5 disabled:cursor-not-allowed disabled:opacity-50"
            >

              <RefreshCw
                size={17}
                className={
                  refreshing
                    ? "animate-spin"
                    : ""
                }
              />

              {refreshing
                ? "Refreshing..."
                : "Refresh Data"}

            </button>

          </div>


          {/* =================================================
              ERROR
              ================================================= */}

          {error && (
            <div className="mb-6 rounded-xl border border-red-400/20 bg-red-400/5 p-4">

              <p className="text-sm text-red-400">
                {error}
              </p>

            </div>
          )}


          {/* =================================================
              STATISTICS
              ================================================= */}

          <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">

            <StatCard
              title="Total Trades"
              value={
                loading
                  ? "..."
                  : statistics.total_trades
              }
              subtitle={
                loading
                  ? "Loading..."
                  : `${statistics.winning_trades} winning`
              }
              icon={
                <BarChart3
                  size={21}
                />
              }
            />


            <StatCard
              title="Win Rate"
              value={
                loading
                  ? "..."
                  : `${formatNumber(
                      statistics.win_rate,
                      1,
                    )}%`
              }
              subtitle={
                loading
                  ? "Loading..."
                  : `${statistics.losing_trades} losing`
              }
              icon={
                <TrendingUp
                  size={21}
                />
              }
            />


            <StatCard
              title="Open Trades"
              value={
                loading
                  ? "..."
                  : statistics.open_trades
              }
              subtitle="Currently active"
              icon={
                <Activity
                  size={21}
                />
              }
            />


            <StatCard
              title="Total Profit"
              value={
                loading
                  ? "..."
                  : formatMoney(
                      statistics.total_profit,
                    )
              }
              subtitle={
                loading
                  ? "Loading..."
                  : `Avg ${formatMoney(
                      statistics.average_profit,
                    )}`
              }
              icon={
                <CircleDollarSign
                  size={21}
                />
              }
            />

          </div>


          {/* =================================================
              SECONDARY METRICS
              ================================================= */}

          <div className="mt-5 grid gap-5 md:grid-cols-3">

            <SmallMetric
              label="Winning Trades"
              value={
                loading
                  ? "..."
                  : statistics.winning_trades
              }
            />

            <SmallMetric
              label="Losing Trades"
              value={
                loading
                  ? "..."
                  : statistics.losing_trades
              }
            />

            <SmallMetric
              label="Profit Factor"
              value={
                loading
                  ? "..."
                  : formatNumber(
                      statistics.profit_factor,
                      2,
                    )
              }
            />

          </div>

          {/* =================================================
              CREATE TRADE
              ================================================= */}

          <div className="mt-8 rounded-2xl border border-white/10 bg-[#0a0e13]">

            <div className="border-b border-white/10 px-5 py-5">

              <h2 className="text-base font-semibold text-white">
                Create Trade
              </h2>

              <p className="mt-1 text-xs text-gray-600">
                Create a new trade through the Aladdin backend.
              </p>

            </div>


            <div className="p-5">

              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">

                {/* Symbol */}

                <div>

                  <label className="mb-2 block text-[10px] uppercase tracking-wider text-gray-500">
                    Symbol
                  </label>

                  <select
                    value={tradeForm.symbol}
                    onChange={(event) =>
                      setTradeForm({
                        ...tradeForm,
                        symbol: event.target.value,
                      })
                    }
                    className="w-full rounded-xl border border-white/10 bg-black px-3 py-3 text-sm text-white outline-none transition focus:border-emerald-400/50"
                  >
                    <option value="EUR/USD">
                      EUR/USD
                    </option>

                    <option value="GBP/USD">
                      GBP/USD
                    </option>

                    <option value="USD/JPY">
                      USD/JPY
                    </option>

                    <option value="AUD/USD">
                      AUD/USD
                    </option>
                  </select>

                </div>


                {/* Direction */}

                <div>

                  <label className="mb-2 block text-[10px] uppercase tracking-wider text-gray-500">
                    Direction
                  </label>

                  <select
                    value={tradeForm.direction}
                    onChange={(event) =>
                      setTradeForm({
                        ...tradeForm,
                        direction: event.target.value,
                      })
                    }
                    className="w-full rounded-xl border border-white/10 bg-black px-3 py-3 text-sm text-white outline-none transition focus:border-emerald-400/50"
                  >
                    <option value="Buy">
                      Buy
                    </option>

                    <option value="Sell">
                      Sell
                    </option>
                  </select>

                </div>


                {/* Entry Price */}

                <div>

                  <label className="mb-2 block text-[10px] uppercase tracking-wider text-gray-500">
                    Entry Price
                  </label>

                  <input
                    type="number"
                    step="0.00001"
                    min="0"
                    value={
                      tradeForm.entry_price || ""
                    }
                    onChange={(event) =>
                      setTradeForm({
                        ...tradeForm,
                        entry_price:
                          Number(
                            event.target.value,
                          ),
                      })
                    }
                    placeholder="1.08000"
                    className="w-full rounded-xl border border-white/10 bg-black px-3 py-3 text-sm text-white outline-none transition placeholder:text-gray-700 focus:border-emerald-400/50"
                  />

                </div>


                {/* Lot Size */}

                <div>

                  <label className="mb-2 block text-[10px] uppercase tracking-wider text-gray-500">
                    Lot Size
                  </label>

                  <input
                    type="number"
                    step="0.01"
                    min="0.01"
                    value={
                      tradeForm.lot_size || ""
                    }
                    onChange={(event) =>
                      setTradeForm({
                        ...tradeForm,
                        lot_size:
                          Number(
                            event.target.value,
                          ),
                      })
                    }
                    placeholder="0.10"
                    className="w-full rounded-xl border border-white/10 bg-black px-3 py-3 text-sm text-white outline-none transition placeholder:text-gray-700 focus:border-emerald-400/50"
                  />

                </div>


                {/* Stop Loss */}

                <div>

                  <label className="mb-2 block text-[10px] uppercase tracking-wider text-gray-500">
                    Stop Loss
                  </label>

                  <input
                    type="number"
                    step="0.00001"
                    min="0"
                    value={
                      tradeForm.stop_loss || ""
                    }
                    onChange={(event) =>
                      setTradeForm({
                        ...tradeForm,
                        stop_loss:
                          Number(
                            event.target.value,
                          ),
                      })
                    }
                    placeholder="1.07500"
                    className="w-full rounded-xl border border-white/10 bg-black px-3 py-3 text-sm text-white outline-none transition placeholder:text-gray-700 focus:border-emerald-400/50"
                  />

                </div>


                {/* Take Profit */}

                <div>

                  <label className="mb-2 block text-[10px] uppercase tracking-wider text-gray-500">
                    Take Profit
                  </label>

                  <input
                    type="number"
                    step="0.00001"
                    min="0"
                    value={
                      tradeForm.take_profit || ""
                    }
                    onChange={(event) =>
                      setTradeForm({
                        ...tradeForm,
                        take_profit:
                          Number(
                            event.target.value,
                          ),
                      })
                    }
                    placeholder="1.09000"
                    className="w-full rounded-xl border border-white/10 bg-black px-3 py-3 text-sm text-white outline-none transition placeholder:text-gray-700 focus:border-emerald-400/50"
                  />

                </div>

              </div>


              {/* Messages */}

              {tradeActionError && (
                <div className="mt-4 rounded-xl border border-red-400/20 bg-red-400/5 px-4 py-3 text-xs text-red-400">
                  {tradeActionError}
                </div>
              )}


              {tradeActionMessage && (
                <div className="mt-4 rounded-xl border border-emerald-400/20 bg-emerald-400/5 px-4 py-3 text-xs text-emerald-400">
                  {tradeActionMessage}
                </div>
              )}


              {/* AI Analysis Button */}

              <div className="mt-5 flex justify-end">
                <button
                  type="button"
                  onClick={handleAIAnalysis}
                  disabled={aiAnalyzing}
                  className="inline-flex items-center gap-2 rounded-xl border border-purple-400/20 bg-purple-400/10 px-5 py-3 text-xs font-bold text-purple-300 transition hover:bg-purple-400/20 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {aiAnalyzing ? (
                    <>
                      <RefreshCw size={14} className="animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <BrainCircuit size={14} />
                      Analyze with Aladdin AI
                    </>
                  )}
                </button>
              </div>

              {aiAnalysisError && (
                <div className="mt-4 rounded-xl border border-red-400/20 bg-red-400/5 px-4 py-3 text-xs text-red-400">
                  {aiAnalysisError}
                </div>
              )}


              {/* Create Button */}

              <div className="mt-3 flex justify-end">

                <button
                  type="button"
                  onClick={handleCreateTrade}
                  disabled={creatingTrade}
                  className="inline-flex items-center gap-2 rounded-xl bg-emerald-400 px-5 py-3 text-xs font-bold text-black transition hover:bg-emerald-300 disabled:cursor-not-allowed disabled:opacity-50"
                >

                  {creatingTrade ? (
                    <>
                      <RefreshCw
                        size={14}
                        className="animate-spin"
                      />

                      Creating...
                    </>
                  ) : (
                    <>
                      <CheckCircle2
                        size={14}
                      />

                      Create Trade
                    </>
                  )}

                </button>

              </div>

            </div>

          </div>


          {/* =================================================
              AI DECISION GATE RESULT
              ================================================= */}

          {aiAnalysis && (
            <section className="mt-8 overflow-hidden rounded-2xl border border-white/10 bg-[#0a0e13]">
              <div className="border-b border-white/10 px-5 py-5">
                <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <BrainCircuit size={19} className="text-purple-300" />
                      <h2 className="text-base font-semibold text-white">
                        Aladdin Decision Gate
                      </h2>
                    </div>
                    <p className="mt-1 text-xs text-gray-600">
                      Live market intelligence evaluated by Aladdin's multi-gate decision system.
                    </p>
                  </div>

                  <div
                    className={`inline-flex w-fit items-center gap-2 rounded-xl px-4 py-2 text-xs font-bold ${
                      aiAnalysis.decision.action === "BUY"
                        ? "bg-emerald-400/10 text-emerald-400"
                        : aiAnalysis.decision.action === "SELL"
                          ? "bg-red-400/10 text-red-400"
                          : "bg-amber-400/10 text-amber-400"
                    }`}
                  >
                    <span
                      className={`h-1.5 w-1.5 rounded-full ${
                        aiAnalysis.decision.action === "BUY"
                          ? "bg-emerald-400"
                          : aiAnalysis.decision.action === "SELL"
                            ? "bg-red-400"
                            : "bg-amber-400"
                      }`}
                    />
                    {aiAnalysis.decision.action}
                  </div>
                </div>
              </div>

              {/* Decision metrics */}
              <div className="grid gap-4 p-5 sm:grid-cols-2 lg:grid-cols-4">
                <AIMetricCard
                  label="Approved"
                  value={aiAnalysis.decision.approved ? "YES" : "NO"}
                  valueClassName={
                    aiAnalysis.decision.approved
                      ? "text-emerald-400"
                      : "text-red-400"
                  }
                />
                <AIMetricCard
                  label="Market Confidence"
                  value={`${formatNumber(aiAnalysis.decision.market_confidence, 1)}%`}
                />
                <AIMetricCard
                  label="MTF Confidence"
                  value={`${formatNumber(aiAnalysis.decision.timeframe_confidence, 1)}%`}
                />
                <AIMetricCard
                  label="Decision Confidence"
                  value={`${formatNumber(aiAnalysis.decision.decision_confidence, 1)}%`}
                  valueClassName="text-purple-300"
                />
              </div>

              {/* Decision reason */}
              <div className="border-t border-white/10 px-5 py-5">
                <p className="text-[10px] uppercase tracking-wider text-gray-600">
                  Decision Reason
                </p>
                <p className="mt-3 max-w-4xl text-sm leading-6 text-gray-300">
                  {aiAnalysis.decision.reason}
                </p>
              </div>

              {/* Gates */}
              <div className="grid gap-4 border-t border-white/10 p-5 lg:grid-cols-2">
                <GateListCard
                  title="Gates Passed"
                  items={aiAnalysis.decision.gates_passed}
                  passed
                />
                <GateListCard
                  title="Gates Failed"
                  items={aiAnalysis.decision.gates_failed}
                  passed={false}
                />
              </div>

              {/* Market intelligence */}
              <div className="border-t border-white/10 px-5 py-5">
                <div className="flex items-center gap-2">
                  <Activity size={17} className="text-blue-400" />
                  <p className="text-sm font-semibold text-white">
                    Market Intelligence
                  </p>
                </div>

                <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                  <AIMetricCard
                    label="Market Bias"
                    value={aiAnalysis.market_intelligence.market_bias}
                    valueClassName={
                      aiAnalysis.market_intelligence.market_bias === "BULLISH"
                        ? "text-emerald-400"
                        : aiAnalysis.market_intelligence.market_bias === "BEARISH"
                          ? "text-red-400"
                          : "text-amber-400"
                    }
                  />
                  <AIMetricCard
                    label="Market Confidence"
                    value={`${formatNumber(aiAnalysis.market_intelligence.confidence, 1)}%`}
                  />
                  <AIMetricCard
                    label="Risk Level"
                    value={aiAnalysis.market_intelligence.risk_level}
                    valueClassName={
                      aiAnalysis.market_intelligence.risk_level === "LOW"
                        ? "text-emerald-400"
                        : aiAnalysis.market_intelligence.risk_level === "MEDIUM"
                          ? "text-amber-400"
                          : "text-red-400"
                    }
                  />
                  <AIMetricCard
                    label="Recommendation"
                    value={aiAnalysis.market_intelligence.recommendation}
                  />
                </div>
              </div>

              {/* Structure / MTF / Session */}
              <div className="grid gap-4 border-t border-white/10 p-5 sm:grid-cols-2 lg:grid-cols-4">
                <AIMetricCard
                  label="Structure Direction"
                  value={aiAnalysis.market_intelligence.structure_direction}
                  valueClassName={
                    aiAnalysis.market_intelligence.structure_direction === "BULLISH"
                      ? "text-emerald-400"
                      : aiAnalysis.market_intelligence.structure_direction === "BEARISH"
                        ? "text-red-400"
                        : "text-amber-400"
                  }
                />
                <AIMetricCard
                  label="Structure Confirmation"
                  value={aiAnalysis.market_intelligence.structure_confirmation}
                />
                <AIMetricCard
                  label="MTF Alignment"
                  value={aiAnalysis.market_intelligence.timeframe_alignment}
                  valueClassName={
                    aiAnalysis.market_intelligence.timeframe_alignment === "FULL"
                      ? "text-emerald-400"
                      : aiAnalysis.market_intelligence.timeframe_alignment === "PARTIAL"
                        ? "text-amber-400"
                        : "text-red-400"
                  }
                />
                <AIMetricCard
                  label="Market Session"
                  value={aiAnalysis.market_intelligence.market_session}
                />
              </div>

              {/* Analysis summaries */}
              <div className="grid gap-4 border-t border-white/10 p-5 lg:grid-cols-3">
                <AIAnalysisCard
                  icon={<Activity size={16} className="text-blue-400" />}
                  title="Technical Analysis"
                  text={aiAnalysis.market_intelligence.technical_summary}
                />
                <AIAnalysisCard
                  icon={<BarChart3 size={16} className="text-purple-400" />}
                  title="News Analysis"
                  text={aiAnalysis.market_intelligence.news_summary}
                />
                <AIAnalysisCard
                  icon={<TrendingUp size={16} className="text-emerald-400" />}
                  title="Market Structure"
                  text={aiAnalysis.market_intelligence.structure_summary}
                />
              </div>

              {/* MTF and session details */}
              <div className="grid gap-4 border-t border-white/10 p-5 lg:grid-cols-2">
                <AIAnalysisCard
                  icon={<BarChart3 size={16} className="text-purple-400" />}
                  title="Multi-Timeframe Analysis"
                  text={`${aiAnalysis.market_intelligence.timeframe_summary} MTF confidence: ${formatNumber(aiAnalysis.market_intelligence.timeframe_confidence, 1)}%.`}
                />
                <AIAnalysisCard
                  icon={<Clock3 size={16} className="text-blue-400" />}
                  title="Market Session"
                  text={`${aiAnalysis.market_intelligence.session_summary} Activity: ${aiAnalysis.market_intelligence.session_activity}. Condition: ${aiAnalysis.market_intelligence.session_condition}.`}
                />
              </div>

              {/* Confidence explanation */}
              <div className="border-t border-white/10 px-5 py-5">
                <div className="flex items-center gap-2">
                  <BrainCircuit size={17} className="text-purple-300" />
                  <p className="text-sm font-semibold text-white">
                    Decision Confidence Explanation
                  </p>
                </div>
                <p className="mt-3 text-xs leading-6 text-gray-400">
                  {aiAnalysis.market_intelligence.confidence_summary}
                </p>
              </div>

              {/* Conflict */}
              <div className="border-t border-white/10 px-5 py-5">
                <div className="flex items-center gap-2">
                  {aiAnalysis.market_intelligence.conflict_detected ? (
                    <AlertTriangle size={17} className="text-amber-400" />
                  ) : (
                    <CheckCircle2 size={17} className="text-emerald-400" />
                  )}
                  <p className="text-sm font-semibold text-white">
                    Agent Conflict
                  </p>
                </div>
                <p className="mt-3 text-xs leading-6 text-gray-400">
                  {aiAnalysis.market_intelligence.conflict_summary}
                </p>
              </div>
            </section>
          )}

          {/* =================================================
              RECENT TRADES
              ================================================= */}


          {/* =================================================
              RECENT TRADES
              ================================================= */}

          <div className="mt-8 overflow-hidden rounded-2xl border border-white/10 bg-[#0a0e13]">

            <div className="flex flex-col gap-3 border-b border-white/10 px-5 py-5 sm:flex-row sm:items-center sm:justify-between">

              <div>

                <h2 className="text-base font-semibold text-white">
                  Recent Trades
                </h2>

                <p className="mt-1 text-xs text-gray-600">
                  Live trades loaded from the Aladdin
                  backend.
                </p>

              </div>

              <div className="flex items-center gap-2 text-[10px] uppercase tracking-wider text-gray-600">

                <span className="h-2 w-2 rounded-full bg-emerald-400" />

                Backend data

              </div>

            </div>


            {/* Loading */}

            {loading && (
              <div className="p-10 text-center">

                <RefreshCw
                  size={22}
                  className="mx-auto animate-spin text-gray-600"
                />

                <p className="mt-3 text-sm text-gray-600">
                  Loading trades...
                </p>

              </div>
            )}


            {/* Empty */}

            {!loading &&
              trades.length ===
                0 && (
                <div className="p-10 text-center">

                  <Activity
                    size={25}
                    className="mx-auto text-gray-700"
                  />

                  <p className="mt-3 text-sm text-gray-500">
                    No trades found.
                  </p>

                </div>
              )}


            {/* Table */}

            {!loading &&
              trades.length > 0 && (
                <div className="overflow-x-auto">

                  <table className="w-full min-w-[800px] text-left">

                    <thead>

                      <tr className="border-b border-white/10 text-[10px] uppercase tracking-wider text-gray-600">

                        <th className="px-5 py-4 font-medium">
                          Trade
                        </th>

                        <th className="px-5 py-4 font-medium">
                          Direction
                        </th>

                        <th className="px-5 py-4 font-medium">
                          Entry
                        </th>

                        <th className="px-5 py-4 font-medium">
                          Stop Loss
                        </th>

                        <th className="px-5 py-4 font-medium">
                          Take Profit
                        </th>

                        <th className="px-5 py-4 font-medium">
                          Status
                        </th>

                        <th className="px-5 py-4 font-medium">
                          Open Time
                        </th>

                        <th className="px-5 py-4 font-medium">
                          Actions
                        </th>

                      </tr>

                    </thead>


                    <tbody>

                      {trades.map(
                        (trade) => (
                          <TradeRow
                            key={trade.trade_id}
                            trade={trade}
                            onClose={handleCloseTrade}
                          />
                        ),
                      )}

                    </tbody>

                  </table>

                </div>
              )}

          </div>


          {/* =================================================
              SYSTEM STATUS
              ================================================= */}

          <div className="mt-6 grid gap-5 md:grid-cols-2">


            <div className="rounded-2xl border border-white/10 bg-[#0a0e13] p-5">

              <div className="flex items-start gap-4">

                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-emerald-400/10 text-emerald-400">

                  <CheckCircle2
                    size={20}
                  />

                </div>

                <div>

                  <h3 className="text-sm font-medium">
                    API Connection
                  </h3>

                  <p className="mt-1 text-xs leading-5 text-gray-600">
                    FastAPI backend is connected
                    and providing live trading data.
                  </p>

                </div>

              </div>

            </div>


            <div className="rounded-2xl border border-white/10 bg-[#0a0e13] p-5">

              <div className="flex items-start gap-4">

                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-emerald-400/10 text-emerald-400">

                  <ShieldCheck
                    size={20}
                  />

                </div>

                <div>

                  <h3 className="text-sm font-medium">
                    Authentication
                  </h3>

                  <p className="mt-1 text-xs leading-5 text-gray-600">
                    Dashboard requests use the JWT
                    access token from login.
                  </p>

                </div>

              </div>

            </div>

          </div>


          {/* Footer */}

          <p className="mt-8 text-center text-[10px] text-gray-700">
            Aladdin AI · Forex Trading Assistant
          </p>

        </section>

      </div>

    </main>
  );
}


/* =========================================================
   SIDEBAR ITEM
   ========================================================= */

function SidebarItem({
  icon,
  label,
  active = false,
}: {
  icon: ReactNode;
  label: string;
  active?: boolean;
}) {
  return (
    <button
      type="button"
      className={`
        flex
        w-full
        items-center
        gap-3
        rounded-xl
        px-4
        py-3
        text-sm
        transition
        ${
          active
            ? "bg-white text-black"
            : "text-gray-500 hover:bg-white/5 hover:text-white"
        }
      `}
    >
      {icon}

      <span>
        {label}
      </span>
    </button>
  );
}


/* =========================================================
   STAT CARD
   ========================================================= */

function StatCard({
  title,
  value,
  subtitle,
  icon,
}: {
  title: string;
  value: string | number;
  subtitle: string;
  icon: ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-[#0a0e13] p-5">

      <div className="flex items-start justify-between">

        <p className="text-xs text-gray-500">
          {title}
        </p>

        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/5 text-gray-500">
          {icon}
        </div>

      </div>

      <p className="mt-6 text-2xl font-semibold tracking-tight text-white">
        {value}
      </p>

      <p className="mt-2 text-xs text-emerald-400">
        {subtitle}
      </p>

    </div>
  );
}


/* =========================================================
   SMALL METRIC
   ========================================================= */

function SmallMetric({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div className="rounded-xl border border-white/10 bg-[#0a0e13] px-5 py-4">

      <p className="text-[11px] text-gray-600">
        {label}
      </p>

      <p className="mt-2 text-lg font-semibold text-white">
        {value}
      </p>

    </div>
  );
}


/* =========================================================
   AI METRIC CARD
   ========================================================= */

function AIMetricCard({
  label,
  value,
  valueClassName = "text-white",
}: {
  label: string;
  value: string;
  valueClassName?: string;
}) {
  return (
    <div className="rounded-xl border border-white/5 bg-black/20 p-4">
      <p className="text-[10px] uppercase tracking-wider text-gray-600">{label}</p>
      <p className={`mt-2 text-sm font-semibold ${valueClassName}`}>{value}</p>
    </div>
  );
}


/* =========================================================
   AI ANALYSIS CARD
   ========================================================= */

function AIAnalysisCard({
  icon,
  title,
  text,
}: {
  icon: ReactNode;
  title: string;
  text: string;
}) {
  return (
    <div className="rounded-xl border border-white/5 bg-black/20 p-5">
      <div className="flex items-center gap-2">
        {icon}
        <p className="text-sm font-semibold text-white">{title}</p>
      </div>
      <p className="mt-3 text-xs leading-6 text-gray-400">{text}</p>
    </div>
  );
}


/* =========================================================
   GATE LIST CARD
   ========================================================= */

function GateListCard({
  title,
  items,
  passed,
}: {
  title: string;
  items: string[];
  passed: boolean;
}) {
  return (
    <div className="rounded-xl border border-white/5 bg-black/20 p-5">
      <div className="flex items-center gap-2">
        {passed ? (
          <CheckCircle2 size={16} className="text-emerald-400" />
        ) : (
          <CircleAlert size={16} className="text-red-400" />
        )}
        <p className="text-sm font-semibold text-white">{title}</p>
      </div>

      {items.length === 0 ? (
        <p className="mt-3 text-xs text-gray-600">None</p>
      ) : (
        <div className="mt-3 flex flex-wrap gap-2">
          {items.map((item) => (
            <span
              key={item}
              className={`rounded-lg px-2.5 py-1.5 text-[10px] font-medium ${
                passed
                  ? "bg-emerald-400/10 text-emerald-400"
                  : "bg-red-400/10 text-red-400"
              }`}
            >
              {item}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}


/* =========================================================
   TRADE ROW
   ========================================================= */

function TradeRow({
  trade,
  onClose,
}: {
  trade: Trade;
  onClose: (
    tradeId: string,
    exitPrice: number,
  ) => Promise<void>;
}) {
  const isBuy =
    trade.direction.toLowerCase() ===
    "buy";

  const isOpen =
    trade.status.toLowerCase() ===
    "open";

  return (
    <tr className="border-b border-white/5 transition hover:bg-white/[0.025]">

      <td className="px-5 py-4">

        <div>

          <p className="text-sm font-medium text-white">
            {trade.symbol}
          </p>

          <p className="mt-1 text-[10px] text-gray-600">
            {trade.trade_id}
          </p>

        </div>

      </td>


      <td className="px-5 py-4">

        <span
          className={`
            inline-flex
            rounded-lg
            px-2.5
            py-1
            text-[10px]
            font-semibold
            ${
              isBuy
                ? "bg-emerald-400/10 text-emerald-400"
                : "bg-red-400/10 text-red-400"
            }
          `}
        >
          {trade.direction}
        </span>

      </td>


      <td className="px-5 py-4 text-xs text-gray-400">
        {formatNumber(
          trade.entry_price,
          5,
        )}
      </td>


      <td className="px-5 py-4 text-xs text-gray-500">
        {formatNumber(
          trade.stop_loss,
          5,
        )}
      </td>


      <td className="px-5 py-4 text-xs text-gray-500">
        {formatNumber(
          trade.take_profit,
          5,
        )}
      </td>


      <td className="px-5 py-4">

        <span
          className={`
            inline-flex
            items-center
            gap-1.5
            text-[10px]
            font-medium
            ${
              isOpen
                ? "text-amber-400"
                : "text-emerald-400"
            }
          `}
        >

          <span
            className={`
              h-1.5
              w-1.5
              rounded-full
              ${
                isOpen
                  ? "bg-amber-400"
                  : "bg-emerald-400"
              }
            `}
          />

          {trade.status}

        </span>

      </td>


      <td className="px-5 py-4 text-[11px] text-gray-600">
        {formatDate(
          trade.open_time,
        )}
      </td>

      <td className="px-5 py-4">
        {isOpen ? (
          <CloseTradeControl
            trade={trade}
            onClose={onClose}
          />
        ) : (
          <span className="text-[10px] text-gray-700">
            —
          </span>
        )}
      </td>

    </tr>
  );
}

/* =========================================================
   CLOSE TRADE CONTROL
   ========================================================= */

function CloseTradeControl({
  trade,
  onClose,
}: {
  trade: Trade;
  onClose: (
    tradeId: string,
    exitPrice: number,
  ) => Promise<void>;
}) {
  const [exitPrice, setExitPrice] =
    useState("");

  const [closing, setClosing] =
    useState(false);

  async function handleClose() {
    const price =
      Number(exitPrice);

    if (price <= 0) {
      return;
    }

    try {
      setClosing(true);

      await onClose(
        trade.trade_id,
        price,
      );

      setExitPrice("");
    } finally {
      setClosing(false);
    }
  }

  return (
    <div className="flex min-w-[180px] items-center gap-2">

      <input
        type="number"
        step="0.00001"
        min="0"
        value={exitPrice}
        onChange={(event) =>
          setExitPrice(
            event.target.value,
          )
        }
        placeholder="Exit price"
        className="w-24 rounded-lg border border-white/10 bg-black px-2.5 py-2 text-[10px] text-white outline-none placeholder:text-gray-700 focus:border-emerald-400/50"
      />

      <button
        type="button"
        onClick={handleClose}
        disabled={
          closing ||
          Number(exitPrice) <= 0
        }
        className="rounded-lg bg-emerald-400 px-3 py-2 text-[10px] font-semibold text-black transition hover:bg-emerald-300 disabled:cursor-not-allowed disabled:opacity-40"
      >
        {closing
          ? "Closing..."
          : "Close"}
      </button>

    </div>
  );
}