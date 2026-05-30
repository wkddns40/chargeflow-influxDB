import type { Station } from "../../types";

type Props = {
  stations: Station[];
  selectedStationId: string | null;
  loading: boolean;
  error: string | null;
  onSelect: (station: Station) => void;
};

const BOUNDS = {
  minLat: 33.0,
  maxLat: 38.8,
  minLng: 124.5,
  maxLng: 130.1
};

function clamp(value: number): number {
  return Math.min(100, Math.max(0, value));
}

function markerPosition(station: Station): { left: string; top: string } {
  const left = ((station.lng - BOUNDS.minLng) / (BOUNDS.maxLng - BOUNDS.minLng)) * 100;
  const top = 100 - ((station.lat - BOUNDS.minLat) / (BOUNDS.maxLat - BOUNDS.minLat)) * 100;
  return { left: `${clamp(left)}%`, top: `${clamp(top)}%` };
}

export function StationMap({ stations, selectedStationId, loading, error, onSelect }: Props) {
  return (
    <section className="map-region" aria-label="Station map">
      <div className="map-toolbar">
        <div>
          <h1>chargeflow-influxDB</h1>
          <p>Local station timeline package</p>
        </div>
        <div className="map-count">{loading ? "..." : stations.length}</div>
      </div>
      <div className="map-surface">
        <div className="map-water" />
        <div className="map-land" />
        <div className="map-grid" />
        {error ? <div className="map-state">{error}</div> : null}
        {!loading && !error && stations.length === 0 ? <div className="map-state">No station data</div> : null}
        {stations.map((station) => {
          const selected = station.station_id === selectedStationId;
          return (
            <button
              className={selected ? "station-marker station-marker-selected" : "station-marker"}
              key={station.station_id}
              onClick={() => onSelect(station)}
              style={markerPosition(station)}
              title={`${station.name} (${station.connector_count})`}
              aria-label={`Open ${station.name}`}
            >
              <span />
            </button>
          );
        })}
      </div>
    </section>
  );
}
