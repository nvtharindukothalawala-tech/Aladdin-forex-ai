"use client";

import {
  CandlestickSeries,
  LineSeries,
  ColorType,
  CrosshairMode,
  createChart,
  createSeriesMarkers,
  type CandlestickData,
  type LineData,
  type IChartApi,
  type ISeriesApi,
  type ISeriesMarkersPluginApi,
  type SeriesMarker,
  type Time,
  type UTCTimestamp,
} from "lightweight-charts";
import {
  getMarketCandles,
  type MarketCandle,
  type MarketStructure,
  type MarketTimeframe,
} from "@/lib/api";
import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

const SUPPORTED_TIMEFRAMES: MarketTimeframe[] = [
  "M1",
  "M5",
  "M15",
  "M30",
  "H1",
  "H4",
  "D1",
  "W1",
];

const SUPPORTED_CANDLE_COUNTS = [
  300,
  1000,
  5000,
] as const;

const DEFAULT_REFRESH_INTERVAL_MS = 5_000;
const MIN_REFRESH_INTERVAL_MS = 5_000;
const DEFAULT_CANDLE_COUNT = 1000;
const MIN_CANDLE_COUNT = 50;
const MAX_CANDLE_COUNT = 5000;

type MarketChartProps = {
  symbol: string;
  timeframe?: MarketTimeframe;
  candleCount?: number;
  refreshIntervalMs?: number;
  className?: string;
  onTimeframeChange?: (
    timeframe: MarketTimeframe,
  ) => void;
};

type LatestCandleState = {
  open: number;
  high: number;
  low: number;
  close: number;
} | null;

function normalizeSymbol(
  symbol: string,
): string {
  return symbol
    .replace("/", "")
    .trim()
    .toUpperCase();
}

function clampCandleCount(
  count: number,
): number {
  return Math.max(
    MIN_CANDLE_COUNT,
    Math.min(
      Math.trunc(count),
      MAX_CANDLE_COUNT,
    ),
  );
}

function getPriceFormatting(
  symbol: string,
): {
  precision: number;
  minMove: number;
} {
  const normalizedSymbol =
    normalizeSymbol(symbol);

  if (normalizedSymbol === "XAUUSD") {
    return {
      precision: 2,
      minMove: 0.01,
    };
  }

  if (normalizedSymbol.endsWith("JPY")) {
    return {
      precision: 3,
      minMove: 0.001,
    };
  }

  return {
    precision: 5,
    minMove: 0.00001,
  };
}

function toChartData(
  candles: MarketCandle[],
): CandlestickData<UTCTimestamp>[] {
  const uniqueCandles =
    new Map<number, MarketCandle>();

  for (const candle of candles) {
    if (
      Number.isFinite(candle.time) &&
      Number.isFinite(candle.open) &&
      Number.isFinite(candle.high) &&
      Number.isFinite(candle.low) &&
      Number.isFinite(candle.close)
    ) {
      uniqueCandles.set(
        candle.time,
        candle,
      );
    }
  }

  return Array.from(
    uniqueCandles.values(),
  )
    .sort(
      (left, right) =>
        left.time - right.time,
    )
    .map(
      (candle) => ({
        time:
          candle.time as UTCTimestamp,
        open: candle.open,
        high: candle.high,
        low: candle.low,
        close: candle.close,
      }),
    );
}

function toLineData(
  points: {
    time: number;
    value: number;
  }[],
): LineData<UTCTimestamp>[] {
  const uniquePoints =
    new Map<number, number>();

  for (const point of points) {
    if (
      Number.isFinite(point.time) &&
      Number.isFinite(point.value)
    ) {
      uniquePoints.set(
        point.time,
        point.value,
      );
    }
  }

  return Array.from(
    uniquePoints.entries(),
  )
    .sort(
      ([leftTime], [rightTime]) =>
        leftTime - rightTime,
    )
    .map(
      ([time, value]) => ({
        time: time as UTCTimestamp,
        value,
      }),
    );
}


