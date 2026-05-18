import { useEffect, useState } from "preact/hooks";
import type { SessionState } from "./types/session";
import { EMPTY_SESSION } from "./types/session";
import { connectWs, addWsListener } from "./api/client";

type WsMessage =
  | { type: "session_update"; data: SessionState }
  | { type: "render_status"; data: Record<string, unknown> };

export function App() {
  const [session, setSession] = useState<SessionState>(EMPTY_SESSION);

  useEffect(() => {
    connectWs();
    return addWsListener((msg) => {
      const m = msg as WsMessage;
      if (m.type === "session_update") setSession(m.data);
    });
  }, []);

  return (
    <div class="app">
      <header class="app-header">
        <span>{session.current_canvas ?? "AI Light Show"}</span>
      </header>
      <main class="app-main">
        <p>Song: {session.current_song?.song_id ?? "none"}</p>
      </main>
    </div>
  );
}
