import { FitAddon } from "@xterm/addon-fit";
import { Terminal } from "@xterm/xterm";
import { forwardRef, useEffect, useImperativeHandle, useRef, useState } from "react";
import { terminalUrl } from "../api";
import { useTextSizes } from "../textSize";
import { TERMINAL_THEMES, useTheme } from "../theme";

interface Props {
  labId: string;
  enabled: boolean; // false while the machine is stopped
  connectKey: number; // bump to force a fresh connection (e.g. after reset)
  onConnected: () => void;
}

type ConnState = "connecting" | "connected" | "disconnected";

export interface TerminalHandle {
  /** Type text at the prompt without pressing Enter (the learner stays in control). */
  paste: (text: string) => boolean;
}

const TerminalPane = forwardRef<TerminalHandle, Props>(function TerminalPane({ labId, enabled, connectKey, onConnected }, ref) {
  const { theme } = useTheme();
  const fontSize = Math.round((14 * useTextSizes().terminal) / 100);
  const fontSizeRef = useRef(fontSize);
  fontSizeRef.current = fontSize;
  const hostRef = useRef<HTMLDivElement>(null);
  const termRef = useRef<Terminal | null>(null);
  const fitRef = useRef<FitAddon | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const [state, setState] = useState<ConnState>("connecting");
  const [manualKey, setManualKey] = useState(0);
  const onConnectedRef = useRef(onConnected);
  onConnectedRef.current = onConnected;

  useImperativeHandle(ref, () => ({
    paste(text: string) {
      const term = termRef.current;
      if (!term || wsRef.current?.readyState !== WebSocket.OPEN) return false;
      // xterm wraps this in bracketed paste, so even a multi-line command waits for Enter.
      term.paste(text.replace(/\n+$/, ""));
      term.focus();
      return true;
    },
  }));

  // A new text size from the Aa menu: resize the font, then refit (which tells the shell its new size).
  useEffect(() => {
    const term = termRef.current;
    if (!term || term.options.fontSize === fontSize) return;
    term.options.fontSize = fontSize;
    try {
      fitRef.current?.fit();
    } catch {
      return;
    }
    const ws = wsRef.current;
    if (ws?.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ type: "resize", cols: term.cols, rows: term.rows }));
  }, [fontSize]);

  // Create the xterm instance once.
  useEffect(() => {
    const term = new Terminal({
      cursorBlink: true,
      fontFamily: '"JetBrains Mono", ui-monospace, Menlo, monospace',
      fontSize: fontSizeRef.current,
      theme: TERMINAL_THEMES[theme],
      scrollback: 5000,
    });
    const fit = new FitAddon();
    term.loadAddon(fit);
    term.open(hostRef.current!);
    termRef.current = term;
    fitRef.current = fit;
    // The bundled font may finish loading after xterm measured its cells: measure again.
    document.fonts?.ready.then(() => {
      if (termRef.current !== term) return;
      term.options.fontFamily = '"JetBrains Mono", monospace'; // a changed value makes xterm re-measure
      fit.fit();
    });

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
    // Created once on purpose; theme changes are applied by the next effect.
  }, []);

  useEffect(() => {
    if (termRef.current) termRef.current.options.theme = TERMINAL_THEMES[theme];
  }, [theme]);

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
          // Every connection is a brand new shell. Clear what the previous one left on screen,
          // otherwise its last prompt stays there and the new prompt lands next to it.
          term.reset();
          setState("connected");
          retried = false;
          onConnectedRef.current();
          // No auto focus: the lesson keeps the keyboard (arrow keys move between steps).
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
      <div className="terminal-body">
        {state === "connecting" && enabled && <span className="terminal-connecting muted small">Connecting...</span>}
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
});

export default TerminalPane;
