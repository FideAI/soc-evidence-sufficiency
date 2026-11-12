"""Local stand-in for the Messages API: records each request body (never headers) and replies with a
fixed streamed answer. Nothing is forwarded anywhere. Usage: python3 capture_server.py <port> <out.jsonl>"""
import json, sys
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT, OUT = int(sys.argv[1]), sys.argv[2]
ANSWER = json.dumps({"finding": "cannot_determine", "evidence_ids": ["E100"], "explanation": "Capture stub."})


def sse(event, data):
    return f"event: {event}\ndata: {json.dumps(data)}\n\n".encode()


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("content-length", 0)) or 0)
        try:
            parsed = json.loads(body)
        except ValueError:
            parsed = {"unparsed_bytes": len(body)}
        with open(OUT, "a") as f:
            f.write(json.dumps({"path": self.path, "body": parsed}) + "\n")
        if not self.path.startswith("/v1/messages") or "count_tokens" in self.path:
            self.send_response(404); self.end_headers(); return
        model = parsed.get("model", "unknown")
        msg = {"id": "msg_capture", "type": "message", "role": "assistant", "model": model, "content": [],
               "stop_reason": None, "stop_sequence": None, "usage": {"input_tokens": 1, "output_tokens": 1}}
        if not parsed.get("stream"):
            msg.update(content=[{"type": "text", "text": ANSWER}], stop_reason="end_turn")
            data = json.dumps(msg).encode()
            self.send_response(200); self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(data))); self.end_headers(); self.wfile.write(data); return
        self.send_response(200); self.send_header("content-type", "text/event-stream"); self.end_headers()
        for ev, d in [("message_start", {"type": "message_start", "message": msg}),
                      ("content_block_start", {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}}),
                      ("content_block_delta", {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": ANSWER}}),
                      ("content_block_stop", {"type": "content_block_stop", "index": 0}),
                      ("message_delta", {"type": "message_delta", "delta": {"stop_reason": "end_turn", "stop_sequence": None}, "usage": {"output_tokens": 20}}),
                      ("message_stop", {"type": "message_stop"})]:
            self.wfile.write(sse(ev, d)); self.wfile.flush()


HTTPServer(("127.0.0.1", PORT), H).serve_forever()
