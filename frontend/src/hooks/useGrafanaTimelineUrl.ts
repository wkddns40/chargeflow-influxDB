import { useEffect, useState } from "react";

import { getJson } from "../lib/api";
import { stationTimelinePath } from "../lib/grafana";
import type { GrafanaUrlResponse } from "../types";

type TimelineState = {
  url: string | null;
  loading: boolean;
  error: string | null;
};

export function useGrafanaTimelineUrl(stationId: string | null): TimelineState {
  const [state, setState] = useState<TimelineState>({ url: null, loading: false, error: null });

  useEffect(() => {
    if (!stationId) {
      setState({ url: null, loading: false, error: null });
      return;
    }

    let active = true;
    setState({ url: null, loading: true, error: null });
    getJson<GrafanaUrlResponse>(stationTimelinePath(stationId))
      .then((body) => {
        if (active) {
          setState({ url: body.url, loading: false, error: null });
        }
      })
      .catch((error: Error) => {
        if (active) {
          setState({ url: null, loading: false, error: error.message });
        }
      });
    return () => {
      active = false;
    };
  }, [stationId]);

  return state;
}
