export function stationTimelinePath(stationId: string): string {
  const params = new URLSearchParams({ station_id: stationId });
  return `/api/grafana/station-timeline-url?${params.toString()}`;
}

export function hasStationVariable(url: string, stationId: string): boolean {
  return url.includes(`var-station_id=${encodeURIComponent(stationId)}`);
}
