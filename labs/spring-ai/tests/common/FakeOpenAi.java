package com.atlas.check;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.function.Function;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

/** A fake OpenAI-compatible server for checks: records every request, answers from a script. No network, no model. */
public final class FakeOpenAi {
    /** What the fake model says: plain text, or a request to call one tool with JSON arguments. */
    public record Reply(String text, String toolName, String toolArgs) {
        public static Reply text(String text) { return new Reply(text, null, null); }
        public static Reply tool(String name, String args) { return new Reply(null, name, args); }
    }

    public final List<String> chatRequests = new CopyOnWriteArrayList<>();
    public final List<String> embeddingRequests = new CopyOnWriteArrayList<>();
    public volatile Function<String, Reply> script = body -> Reply.text("Hello from the fake model.");
    private final HttpServer server;

    public FakeOpenAi() {
        try {
            server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        } catch (IOException e) {
            throw new IllegalStateException(e);
        }
        server.createContext("/", this::handle);
        server.setExecutor(java.util.concurrent.Executors.newCachedThreadPool());
        server.start();
    }


    private static final JsonMapper JSON = JsonMapper.builder().build();

    /** Forget every recorded request (each check starts clean). */
    public void reset() {
        chatRequests.clear();
        embeddingRequests.clear();
        script = body -> Reply.text("Hello from the fake model.");
    }

    /** The i-th chat request as JSON (negative counts from the end: -1 is the last). */
    public JsonNode chat(int i) {
        int n = chatRequests.size();
        if (n == 0) throw new IllegalStateException("the app never called the model");
        return JSON.readTree(chatRequests.get(i < 0 ? n + i : i));
    }

    /** The text of every message with this role in a request, in order. */
    public static List<String> texts(JsonNode request, String role) {
        List<String> out = new java.util.ArrayList<>();
        for (JsonNode m : request.path("messages")) {
            if (role.equals(m.path("role").asString())) out.add(m.path("content").asString(""));
        }
        return out;
    }

    /** The names of the tools a request offered the model. */
    public static List<String> tools(JsonNode request) {
        List<String> out = new java.util.ArrayList<>();
        for (JsonNode t : request.path("tools")) out.add(t.path("function").path("name").asString());
        return out;
    }

    public String baseUrl() { return "http://127.0.0.1:" + server.getAddress().getPort() + "/v1"; }
    public void stop() { server.stop(0); }
    public String lastChat() { return chatRequests.isEmpty() ? "" : chatRequests.get(chatRequests.size() - 1); }

    private void handle(HttpExchange ex) throws IOException {
        String body = new String(ex.getRequestBody().readAllBytes(), StandardCharsets.UTF_8);
        String path = ex.getRequestURI().getPath();
        if (path.endsWith("/embeddings")) {
            embeddingRequests.add(body);
            send(ex, 200, "application/json", embeddings(body));
            return;
        }
        if (!path.endsWith("/chat/completions")) {
            send(ex, 404, "application/json", "{\"error\":{\"message\":\"no such path " + esc(path) + "\"}}");
            return;
        }
        chatRequests.add(body);
        Reply r = script.apply(body);
        boolean stream = body.replace(" ", "").contains("\"stream\":true");
        if (stream) {
            ex.getResponseHeaders().add("Content-Type", "text/event-stream");
            ex.sendResponseHeaders(200, 0);
            try (OutputStream out = ex.getResponseBody()) {
                String[] words = r.text().split("(?<= )");
                for (String w : words) {
                    out.write(("data: {\"id\":\"c1\",\"object\":\"chat.completion.chunk\",\"created\":1,\"model\":\"ai-chat\",\"choices\":[{\"index\":0,\"delta\":{\"content\":\"" + esc(w) + "\"},\"finish_reason\":null}]}\n\n").getBytes(StandardCharsets.UTF_8));
                    out.flush();
                }
                out.write("data: {\"id\":\"c1\",\"object\":\"chat.completion.chunk\",\"created\":1,\"model\":\"ai-chat\",\"choices\":[{\"index\":0,\"delta\":{},\"finish_reason\":\"stop\"}]}\n\ndata: [DONE]\n\n".getBytes(StandardCharsets.UTF_8));
            }
            return;
        }
        String message = r.toolName() == null
                ? "{\"role\":\"assistant\",\"content\":\"" + esc(r.text()) + "\"}"
                : "{\"role\":\"assistant\",\"content\":null,\"tool_calls\":[{\"id\":\"call_1\",\"type\":\"function\",\"function\":{\"name\":\"" + r.toolName() + "\",\"arguments\":\"" + esc(r.toolArgs()) + "\"}}]}";
        String finish = r.toolName() == null ? "stop" : "tool_calls";
        send(ex, 200, "application/json", "{\"id\":\"c1\",\"object\":\"chat.completion\",\"created\":1,\"model\":\"ai-chat\",\"choices\":[{\"index\":0,\"message\":" + message
                + ",\"finish_reason\":\"" + finish + "\"}],\"usage\":{\"prompt_tokens\":42,\"completion_tokens\":8,\"total_tokens\":50}}");
    }

    /** A tiny, predictable embedding: 8 numbers counting a few keywords, so similar texts get similar vectors. */
    static final String[] WORDS = {"pendulum", "planetarium", "show", "gallery", "dinosaur", "robot", "ticket", "hours"};

    private static String embeddings(String body) {
        java.util.regex.Matcher m = java.util.regex.Pattern.compile("\"input\"\\s*:\\s*\\[(.*?)\\]", java.util.regex.Pattern.DOTALL).matcher(body);
        List<String> inputs = new java.util.ArrayList<>();
        if (m.find()) {
            java.util.regex.Matcher s = java.util.regex.Pattern.compile("\"((?:[^\"\\\\]|\\\\.)*)\"").matcher(m.group(1));
            while (s.find()) inputs.add(s.group(1));
        } else {
            java.util.regex.Matcher one = java.util.regex.Pattern.compile("\"input\"\\s*:\\s*\"((?:[^\"\\\\]|\\\\.)*)\"").matcher(body);
            if (one.find()) inputs.add(one.group(1));
        }
        StringBuilder data = new StringBuilder();
        for (int i = 0; i < inputs.size(); i++) {
            String t = inputs.get(i).toLowerCase();
            double[] v = new double[WORDS.length];
            double norm = 0;
            for (int k = 0; k < WORDS.length; k++) {
                v[k] = t.contains(WORDS[k]) ? 1 : 0.01;
                norm += v[k] * v[k];
            }
            StringBuilder vec = new StringBuilder();
            for (int k = 0; k < v.length; k++) vec.append(k == 0 ? "" : ",").append(v[k] / Math.sqrt(norm));
            data.append(i == 0 ? "" : ",").append("{\"object\":\"embedding\",\"index\":").append(i).append(",\"embedding\":[").append(vec).append("]}");
        }
        return "{\"object\":\"list\",\"data\":[" + data + "],\"model\":\"ai-embed\",\"usage\":{\"prompt_tokens\":3,\"total_tokens\":3}}";
    }

    private static void send(HttpExchange ex, int code, String type, String body) throws IOException {
        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        ex.getResponseHeaders().add("Content-Type", type);
        ex.sendResponseHeaders(code, bytes.length);
        try (OutputStream out = ex.getResponseBody()) {
            out.write(bytes);
        }
    }

    static String esc(String s) {
        if (s == null) return "";
        return s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n");
    }
}
