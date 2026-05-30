import { useMemo, useState } from "react";

import { StationMap } from "./components/map/StationMap";
import { StationDetailDrawer } from "./components/station/StationDetailDrawer";
import { useStations } from "./hooks/useStations";
import type { Station } from "./types";
import "./styles.css";

export default function App() {
  const { stations, loading, error } = useStations();
  const [selected, setSelected] = useState<Station | null>(null);

  const selectedStation = useMemo(() => {
    if (selected && stations.some((station) => station.station_id === selected.station_id)) {
      return selected;
    }
    return stations[0] ?? null;
  }, [selected, stations]);

  return (
    <main className="app-shell">
      <StationMap
        stations={stations}
        selectedStationId={selectedStation?.station_id ?? null}
        loading={loading}
        error={error}
        onSelect={setSelected}
      />
      <StationDetailDrawer station={selectedStation} />
    </main>
  );
}
