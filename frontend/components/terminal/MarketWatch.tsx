"use client";

import {
  getMarketQuotes,
  type MarketQuote,
} from "@/lib/api";
import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

const DEFAULT_REFRESH_INTERVAL_MS = 1_000;
const MIN_REFRESH_INTERVAL_MS = 1_000;

type MarketWatchProps = {
  selectedSymbol: string;
  onSelectSymbol: (symbol: string) => void;
  refreshIntervalMs?: number;
  className?: string;
};

function normalizeSymbol(
  symbol: string,
): string {
  return symbol
    .replace("/", "")
    .trim()
    .toUpperCase();
}

function formatPrice(
  value: number | null,
  digits: number | null,
): string {
  if (
    value === null ||
    !Number.isFinite(value)
  ) {
    return "—";
  }

  const safeDigits =
    digits !== null &&
    Number.isInteger(digits) &&
    digits >= 0 &&
    digits <= 10
      ? digits
      : 5;

  return value.toFixed(
    safeDigits,
  );
}

function formatSpread(
  quote: MarketQuote,
): string {
  if (
    !quote.available ||
    quote.spread_points === null ||
    !Number.isFinite(
      quote.spread_points,
    )
  ) {
    return "—";
  }

  return quote.spread_points.toFixed(
    1,
  );
}

function formatTickTime(
  time: number | null,
): string {
  if (
    time === null ||
    !Number.isFinite(time) ||
    time <= 0
  ) {
    return "—";
  }

  return new Date(
    time * 1000,
  ).toLocaleTimeString();
}

