"""Exercise the real SMTP transport against a disposable loopback server."""
import socketserver
import threading
from email import policy
from email.parser import BytesParser
from sqlalchemy import select
from app.models import Notification
from app.notifications import deliver_pending
from test_public import send


def test_real_smtp_delivery(setup, payload):
    received = []
    class SMTPHandler(socketserver.StreamRequestHandler):
        def handle(self):
            self.wfile.write(b"220 localhost test SMTP\r\n")
            while line := self.rfile.readline():
                verb = line.split(b" ", 1)[0].strip().upper()
                if verb == b"DATA":
                    self.wfile.write(b"354 Send message\r\n")
                    lines = []
                    while (line := self.rfile.readline()) != b".\r\n":
                        if not line:
                            return
                        lines.append(line[1:] if line.startswith(b"..") else line)
                    received.append(b"".join(lines))
                    self.wfile.write(b"250 Accepted\r\n")
                elif verb == b"QUIT":
                    self.wfile.write(b"221 Bye\r\n")
                    return
                else:
                    self.wfile.write(b"250 OK\r\n")
    client, sessions, settings = setup
    settings.smtp_host = "127.0.0.1"
    settings.smtp_starttls = False
    settings.smtp_from = "site@example.org"
    settings.notification_to = "manager@example.org"
    with socketserver.TCPServer(("127.0.0.1", 0), SMTPHandler) as server:
        settings.smtp_port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            identifier = send(client, payload).json()["id"]
            deliver_pending(sessions, settings)
        finally:
            server.shutdown()
            thread.join()
    assert len(received) == 1
    message = BytesParser(policy=policy.default).parsebytes(received[0])
    assert message["To"] == "manager@example.org"
    assert identifier in message["Subject"]
    assert payload["message"] in message.get_content()
    assert message.get_content_type() == "text/plain"
    with sessions() as db:
        assert db.scalar(select(Notification)).sent_at is not None
