import { useCallback, useEffect, useMemo, useState } from "react";
import { ScatterplotLayer } from "@deck.gl/layers";
import DeckGL from "@deck.gl/react";
import { Map as MapLibreMap } from "react-map-gl/maplibre";
import "maplibre-gl/dist/maplibre-gl.css";

import { INITIAL_VIEW_STATE, MAP_MAX_BOUNDS, MAP_STYLE_URL, REFERENCE_VIEWPORT_SIZE } from "../../constants/viewport";
import { useGrafanaTimelineUrl } from "../../hooks/useGrafanaTimelineUrl";
import {
  getBboxFitViewState,
  getStationFocusViewState,
  getStationsBbox,
  getValidData
} from "../../lib/geo";
import type { Station, ViewState } from "../../types";
import { AskPanel } from "../search/AskPanel";
import { GrafanaTimelineFrame } from "../station/GrafanaTimelineFrame";

type MapShellProps = {
  stations: Station[];
  loading: boolean;
  error: string | null;
};

type StageTransform = {
  scale: number;
  x: number;
  y: number;
};

const MARKER_COLORS: [number, number, number, number][] = [
  [44, 162, 105, 225],
  [211, 72, 64, 222],
  [238, 166, 48, 225],
  [54, 83, 132, 205]
];
const SELECTED_MARKER_COLOR: [number, number, number, number] = [217, 71, 63, 245];
const SELECTED_MARKER_MIN_RADIUS = 28;
const SELECTED_MARKER_MAX_RADIUS = 40;
const ASK_RESULT_LIMIT = 3;
const ASK_RESULT_FIT_PADDING = {
  top: 120,
  right: 430,
  bottom: 180,
  left: 420
};
const INITIAL_ASK_QUERY = "강남구청역 가까운 충전소는";
const INITIAL_ASK_RESULT_IDS = ["ST-0514", "ST-0224", "ST-0066"];
const INITIAL_SELECTED_STATION_ID = "ST-0224";

function getStageTransform(): StageTransform {
  if (typeof window === "undefined") {
    return { scale: 1, x: 0, y: 0 };
  }

  const scale = Math.min(
    window.innerWidth / REFERENCE_VIEWPORT_SIZE.width,
    window.innerHeight / REFERENCE_VIEWPORT_SIZE.height
  );
  return {
    scale,
    x: (window.innerWidth - REFERENCE_VIEWPORT_SIZE.width * scale) / 2,
    y: (window.innerHeight - REFERENCE_VIEWPORT_SIZE.height * scale) / 2
  };
}

export function getStationMarkerSize(
  station: Station,
  selectedStationId: string | null,
  zoom: number,
  isAskResult = false
): number {
  if (station.station_id !== selectedStationId) {
    const maxKw = Number(station.max_kw);
    const markerKw = Number.isFinite(maxKw) ? maxKw : 50;
    const baseRadius = Math.max(5, Math.min(13, markerKw / 18));
    return isAskResult ? Math.max(18, Math.min(24, baseRadius * 1.8)) : baseRadius;
  }

  const zoomRadius = 16 + Math.max(0, zoom - INITIAL_VIEW_STATE.zoom) * 4;
  return Math.min(SELECTED_MARKER_MAX_RADIUS, Math.max(SELECTED_MARKER_MIN_RADIUS, zoomRadius));
}

export function getStationMarkerColor(station: Station, selectedStationId: string | null): [number, number, number, number] {
  if (station.station_id === selectedStationId) {
    return SELECTED_MARKER_COLOR;
  }
  const digits = Number(station.station_id.replace(/\D/g, ""));
  return MARKER_COLORS[digits % MARKER_COLORS.length];
}

