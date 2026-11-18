import { FitAddon } from "@xterm/addon-fit";
import { Terminal } from "@xterm/xterm";
import { useEffect, useRef, useState } from "react";
import { terminalUrl } from "../api";

interface Props {
  labId: string;
  enabled: boolean; // false while the machine is stopped
  connectKey: number; // bump to force a fresh connection (e.g. after reset)
  onConnected: () => void;
}

type ConnState = "connecting" | "connected" | "disconnected";

export default function TerminalPane({ labId, enabled, connectKey, onConnected }: Props) {
  const hostRef = useRef<HTMLDivElement>(null);
  const termRef = useRef<Terminal | null>(null);
  const fitRef = useRef<FitAddon | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const [state, setState] = useState<ConnState>("connecting");
  const [manualKey, setManualKey] = useState(0);
  const onConnectedRef = useRef(onConnected);
  onConnectedRef.current = onConnected;

  // Create the xterm instance once.
  useEffect(() => {
    const term = new Terminal({
      cursorBlink: true,
      fontFamily: "JetBrains Mono, Menlo, monospace",
      fontSize: 14,
      theme: { background: "#0d1117", foreground: "#e6edf3", cursor: "#e6edf3" },
      scrollback: 5000,
    });
    const fit = new FitAddon();
    term.loadAddon(fit);
    term.open(hostRef.current!);
    termRef.current = term;
    fitRef.current = fit;

    const sendResize = () => {
      try {
        fit.fit();
      } catch {
        return; // hidden or zero size
      }
      const ws = wsRef.current;
      if (ws?.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ type: "resize", cols: term.cols, rows: term.rows }));
    };
    let frame = 0;
    const observer = new ResizeObserver(() => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(sendResize);
    });
    observer.observe(hostRef.current!);
    const input = term.onData((data) => {
      const ws = wsRef.current;
      if (ws?.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ type: "input", data }));
    });

    return () => {
      observer.disconnect();
      cancelAnimationFrame(frame);
      input.dispose();
      term.dispose();
      termRef.current = null;
    };
  }, []);

  // (Re)connect the WebSocket.
  useEffect(() => {
    const term = termRef.current;
    if (!term || !enabled) {
      setState("disconnected");
      return;
    }
    let disposed = false;
    let retried = false;
    let retryTimer = 0;
    let pingTimer = 0;

    const connect = () => {
      setState("connecting");
      let shellExited = false;
      const ws = new WebSocket(terminalUrl(labId));
      ws.binaryType = "arraybuffer";
      wsRef.current = ws;

      ws.onopen = () => {
        fitRef.current?.fit();
        ws.send(JSON.stringify({ type: "resize", cols: term.cols, rows: term.rows }));
        pingTimer = window.setInterval(() => ws.readyState === WebSocket.OPEN && ws.send('{"type":"ping"}'), 25000);
      };
      ws.onmessage = (ev) => {
        if (ev.data instanceof ArrayBuffer) {
          term.write(new Uint8Array(ev.data));
          return;
        }
        const msg = JSON.parse(ev.data);
        if (msg.type === "status" && msg.message === "connected") {
          setState("connected");
          retried = false;
          onConnectedRef.current();
          term.focus();
        } else if (msg.type === "exit") {
          shellExited = true;
        } else if (msg.type === "error") {
          term.writeln(`\r\n\x1b[31m${msg.message}\x1b[0m`);
          shellExited = true;
        }
      };
      ws.onclose = () => {
        window.clearInterval(pingTimer);
        if (disposed) return;
        setState("disconnected");
        // A dropped connection gets one automatic retry; a shell that exited (or a stopped machine) does not.
        if (!shellExited && !retried) {
          retried = true;
          retryTimer = window.setTimeout(connect, 2000);
        }
      };
    };
    connect();

    return () => {
      disposed = true;
      window.clearTimeout(retryTimer);
      window.clearInterval(pingTimer);
      wsRef.current?.close();
      wsRef.current = null;
    };
  }, [labId, enabled, connectKey, manualKey]);

  return (
    <div className="terminal-pane">
      <div className="pane-header">
        <span>Terminal</span>
        <span className="spacer" />
        {state === "connecting" && <span className="muted small">Connecting...</span>}
      </div>
      <div className="terminal-body">
        <div ref={hostRef} className="terminal-host" />
        {state === "disconnected" && (
          <div className="terminal-overlay">
            {enabled ? (
              <>
                Disconnected.{" "}
                <button className="btn btn-small" onClick={() => setManualKey((k) => k + 1)}>Reconnect</button>
              </>
            ) : (
              "Machine is stopped. Start it to use the terminal."
            )}
          </div>
        )}
      </div>
    </div>
  );
}
