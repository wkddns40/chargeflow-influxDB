import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { fullscreenButtonLabel, GrafanaTimelineFrame, timelineShellClass } from "./GrafanaTimelineFrame";

describe("GrafanaTimelineFrame", () => {
  it("renders loading, error, and empty timeline states", () => {
    expect(renderToStaticMarkup(<GrafanaTimelineFrame url={null} loading={true} error={null} />)).toContain(
      "Loading timeline"
    );
    expect(renderToStaticMarkup(<GrafanaTimelineFrame url={null} loading={false} error="Grafana failed" />)).toContain(
      "timeline-error"
    );
    expect(renderToStaticMarkup(<GrafanaTimelineFrame url={null} loading={false} error={null} />)).toContain(
      "Select station"
    );
  });

  it("renders the Grafana iframe with the selected station variable", () => {
    const url = "https://grafana.woonjang.dev/d/station?var-station_id=ST-0001";
    const html = renderToStaticMarkup(<GrafanaTimelineFrame url={url} loading={false} error={null} />);

    expect(html).toContain('class="timeline-shell"');
    expect(html).toContain('title="Grafana station timeline"');
    expect(html).toContain('src="https://grafana.woonjang.dev/d/station?var-station_id=ST-0001"');
    expect(html.toLowerCase()).toContain("allowfullscreen");
  });

  it("keeps explicit fullscreen and panel return labels", () => {
    expect(timelineShellClass(false)).toBe("timeline-shell");
    expect(timelineShellClass(true)).toBe("timeline-shell timeline-shell-fullscreen");
    expect(fullscreenButtonLabel(false)).toBe("Open Grafana fullscreen");
    expect(fullscreenButtonLabel(true)).toBe("Return to panel view");
  });
});