export function MapShell({ stations, loading, error }: MapShellProps) {
  const [viewState, setViewState] = useState<ViewState>(INITIAL_VIEW_STATE);
  const [stageTransform, setStageTransform] = useState<StageTransform>(getStageTransform);
  const [selected, setSelected] = useState<Station | null>(null);
  const [askResults, setAskResults] = useState<Station[] | null>(null);
  const [initialDemoApplied, setInitialDemoApplied] = useState(false);
  const timeline = useGrafanaTimelineUrl(selected?.station_id ?? null);
  const layerStations = askResults ?? stations;
  const validStations = useMemo(() => getValidData(layerStations), [layerStations]);
  const isAskResultMode = askResults !== null;
  const selectedStationId = selected?.station_id ?? null;

  const handleFocusStation = useCallback((station: Station) => {
    setSelected(station);
    setViewState((currentViewState) => getStationFocusViewState(station, currentViewState));
  }, []);

  const handleApplyAskResults = useCallback(
    (results: Station[]) => {
      const limitedResults = results.slice(0, ASK_RESULT_LIMIT);
      setAskResults(limitedResults);
      setSelected(null);
      const bounds = getStationsBbox(limitedResults);
      if (bounds) {
        setViewState((currentViewState) =>
          getBboxFitViewState(bounds, REFERENCE_VIEWPORT_SIZE, currentViewState, ASK_RESULT_FIT_PADDING)
        );
        return;
      }

      if (limitedResults[0]) {
        handleFocusStation(limitedResults[0]);
      }
    },
    [handleFocusStation]
  );

  const handleResetMapHome = useCallback(() => {
    setAskResults(null);
    setSelected(null);
    setViewState(INITIAL_VIEW_STATE);
  }, []);

  useEffect(() => {
    const updateStageScale = () => {
      setStageTransform(getStageTransform());
    };

    updateStageScale();
    window.addEventListener("resize", updateStageScale);
    return () => window.removeEventListener("resize", updateStageScale);
  }, []);

  useEffect(() => {
    if (initialDemoApplied || loading || stations.length === 0) {
      return;
    }

    const stationsById = new Map(stations.map((station) => [station.station_id, station]));
    const initialResults = INITIAL_ASK_RESULT_IDS.flatMap((stationId) => {
      const station = stationsById.get(stationId);
      return station ? [station] : [];
    });
    const fallbackResults = initialResults.length > 0 ? initialResults : stations.slice(0, ASK_RESULT_LIMIT);
    const initialSelected = stationsById.get(INITIAL_SELECTED_STATION_ID) ?? fallbackResults[0] ?? null;

    setInitialDemoApplied(true);
    setAskResults(fallbackResults);
    setSelected(initialSelected);
    const bounds = getStationsBbox(fallbackResults);
    if (bounds) {
      setViewState((currentViewState) =>
        getBboxFitViewState(bounds, REFERENCE_VIEWPORT_SIZE, currentViewState, ASK_RESULT_FIT_PADDING)
      );
    }
  }, [initialDemoApplied, loading, stations]);

  const stationLayer = useMemo(
    () =>
      new ScatterplotLayer<Station>({
        id: "station-points",
        data: validStations,
        pickable: true,
        radiusUnits: "pixels",
        stroked: true,
        filled: true,
        lineWidthUnits: "pixels",
        getLineWidth: (station: Station) => (station.station_id === selectedStationId ? 5 : isAskResultMode ? 2 : 0),
        getRadius: (station: Station) =>
          getStationMarkerSize(station, selectedStationId, viewState.zoom, isAskResultMode),
        getPosition: (station: Station) => [station.lng, station.lat],
        getFillColor: (station: Station) => getStationMarkerColor(station, selectedStationId),
        getLineColor: () => [255, 255, 255, 245],
        onClick: ({ object }: { object?: Station | null }) => {
          if (object) {
            handleFocusStation(object);
          }
        }
      }),
    [handleFocusStation, isAskResultMode, selectedStationId, validStations, viewState.zoom]
  );

  return (
    <div className="map-shell-frame">
      <div
        className={selected ? "map-shell right-panels-enabled side-panel-open" : "map-shell right-panels-enabled"}
        style={{
          transform: `translate(${stageTransform.x}px, ${stageTransform.y}px) scale(${stageTransform.scale})`
        }}
      >
        <DeckGL
          layers={[stationLayer]}
          viewState={viewState}
          onViewStateChange={({ viewState: nextViewState }: { viewState: ViewState }) => setViewState(nextViewState)}
          controller={{ dragPan: true, scrollZoom: true, doubleClickZoom: false, dragRotate: false }}
        >
          <MapLibreMap reuseMaps mapStyle={MAP_STYLE_URL} maxBounds={MAP_MAX_BOUNDS} />
        </DeckGL>

        <aside className="summary-panel">
          <p className="eyebrow">ChargeFlow KR</p>
          <h1>InfluxDB timeline demo</h1>
          <dl>
            <div>
              <dt>Loaded stations</dt>
              <dd>{loading ? "..." : validStations.length.toLocaleString()}</dd>
            </div>
            <div>
              <dt>Data mode</dt>
              <dd>Vercel FastAPI</dd>
            </div>
          </dl>
          {error ? <p className="panel-message">{error}</p> : null}
        </aside>

        <div className="right-panel-stack">
          <AskPanel
            initialMessage={INITIAL_ASK_QUERY}
            initialResults={initialDemoApplied ? askResults ?? [] : []}
            onApplyResults={handleApplyAskResults}
            onSelectResult={handleFocusStation}
            onClearResults={handleResetMapHome}
          />
        </div>

        {selected && (
          <aside className="timeline-side-panel" aria-label="Station Grafana timeline">
            <div className="side-panel-station">
              <div>
                <p className="eyebrow">{selected.station_id}</p>
                <h2>{selected.name}</h2>
                <p className="station-address">{selected.address}</p>
              </div>
              <button type="button" aria-label="Close station timeline" onClick={() => setSelected(null)}>
                x
              </button>
            </div>
            <dl className="station-facts">
              <div>
                <dt>Region</dt>
                <dd>{selected.region}</dd>
              </div>
              <div>
                <dt>Operator</dt>
                <dd>{selected.operator}</dd>
              </div>
              <div>
                <dt>Connectors</dt>
                <dd>{selected.connector_count}</dd>
              </div>
            </dl>
            <GrafanaTimelineFrame url={timeline.url} loading={timeline.loading} error={timeline.error} />
          </aside>
        )}
      </div>
    </div>
  );
}
