#!/usr/bin/env python3
# Local HTTPS server for the Miseda site/portal, with security headers.
import os, ssl, sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = "/root/miseda/portal"
TLS = os.path.join(ROOT, "tls")

class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)
    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        self.send_header("Content-Security-Policy",
            "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; img-src 'self' data:; base-uri 'self'; form-action 'self'")
        super().end_headers()
    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8443
    bind = sys.argv[2] if len(sys.argv) > 2 else "0.0.0.0"
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.load_cert_chain(os.path.join(TLS, "cert.pem"), os.path.join(TLS, "key.pem"))
    srv = ThreadingHTTPServer((bind, port), H)
    srv.socket = ctx.wrap_socket(srv.socket, server_side=True)
    print("HTTPS pe %s:%d (TLS1.2+)" % (bind, port), flush=True)
    srv.serve_forever()

if __name__ == "__main__":
    main()
