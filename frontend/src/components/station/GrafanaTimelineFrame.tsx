import { Maximize2, Minimize2 } from "lucide-react";
import { useEffect, useRef, useState } from "react";

type Props = {
  url: string | null;
  loading: boolean;
  error: string | null;
};

export function GrafanaTimelineFrame({ url, loading, error }: Props) {
  const shellRef = useRef<HTMLDivElement>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);

  useEffect(() => {
    function handleFullscreenChange() {
      if (document.fullscreenElement !== shellRef.current) {
        setIsFullscreen(false);
      }
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape" && isFullscreen && !document.fullscreenElement) {
        setIsFullscreen(false);
      }
    }

    document.addEventListener("fullscreenchange", handleFullscreenChange);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("fullscreenchange", handleFullscreenChange);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isFullscreen]);

  async function enterFullscreen() {
    setIsFullscreen(true);
    try {
      await shellRef.current?.requestFullscreen();
    } catch {
      // Keep CSS fullscreen fallback when browser Fullscreen API is unavailable.
    }
  }

  async function exitFullscreen() {
    if (document.fullscreenElement === shellRef.current) {
      await document.exitFullscreen();
    }
    setIsFullscreen(false);
  }

  if (loading) {
    return <div className="timeline-state">Loading timeline</div>;
  }

  if (error) {
    return <div className="timeline-state timeline-error">{error}</div>;
  }

  if (!url) {
    return <div className="timeline-state">Select station</div>;
  }

  return (
    <div ref={shellRef} className={isFullscreen ? "timeline-shell timeline-shell-fullscreen" : "timeline-shell"}>
      <div className="timeline-toolbar">
        <span className="timeline-label">Grafana</span>
        <button
          className="timeline-icon-button"
          type="button"
          onClick={isFullscreen ? exitFullscreen : enterFullscreen}
          aria-label={isFullscreen ? "Return to panel view" : "Open Grafana fullscreen"}
          title={isFullscreen ? "Return to panel view" : "Open Grafana fullscreen"}
        >
          {isFullscreen ? <Minimize2 aria-hidden="true" size={18} /> : <Maximize2 aria-hidden="true" size={18} />}
        </button>
      </div>
      <iframe className="timeline-frame" title="Grafana station timeline" src={url} allowFullScreen />
    </div>
  );
}
