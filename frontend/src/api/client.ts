const BASE = "http://localhost:3401/api";
const WS_URL = "ws://localhost:3401/ws";

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, init);
  if (!res.ok) throw new Error(`API ${path}: ${res.status}`);
  return res.json() as Promise<T>;
}

type WsListener = (msg: unknown) => void;

let socket: WebSocket | null = null;
const listeners: WsListener[] = [];

export function connectWs(): void {
  if (socket) return;
  socket = new WebSocket(WS_URL);
  socket.onmessage = (e) => {
    const msg = JSON.parse(e.data as string) as unknown;
    listeners.forEach((fn) => fn(msg));
  };
  socket.onclose = () => {
    socket = null;
    setTimeout(connectWs, 2000);
  };
}

export function addWsListener(fn: WsListener): () => void {
  listeners.push(fn);
  return () => {
    const idx = listeners.indexOf(fn);
    if (idx >= 0) listeners.splice(idx, 1);
  };
}