export default function MarketWatch({
  selectedSymbol,
  onSelectSymbol,
  refreshIntervalMs =
    DEFAULT_REFRESH_INTERVAL_MS,
  className = "",
}: MarketWatchProps) {
  const requestGenerationRef =
    useRef(0);

  const [
    quotes,
    setQuotes,
  ] =
    useState<MarketQuote[]>([]);

  const [
    availableCount,
    setAvailableCount,
  ] = useState(0);

  const [
    unavailableCount,
    setUnavailableCount,
  ] = useState(0);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] =
    useState<string | null>(
      null,
    );

  const [
    lastUpdated,
    setLastUpdated,
  ] =
    useState<Date | null>(
      null,
    );

  const normalizedSelectedSymbol =
    useMemo(
      () =>
        normalizeSymbol(
          selectedSymbol,
        ),
      [selectedSymbol],
    );

  const safeRefreshIntervalMs =
    useMemo(
      () =>
        Math.max(
          MIN_REFRESH_INTERVAL_MS,
          Math.trunc(
            refreshIntervalMs,
          ),
        ),
      [refreshIntervalMs],
    );

  const loadQuotes =
    useCallback(
      async (
        showLoading: boolean,
      ) => {
        const currentGeneration =
          ++requestGenerationRef.current;

        if (showLoading) {
          setLoading(true);
        }

        try {
          const result =
            await getMarketQuotes();

          if (
            currentGeneration !==
            requestGenerationRef.current
          ) {
            return;
          }

          setQuotes(
            result.quotes,
          );

          setAvailableCount(
            result.available_count,
          );

          setUnavailableCount(
            result.unavailable_count,
          );

          setLastUpdated(
            new Date(),
          );

          setError(null);
        } catch (loadError) {
          if (
            currentGeneration !==
            requestGenerationRef.current
          ) {
            return;
          }

          setError(
            loadError instanceof Error
              ? loadError.message
              : "Failed to load MT5 market quotes.",
          );
        } finally {
          if (
            currentGeneration ===
            requestGenerationRef.current
          ) {
            setLoading(false);
          }
        }
      },
      [],
    );

  useEffect(() => {
    void loadQuotes(true);

    const refreshTimer =
      window.setInterval(
        () => {
          void loadQuotes(false);
        },
        safeRefreshIntervalMs,
      );

    return () => {
      window.clearInterval(
        refreshTimer,
      );

      requestGenerationRef.current +=
        1;
    };
  }, [
    loadQuotes,
    safeRefreshIntervalMs,
  ]);

  return (
    <section
      className={[
        "overflow-hidden rounded-xl border border-slate-800 bg-slate-950 shadow-2xl",
        className,
      ]
        .filter(Boolean)
        .join(" ")}
      aria-label="MT5 Market Watch"
    >
      <div className="border-b border-slate-800 bg-slate-950/95 px-4 py-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-semibold tracking-wide text-slate-100">
                Market Watch
              </h2>

              <span className="rounded border border-sky-500/30 bg-sky-500/10 px-2 py-0.5 text-[10px] font-semibold tracking-wider text-sky-300">
                MT5 DEMO
              </span>
            </div>

            <p className="mt-1 text-[11px] text-slate-500">
              Real broker bid / ask quotes
            </p>
          </div>

          <div className="flex items-center gap-2 text-[10px]">
            <span className="rounded border border-emerald-500/20 bg-emerald-500/10 px-2 py-1 font-semibold text-emerald-300">
              {availableCount} LIVE
            </span>

            {unavailableCount > 0 && (
              <span className="rounded border border-amber-500/20 bg-amber-500/10 px-2 py-1 font-semibold text-amber-300">
                {unavailableCount} UNAVAILABLE
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <div className="min-w-0">
          <div className="grid grid-cols-[1.25fr_1fr_1fr_0.7fr] border-b border-slate-800 bg-slate-900/60 px-3 py-2 text-[10px] font-semibold uppercase tracking-wider text-slate-500">
            <span>Symbol</span>
            <span className="text-right">
              Bid
            </span>
            <span className="text-right">
              Ask
            </span>
            <span className="text-right">
              Spread
            </span>
          </div>

          {loading &&
            quotes.length === 0 && (
              <div className="px-4 py-10 text-center text-xs text-slate-400">
                Loading real MT5 quotes…
              </div>
            )}

          {!loading &&
            error &&
            quotes.length === 0 && (
              <div className="px-4 py-8 text-center">
                <p className="text-sm font-semibold text-red-300">
                  Market Watch unavailable
                </p>

                <p className="mt-2 text-xs leading-5 text-red-200/70">
                  {error}
                </p>

                <button
                  type="button"
                  onClick={() =>
                    void loadQuotes(
                      true,
                    )
                  }
                  className="mt-3 rounded-md border border-red-400/40 px-3 py-1.5 text-xs font-semibold text-red-200 transition-colors hover:bg-red-400/10"
                >
                  Retry
                </button>
              </div>
            )}

          {!loading &&
            !error &&
            quotes.length === 0 && (
              <div className="px-4 py-10 text-center text-xs text-slate-400">
                No MT5 quotes returned.
              </div>
            )}

          {quotes.map(
            (quote) => {
              const selected =
                normalizeSymbol(
                  quote.symbol,
                ) ===
                normalizedSelectedSymbol;

              const available =
                quote.available;

              return (
                <button
                  key={quote.symbol}
                  type="button"
                  onClick={() => {
                    if (available) {
                      onSelectSymbol(
                        quote.display_symbol,
                      );
                    }
                  }}
                  disabled={!available}
                  title={
                    available
                      ? `${quote.broker_symbol ?? quote.symbol} • Updated ${formatTickTime(
                          quote.time,
                        )}`
                      : quote.error ??
                        `${quote.display_symbol} quote unavailable`
                  }
                  className={[
                    "grid w-full grid-cols-[1.25fr_1fr_1fr_0.7fr] items-center border-b border-slate-900 px-3 py-2.5 text-left transition-colors last:border-b-0",
                    selected
                      ? "bg-sky-500/10"
                      : available
                        ? "hover:bg-slate-900/70"
                        : "cursor-not-allowed bg-slate-950/40 opacity-60",
                  ].join(" ")}
                >
                  <span className="min-w-0">
                    <span
                      className={[
                        "block truncate text-xs font-semibold",
                        selected
                          ? "text-sky-300"
                          : available
                            ? "text-slate-200"
                            : "text-slate-500",
                      ].join(" ")}
                    >
                      {quote.display_symbol}
                    </span>

                    <span className="mt-0.5 block truncate text-[9px] text-slate-600">
                      {available
                        ? quote.broker_symbol ??
                          quote.symbol
                        : "Unavailable"}
                    </span>
                  </span>

                  <span
                    className={[
                      "text-right font-mono text-xs",
                      available
                        ? "text-slate-200"
                        : "text-slate-600",
                    ].join(" ")}
                  >
                    {formatPrice(
                      quote.bid,
                      quote.digits,
                    )}
                  </span>

                  <span
                    className={[
                      "text-right font-mono text-xs",
                      available
                        ? "text-slate-200"
                        : "text-slate-600",
                    ].join(" ")}
                  >
                    {formatPrice(
                      quote.ask,
                      quote.digits,
                    )}
                  </span>

                  <span
                    className={[
                      "text-right font-mono text-xs",
                      available
                        ? "text-slate-400"
                        : "text-slate-600",
                    ].join(" ")}
                  >
                    {formatSpread(
                      quote,
                    )}
                  </span>
                </button>
              );
            },
          )}
        </div>
      </div>

      {error &&
        quotes.length > 0 && (
          <div className="border-t border-amber-500/20 bg-amber-500/5 px-3 py-2 text-[10px] text-amber-300">
            Latest refresh failed: {error}
          </div>
        )}

      <div className="flex flex-wrap items-center justify-between gap-2 border-t border-slate-800 bg-slate-950 px-4 py-2 text-[10px] text-slate-500">
        <span>
          Refresh{" "}
          <strong className="font-semibold text-slate-300">
            {Math.round(
              safeRefreshIntervalMs /
                1000,
            )}
            s
          </strong>
        </span>

        <span>
          Updated{" "}
          <strong className="font-semibold text-slate-300">
            {lastUpdated
              ? lastUpdated.toLocaleTimeString()
              : "—"}
          </strong>
        </span>
      </div>
    </section>
  );
}