import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { MapShell } from "./components/map/MapShell";
import { useStations } from "./hooks/useStations";
import "./styles.css";

const queryClient = new QueryClient();

function StationTimelineMap() {
  const { stations, loading, error } = useStations();

  return <MapShell stations={stations} loading={loading} error={error} />;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <StationTimelineMap />
    </QueryClientProvider>
  );
}
