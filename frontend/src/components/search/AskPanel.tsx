import { useEffect, useState } from "react";
import type { FormEvent } from "react";

import { postJson } from "../../lib/api";
import type { AskResponse, Station } from "../../types";

const ASK_RESULT_LIMIT = 3;

type Props = {
  initialMessage?: string;
  initialResults?: Station[];
  onApplyResults: (stations: Station[]) => void;
  onSelectResult: (station: Station) => void;
  onClearResults: () => void;
  selectedStationId?: string | null;
};

export function AskPanel({
  initialMessage = "",
  initialResults = [],
  onApplyResults,
  onSelectResult,
  onClearResults,
  selectedStationId = null
}: Props) {
  const [message, setMessage] = useState("");
  const [results, setResults] = useState<Station[]>([]);
  const [showingInitialExample, setShowingInitialExample] = useState(false);
  const [userInteracted, setUserInteracted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (userInteracted || initialResults.length === 0) {
      return;
    }

    setMessage(initialMessage);
    setResults(initialResults.slice(0, ASK_RESULT_LIMIT));
    setShowingInitialExample(initialMessage.length > 0);
  }, [initialMessage, initialResults, userInteracted]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = message.trim();
    if (!trimmed) {
      return;
    }

    setLoading(true);
    setUserInteracted(true);
    setShowingInitialExample(false);
    setError(null);
    try {
      const response = await postJson<AskResponse>("/api/search/ask?profile=seoul-gyeonggi&limit=3", {
        message: trimmed
      });
      const limitedResults = response.results.slice(0, ASK_RESULT_LIMIT);
      setResults(limitedResults);
      onApplyResults(limitedResults);
    } catch (requestError) {
      setResults([]);
      setError(requestError instanceof Error ? requestError.message : "Ask request failed");
    } finally {
      setLoading(false);
    }
  }

  function handleClear() {
    setMessage("");
    setResults([]);
    setError(null);
    setUserInteracted(true);
    setShowingInitialExample(false);
    onClearResults();
  }

  function handleInputFocus() {
    if (!showingInitialExample) {
      return;
    }

    setMessage("");
    setUserInteracted(true);
    setShowingInitialExample(false);
  }

  return (
    <section className="assistant-panel" aria-label="Ask station search">
      <div className="assistant-heading">
        <div>
          <p className="eyebrow">Ask</p>
          <h2>Station search</h2>
        </div>
        <button type="button" onClick={handleClear}>
          Clear
        </button>
      </div>

      <form className="assistant-chat-form" onSubmit={handleSubmit}>
        <label>
          <span>Query</span>
          <input
            value={message}
            onFocus={handleInputFocus}
            onChange={(event) => {
              setMessage(event.target.value);
              setUserInteracted(true);
              setShowingInitialExample(false);
            }}
            placeholder="ST-0001, Seoul, fast chargers"
          />
        </label>
        <button type="submit" disabled={loading}>
          Ask
        </button>
      </form>

      {error ? <p className="assistant-message">{error}</p> : null}

      {results.length > 0 ? (
        <div className="assistant-results">
          <ol>
            {results.map((station) => (
              <li
                className={station.station_id === selectedStationId ? "assistant-result-item-selected" : undefined}
                key={station.station_id}
              >
                <button
                  aria-pressed={station.station_id === selectedStationId}
                  className="assistant-result-button"
                  type="button"
                  onClick={() => onSelectResult(station)}
                >
                  <strong>{station.name}</strong>
                  <span>
                    {station.station_id} / {station.region} / {station.connector_count} connectors
                  </span>
                </button>
              </li>
            ))}
          </ol>
        </div>
      ) : null}
    </section>
  );
}