function toStructureMarkers(
  structure: MarketStructure,
): SeriesMarker<UTCTimestamp>[] {
  const markers: SeriesMarker<UTCTimestamp>[] = [];

  for (const point of structure.swing_highs) {
    if (
      Number.isFinite(point.time) &&
      Number.isFinite(point.price)
    ) {
      markers.push({
        time: point.time as UTCTimestamp,
        position: "aboveBar",
        shape: "arrowDown",
        color: "#f59e0b",
        text: "SH",
      });
    }
  }

  for (const point of structure.swing_lows) {
    if (
      Number.isFinite(point.time) &&
      Number.isFinite(point.price)
    ) {
      markers.push({
        time: point.time as UTCTimestamp,
        position: "belowBar",
        shape: "arrowUp",
        color: "#22d3ee",
        text: "SL",
      });
    }
  }

  if (
    structure.bos &&
    Number.isFinite(structure.bos.time)
  ) {
    const bullish =
      structure.bos.type === "BOS_BULLISH";

    markers.push({
      time: structure.bos.time as UTCTimestamp,
      position: bullish ? "belowBar" : "aboveBar",
      shape: bullish ? "arrowUp" : "arrowDown",
      color: bullish ? "#22c55e" : "#ef4444",
      text: "BOS",
    });
  }

  if (
    structure.choch &&
    Number.isFinite(structure.choch.time)
  ) {
    const bullish =
      structure.choch.type === "CHOCH_BULLISH";

    markers.push({
      time: structure.choch.time as UTCTimestamp,
      position: bullish ? "belowBar" : "aboveBar",
      shape: "square",
      color: "#e879f9",
      text: bullish ? "CHoCH UP" : "CHoCH DOWN",
    });
  }

  if (
    structure.liquidity_sweep &&
    Number.isFinite(structure.liquidity_sweep.time) &&
    Number.isFinite(structure.liquidity_sweep.level_price)
  ) {
    const highSide =
      structure.liquidity_sweep.type ===
      "LIQUIDITY_SWEEP_HIGH";

    markers.push({
      time:
        structure.liquidity_sweep.time as UTCTimestamp,
      position: highSide ? "aboveBar" : "belowBar",
      shape: "circle",
      color: "#fb7185",
      text: highSide ? "LS HIGH" : "LS LOW",
    });
  }

  return markers.sort(
    (left, right) =>
      Number(left.time) - Number(right.time),
  );
}

function formatPrice(
  value: number | null,
  symbol: string,
): string {
  if (
    value === null ||
    !Number.isFinite(value)
  ) {
    return "-";
  }

  const { precision } =
    getPriceFormatting(symbol);

  return value.toFixed(
    precision,
  );
}

