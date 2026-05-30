import { useGrafanaTimelineUrl } from "../../hooks/useGrafanaTimelineUrl";
import type { Station } from "../../types";
import { GrafanaTimelineFrame } from "./GrafanaTimelineFrame";

type Props = {
  station: Station | null;
};

export function StationDetailDrawer({ station }: Props) {
  const timeline = useGrafanaTimelineUrl(station?.station_id ?? null);

  return (
    <aside className="station-panel" aria-label="Station detail">
      {station ? (
        <>
          <div className="station-header">
            <div>
              <p>{station.station_id}</p>
              <h2>{station.name}</h2>
            </div>
            <span className="connector-pill">{station.connector_count}</span>
          </div>
          <dl className="station-facts">
            <div>
              <dt>Region</dt>
              <dd>{station.region}</dd>
            </div>
            <div>
              <dt>Operator</dt>
              <dd>{station.operator}</dd>
            </div>
            <div>
              <dt>Address</dt>
              <dd>{station.address}</dd>
            </div>
          </dl>
          <GrafanaTimelineFrame url={timeline.url} loading={timeline.loading} error={timeline.error} />
        </>
      ) : (
        <div className="empty-panel">
          <h2>Station timeline</h2>
          <p>Select a station marker to load the 24h Grafana panel.</p>
        </div>
      )}
    </aside>
  );
}
