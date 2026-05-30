import { useEffect, useState } from "react";

import { getJson } from "../lib/api";
import type { Station, StationsResponse } from "../types";

type StationsState = {
  stations: Station[];
  loading: boolean;
  error: string | null;
};

export function useStations(): StationsState {
  const [state, setState] = useState<StationsState>({ stations: [], loading: true, error: null });

  useEffect(() => {
    let active = true;
    getJson<StationsResponse>("/api/stations?profile=smoke&limit=300")
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