export default function MarketChart({
  symbol,
  timeframe = "H1",
  candleCount = DEFAULT_CANDLE_COUNT,
  refreshIntervalMs =
    DEFAULT_REFRESH_INTERVAL_MS,
  className = "",
  onTimeframeChange,
}: MarketChartProps) {
  const containerRef =
    useRef<HTMLDivElement | null>(
      null,
    );

  const chartRef =
    useRef<IChartApi | null>(
      null,
    );

  const seriesRef =
    useRef<
      ISeriesApi<"Candlestick"> | null
    >(null);

  const ema20SeriesRef =
    useRef<
      ISeriesApi<"Line"> | null
    >(null);

  const rsi14SeriesRef =
    useRef<
      ISeriesApi<"Line"> | null
    >(null);

  const adx14SeriesRef =
    useRef<
      ISeriesApi<"Line"> | null
    >(null);

  const structureMarkersRef =
    useRef<
      ISeriesMarkersPluginApi<Time> | null
    >(null);

  const structureMarkerDataRef =
    useRef<SeriesMarker<UTCTimestamp>[]>([]);

  const structureVisibleRef =
    useRef(true);

  const requestGenerationRef =
    useRef(0);

  const fittedKeyRef =
    useRef<string | null>(
      null,
    );

  const [
    selectedTimeframe,
    setSelectedTimeframe,
  ] =
    useState<MarketTimeframe>(
      timeframe,
    );

  const [
    selectedCandleCount,
    setSelectedCandleCount,
  ] = useState(
    clampCandleCount(
      candleCount,
    ),
  );

  const [
    brokerSymbol,
    setBrokerSymbol,
  ] = useState<string>("");

  const [
    latestCandle,
    setLatestCandle,
  ] =
    useState<LatestCandleState>(
      null,
    );

  const [
    candleTotal,
    setCandleTotal,
  ] = useState(0);

  const [
    lastUpdated,
    setLastUpdated,
  ] =
    useState<Date | null>(
      null,
    );

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
    ema20Visible,
    setEma20Visible,
  ] = useState(true);

  const [
    rsi14Visible,
    setRsi14Visible,
  ] = useState(true);

  const [
    adx14Visible,
    setAdx14Visible,
  ] = useState(true);

  const [
    structureVisible,
    setStructureVisible,
  ] = useState(true);

  const normalizedSymbol =
    useMemo(
      () =>
        normalizeSymbol(symbol),
      [symbol],
    );

  const safeCandleCount =
    useMemo(
      () =>
        clampCandleCount(
          selectedCandleCount,
        ),
      [selectedCandleCount],
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

  useEffect(() => {
    setSelectedTimeframe(
      timeframe,
    );
  }, [timeframe]);

  useEffect(() => {
    setSelectedCandleCount(
      clampCandleCount(
        candleCount,
      ),
    );
  }, [candleCount]);

  useEffect(() => {
    const container =
      containerRef.current;

    if (!container) {
      return;
    }

    const chart =
      createChart(
        container,
        {
          autoSize: true,

          layout: {
            background: {
              type:
                ColorType.Solid,
              color: "#07101d",
            },

            textColor:
              "#94a3b8",

            panes: {
              enableResize: true,
              separatorColor:
                "rgba(148, 163, 184, 0.18)",
              separatorHoverColor:
                "rgba(56, 189, 248, 0.35)",
            },
          },

          grid: {
            vertLines: {
              color:
                "rgba(148, 163, 184, 0.08)",
            },

            horzLines: {
              color:
                "rgba(148, 163, 184, 0.08)",
            },
          },

          crosshair: {
            mode:
              CrosshairMode.Normal,

            vertLine: {
              color:
                "rgba(148, 163, 184, 0.45)",
              labelBackgroundColor:
                "#1e293b",
            },

            horzLine: {
              color:
                "rgba(148, 163, 184, 0.45)",
              labelBackgroundColor:
                "#1e293b",
            },
          },

          rightPriceScale: {
            borderColor:
              "rgba(148, 163, 184, 0.18)",

            scaleMargins: {
              top: 0.08,
              bottom: 0.08,
            },
          },

          timeScale: {
            borderColor:
              "rgba(148, 163, 184, 0.18)",

            timeVisible: true,

            secondsVisible: false,

            rightOffset: 4,

            barSpacing: 8,

            minBarSpacing: 2,
          },

          handleScroll: {
            mouseWheel: true,
            pressedMouseMove: true,
            horzTouchDrag: true,
            vertTouchDrag: true,
          },

          handleScale: {
            axisPressedMouseMove: true,
            mouseWheel: true,
            pinch: true,
          },
        },
      );

    const candleSeries =
      chart.addSeries(
        CandlestickSeries,
        {
          upColor:
            "#22c55e",

          downColor:
            "#ef4444",

          borderUpColor:
            "#22c55e",

          borderDownColor:
            "#ef4444",

          wickUpColor:
            "#22c55e",

          wickDownColor:
            "#ef4444",

          priceLineVisible: true,

          lastValueVisible: true,
        },
      );

    const structureMarkers =
      createSeriesMarkers(
        candleSeries,
        [],
        {
          autoScale: true,
          zOrder: "aboveSeries",
        },
      );

    const ema20Series =
      chart.addSeries(
        LineSeries,
        {
          color: "#f59e0b",
          lineWidth: 2,
          priceLineVisible: false,
          lastValueVisible: true,
          title: "EMA 20",
        },
      );

    const rsi14Series =
      chart.addSeries(
        LineSeries,
        {
          color: "#38bdf8",
          lineWidth: 2,
          priceLineVisible: false,
          lastValueVisible: true,
          title: "RSI 14",
          priceFormat: {
            type: "price",
            precision: 2,
            minMove: 0.01,
          },
        },
        1,
      );

    const adx14Series =
      chart.addSeries(
        LineSeries,
        {
          color: "#a78bfa",
          lineWidth: 2,
          priceLineVisible: false,
          lastValueVisible: true,
          title: "ADX 14",
          priceFormat: {
            type: "price",
            precision: 2,
            minMove: 0.01,
          },
        },
        2,
      );

    const panes = chart.panes();

    panes[0]?.setHeight(380);
    panes[1]?.setHeight(130);
    panes[2]?.setHeight(130);

    chartRef.current =
      chart;

    seriesRef.current =
      candleSeries;

    structureMarkersRef.current =
      structureMarkers;

    ema20SeriesRef.current =
      ema20Series;

    rsi14SeriesRef.current =
      rsi14Series;

    adx14SeriesRef.current =
      adx14Series;

    return () => {
      chartRef.current =
        null;

      seriesRef.current =
        null;

      structureMarkersRef.current?.detach();
      structureMarkersRef.current =
        null;
      structureMarkerDataRef.current =
        [];

      ema20SeriesRef.current =
        null;

      rsi14SeriesRef.current =
        null;

      adx14SeriesRef.current =
        null;

      chart.remove();
    };
  }, []);

  useEffect(() => {
    const candleSeries =
      seriesRef.current;

    if (!candleSeries) {
      return;
    }

    const {
      precision,
      minMove,
    } =
      getPriceFormatting(
        normalizedSymbol,
      );

    candleSeries.applyOptions({
      priceFormat: {
        type: "price",
        precision,
        minMove,
      },
    });

    ema20SeriesRef.current?.applyOptions({
      priceFormat: {
        type: "price",
        precision,
        minMove,
      },
    });
  }, [normalizedSymbol]);

  useEffect(() => {
    ema20SeriesRef.current?.applyOptions({
      visible: ema20Visible,
    });
  }, [ema20Visible]);

  useEffect(() => {
    rsi14SeriesRef.current?.applyOptions({
      visible: rsi14Visible,
    });
  }, [rsi14Visible]);

  useEffect(() => {
    adx14SeriesRef.current?.applyOptions({
      visible: adx14Visible,
    });
  }, [adx14Visible]);

  useEffect(() => {
    structureVisibleRef.current =
      structureVisible;

    structureMarkersRef.current?.setMarkers(
      structureVisible
        ? structureMarkerDataRef.current
        : [],
    );
  }, [structureVisible]);

  const loadCandles =
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
            await getMarketCandles(
              normalizedSymbol,
              selectedTimeframe,
              safeCandleCount,
            );

          if (
            currentGeneration !==
            requestGenerationRef.current
          ) {
            return;
          }

          const chartData =
            toChartData(
              result.candles,
            );

          const candleSeries =
            seriesRef.current;

          const chart =
            chartRef.current;

          if (
            !candleSeries ||
            !chart
          ) {
            return;
          }

          candleSeries.setData(
            chartData,
          );

          const ema20Data =
            toLineData(
              result.indicators.ema20.series,
            );

          ema20SeriesRef.current?.setData(
            ema20Data,
          );

          const rsi14Data =
            toLineData(
              result.indicators.rsi14.series,
            );

          rsi14SeriesRef.current?.setData(
            rsi14Data,
          );

          const adx14Data =
            toLineData(
              result.indicators.adx14.series,
            );

          adx14SeriesRef.current?.setData(
            adx14Data,
          );

          const structureMarkers =
            toStructureMarkers(
              result.market_structure,
            );

          structureMarkerDataRef.current =
            structureMarkers;

          structureMarkersRef.current?.setMarkers(
            structureVisibleRef.current
              ? structureMarkers
              : [],
          );

          setBrokerSymbol(
            result.broker_symbol,
          );

          setCandleTotal(
            chartData.length,
          );

          const latest =
            chartData.at(-1);

          setLatestCandle(
            latest
              ? {
                  open:
                    latest.open,
                  high:
                    latest.high,
                  low:
                    latest.low,
                  close:
                    latest.close,
                }
              : null,
          );

          setLastUpdated(
            new Date(),
          );

          setError(null);

          const fitKey =
            `${result.symbol}:${result.timeframe}`;

          if (
            fittedKeyRef.current !==
            fitKey
          ) {
            chart
              .timeScale()
              .fitContent();

            fittedKeyRef.current =
              fitKey;
          }
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
              : "Failed to load MT5 market data.",
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
      [
        normalizedSymbol,
        safeCandleCount,
        selectedTimeframe,
      ],
    );

  useEffect(() => {
    fittedKeyRef.current =
      null;

    setBrokerSymbol("");
    setLatestCandle(null);
    setCandleTotal(0);
    setLastUpdated(null);
    setError(null);

    void loadCandles(true);

    const refreshTimer =
      window.setInterval(
        () => {
          void loadCandles(false);
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
    loadCandles,
    safeRefreshIntervalMs,
  ]);

  const handleTimeframeChange = (
    nextTimeframe:
      MarketTimeframe,
  ) => {
    if (
      nextTimeframe ===
      selectedTimeframe
    ) {
      return;
    }

    setSelectedTimeframe(
      nextTimeframe,
    );

    onTimeframeChange?.(
      nextTimeframe,
    );
  };

  const priceDirection =
    latestCandle
      ? latestCandle.close >=
        latestCandle.open
        ? "up"
        : "down"
      : "neutral";

  return (
    <section
      className={[
        "overflow-hidden rounded-xl border border-slate-800 bg-slate-950 shadow-2xl",
        className,
      ]
        .filter(Boolean)
        .join(" ")}
      aria-label={`${normalizedSymbol} MT5 market chart`}
    >
      <div className="border-b border-slate-800 bg-slate-950/95 px-4 py-3">
        <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
          <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-semibold tracking-wide text-slate-100">
                  {normalizedSymbol}
                </h2>

                <span className="rounded border border-sky-500/30 bg-sky-500/10 px-2 py-0.5 text-[10px] font-semibold tracking-wider text-sky-300">
                  MT5 DEMO
                </span>
              </div>

              <p className="mt-0.5 text-xs text-slate-500">
                {brokerSymbol ||
                  "Broker symbol loading"}
              </p>
            </div>

            <div className="hidden h-8 w-px bg-slate-800 sm:block" />

            <div className="flex flex-wrap items-center gap-3 text-xs">
              {ema20Visible && (
                <span className="font-semibold text-amber-400">
                  EMA 20
                </span>
              )}

              <span className="text-slate-500">
                O{" "}
                <span className="font-mono text-slate-300">
                  {formatPrice(
                    latestCandle?.open ??
                      null,
                    normalizedSymbol,
                  )}
                </span>
              </span>

              <span className="text-slate-500">
                H{" "}
                <span className="font-mono text-slate-300">
                  {formatPrice(
                    latestCandle?.high ??
                      null,
                    normalizedSymbol,
                  )}
                </span>
              </span>

              <span className="text-slate-500">
                L{" "}
                <span className="font-mono text-slate-300">
                  {formatPrice(
                    latestCandle?.low ??
                      null,
                    normalizedSymbol,
                  )}
                </span>
              </span>

              <span className="text-slate-500">
                C{" "}
                <span
                  className={[
                    "font-mono font-semibold",
                    priceDirection ===
                    "up"
                      ? "text-emerald-400"
                      : priceDirection ===
                          "down"
                        ? "text-red-400"
                        : "text-slate-300",
                  ].join(" ")}
                >
                  {formatPrice(
                    latestCandle?.close ??
                      null,
                    normalizedSymbol,
                  )}
                </span>
              </span>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <div className="flex items-center gap-1 rounded-lg border border-slate-800 bg-slate-900/70 p-1">
              <span className="px-2 text-[10px] font-semibold uppercase tracking-wider text-slate-500">
                Indicators
              </span>

              <button
                type="button"
                onClick={() =>
                  setEma20Visible(
                    (visible) => !visible,
                  )
                }
                className={[
                  "rounded-md px-2.5 py-1.5 text-xs font-semibold transition-colors",
                  ema20Visible
                    ? "bg-amber-500 text-slate-950 shadow"
                    : "text-slate-400 hover:bg-slate-800 hover:text-slate-100",
                ].join(" ")}
                aria-pressed={ema20Visible}
                title={
                  ema20Visible
                    ? "Hide EMA 20"
                    : "Show EMA 20"
                }
              >
                EMA 20
              </button>

              <button
                type="button"
                onClick={() =>
                  setRsi14Visible(
                    (visible) => !visible,
                  )
                }
                className={[
                  "rounded-md px-2.5 py-1.5 text-xs font-semibold transition-colors",
                  rsi14Visible
                    ? "bg-sky-500 text-slate-950 shadow"
                    : "text-slate-400 hover:bg-slate-800 hover:text-slate-100",
                ].join(" ")}
                aria-pressed={rsi14Visible}
                title={
                  rsi14Visible
                    ? "Hide RSI 14"
                    : "Show RSI 14"
                }
              >
                RSI 14
              </button>

              <button
                type="button"
                onClick={() =>
                  setAdx14Visible(
                    (visible) => !visible,
                  )
                }
                className={[
                  "rounded-md px-2.5 py-1.5 text-xs font-semibold transition-colors",
                  adx14Visible
                    ? "bg-violet-500 text-slate-950 shadow"
                    : "text-slate-400 hover:bg-slate-800 hover:text-slate-100",
                ].join(" ")}
                aria-pressed={adx14Visible}
                title={
                  adx14Visible
                    ? "Hide ADX 14"
                    : "Show ADX 14"
                }
              >
                ADX 14
              </button>

              <button
                type="button"
                onClick={() =>
                  setStructureVisible(
                    (visible) => !visible,
                  )
                }
                className={[
                  "rounded-md px-2.5 py-1.5 text-xs font-semibold transition-colors",
                  structureVisible
                    ? "bg-fuchsia-500 text-slate-950 shadow"
                    : "text-slate-400 hover:bg-slate-800 hover:text-slate-100",
                ].join(" ")}
                aria-pressed={structureVisible}
                title={
                  structureVisible
                    ? "Hide market structure"
                    : "Show market structure"
                }
              >
                Structure
              </button>
            </div>

            <div className="flex items-center gap-1 rounded-lg border border-slate-800 bg-slate-900/70 p-1">
              {SUPPORTED_TIMEFRAMES.map(
                (
                  chartTimeframe,
                ) => {
                  const active =
                    chartTimeframe ===
                    selectedTimeframe;

                  return (
                    <button
                      key={
                        chartTimeframe
                      }
                      type="button"
                      onClick={() =>
                        handleTimeframeChange(
                          chartTimeframe,
                        )
                      }
                      className={[
                        "rounded-md px-3 py-1.5 text-xs font-semibold transition-colors",
                        active
                          ? "bg-sky-500 text-slate-950 shadow"
                          : "text-slate-400 hover:bg-slate-800 hover:text-slate-100",
                      ].join(" ")}
                      aria-pressed={
                        active
                      }
                    >
                      {chartTimeframe}
                    </button>
                  );
                },
              )}
            </div>

            <div className="flex items-center gap-1 rounded-lg border border-slate-800 bg-slate-900/70 p-1">
              {SUPPORTED_CANDLE_COUNTS.map(
                (countOption) => {
                  const active =
                    countOption ===
                    safeCandleCount;

                  return (
                    <button
                      key={
                        countOption
                      }
                      type="button"
                      onClick={() =>
                        setSelectedCandleCount(
                          countOption,
                        )
                      }
                      className={[
                        "rounded-md px-2.5 py-1.5 text-xs font-semibold transition-colors",
                        active
                          ? "bg-emerald-500 text-slate-950 shadow"
                          : "text-slate-400 hover:bg-slate-800 hover:text-slate-100",
                      ].join(" ")}
                      aria-pressed={
                        active
                      }
                      title={`${countOption} candles`}
                    >
                      {countOption ===
                      5000
                        ? "5K"
                        : countOption ===
                            1000
                          ? "1K"
                          : "300"}
                    </button>
                  );
                },
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="relative h-[620px] min-h-[480px] w-full bg-[#07101d] md:h-[700px]">
        <div
          ref={containerRef}
          className="h-full w-full"
        />

        {loading && (
          <div className="pointer-events-none absolute inset-0 flex items-center justify-center bg-slate-950/60 backdrop-blur-[1px]">
            <div className="rounded-lg border border-slate-800 bg-slate-950/90 px-4 py-3 text-sm text-slate-300 shadow-xl">
              Loading real MT5 candles...
            </div>
          </div>
        )}

        {!loading &&
          error && (
            <div className="absolute inset-0 flex items-center justify-center bg-slate-950/80 px-6">
              <div className="max-w-md rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-center">
                <p className="text-sm font-semibold text-red-300">
                  Market data unavailable
                </p>

                <p className="mt-2 text-xs leading-5 text-red-200/80">
                  {error}
                </p>

                <button
                  type="button"
                  onClick={() =>
                    void loadCandles(
                      true,
                    )
                  }
                  className="mt-3 rounded-md border border-red-400/40 px-3 py-1.5 text-xs font-semibold text-red-200 transition-colors hover:bg-red-400/10"
                >
                  Retry
                </button>
              </div>
            </div>
          )}

        {!loading &&
          !error &&
          candleTotal === 0 && (
            <div className="pointer-events-none absolute inset-0 flex items-center justify-center bg-slate-950/70">
              <p className="text-sm text-slate-400">
                No MT5 candle data
                returned.
              </p>
            </div>
          )}
      </div>

      <div className="flex flex-col gap-2 border-t border-slate-800 bg-slate-950 px-4 py-2 text-[11px] text-slate-500 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1">
          <span>
            Timeframe{" "}
            <strong className="font-semibold text-slate-300">
              {selectedTimeframe}
            </strong>
          </span>

          <span>
            Candles{" "}
            <strong className="font-semibold text-slate-300">
              {candleTotal}
            </strong>
          </span>

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
                : "-"}
            </strong>
          </span>
        </div>

        <a
          href="https://www.tradingview.com/"
          target="_blank"
          rel="noreferrer"
          className="w-fit text-slate-500 transition-colors hover:text-slate-300"
        >
          Charts by TradingView
        </a>
      </div>
    </section>
  );
}
