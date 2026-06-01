import { useEffect, useState } from "react";

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
  const [state, setState] = useState<StationsState>({ stations: [], loading: true, error: null });

  useEffect(() => {
    let active = true;
    getJson<StationsResponse>(stationListPath())
      .then((body) => {
        if (active) {
          setState({ stations: body.stations, loading: false, error: null });
        }
      })
      .catch((error: Error) => {
        if (active) {
          setState({ stations: [], loading: false, error: error.message });
        }
      });
    return () => {
      active = false;
    };
  }, []);

  return state;
}
