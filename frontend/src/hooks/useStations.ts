import { useQuery } from "@tanstack/react-query";

import { getJson } from "../lib/api";
import type { Station, StationProfile, StationsResponse } from "../types";

export const DEFAULT_STATION_PROFILE: StationProfile = "seoul-gyeonggi";
export const DEFAULT_STATION_LIMIT = 700;

export function stationListPath(
  profile: StationProfile = DEFAULT_STATION_PROFILE,
  limit: number = DEFAULT_STATION_LIMIT
): string {
  const params = new URLSearchParams({ profile, limit: String(limit) });
  return `/api/stations?${params.toString()}`;
}

type StationsState = {
  stations: Station[];
  loading: boolean;
  error: string | null;
};

export function useStations(): StationsState {
  const query = useQuery({
    queryKey: ["stations", DEFAULT_STATION_PROFILE, DEFAULT_STATION_LIMIT],
    queryFn: () => getJson<StationsResponse>(stationListPath())
  });

  return {
    stations: query.data?.stations ?? [],
    loading: query.isLoading,
    error: query.error instanceof Error ? query.error.message : null
  };
}
