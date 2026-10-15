"""Exercise HTTPS policy with mocked DNS, sockets, TLS and HTTP responses."""

import tempfile
import unittest
from contextlib import contextmanager
from http.client import HTTPResponse
from io import BytesIO
from pathlib import Path
from queue import Empty
from unittest.mock import Mock, patch

from collection_fixtures import manifest_data
from enterprise_mind.ingestion.collector import (
    CollectionError,
    _PinnedHTTPSConnection,
    collect,
    open_https,
    public_addresses,
)
from enterprise_mind.ingestion.manifest import validate_manifest


class HTTPTransportTests(unittest.TestCase):
    def setUp(self) -> None:
        for function in ("socket.getaddrinfo", "socket.create_connection"):
            guard = patch(function, side_effect=AssertionError("real network forbidden"))
            guard.start()
            self.addCleanup(guard.stop)

    @contextmanager
    def fake_connection(self, response):
        with patch("enterprise_mind.ingestion.collector.public_addresses",
                   return_value=["1.1.1.1"]):
            with patch("enterprise_mind.ingestion.collector._PinnedHTTPSConnection") as factory:
                connection = factory.return_value
                connection.getresponse.return_value = response
                yield connection

    def test_conflicting_duplicate_and_malformed_framing_is_rejected(self) -> None:
        cases = [
            [("Transfer-Encoding", "chunked"), ("Content-Length", "1")],
            [("Transfer-Encoding", "chunked"), ("transfer-encoding", "chunked")],
            [("Content-Length", "1"), ("content-length", "1")],
            [("Content-Length", "1, 1")], [("Content-Length", "-1")],
            [("Content-Length", "1.0")], [("Content-Length", "")],
            [("Content-Length", "\u0661")], [("Content-Length", "9" * 100)],
            [("Content-Length ", "1")], [("Content-Length", "1\r\nInjected: x")],
            [("Transfer-Encoding", "chunked")], [("Transfer-Encoding", "gzip, chunked")],
            [("Transfer-Encoding", "identity")], [("Transfer-Encoding", "")], [],
        ]
        for headers in cases:
            with self.subTest(headers=headers):
                response = Mock(status=200)
                response.getheaders.return_value = headers
                with self.fake_connection(response) as connection:
                    with self.assertRaises(CollectionError):
                        with open_https(manifest_data()["sources"][0]["url"], 10):
                            self.fail("unsafe framing accepted")
                    response.close.assert_called_once()
                    connection.close.assert_called_once()

    def test_valid_content_length_frame_is_read(self) -> None:
        response = Mock(status=200)
        response.getheaders.return_value = [("Content-Length", " 3\t")]
        response.read1.side_effect = [b"abc", b""]
        with self.fake_connection(response):
            with open_https(manifest_data()["sources"][0]["url"], 10) as result:
                self.assertEqual(result.headers["content-length"], "3")
                self.assertEqual(result.read(3), b"abc")
                self.assertEqual(result.read(3), b"")

    def test_http_parser_header_defects_fail_closed(self) -> None:
        # Exercise the standard-library parser without a socket or real network.
        socket = Mock()
        socket.makefile.return_value = BytesIO(
            b"HTTP/1.1 200 OK\r\nContent-Length: 3\r\nMalformed header\r\n\r\nabc"
        )
        response = HTTPResponse(socket)
        response.begin()
        self.assertTrue(response.headers.defects)
        with self.fake_connection(response):
            with self.assertRaisesRegex(CollectionError, "malformed HTTP headers"):
                with open_https(manifest_data()["sources"][0]["url"], 10):
                    self.fail("malformed header accepted")

    def test_truncated_http_body_does_not_publish_a_document(self) -> None:
        socket = Mock()
        socket.makefile.return_value = BytesIO(
            b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 10\r\n\r\nabc"
        )
        response = HTTPResponse(socket)
        response.begin()
        with tempfile.TemporaryDirectory() as folder:
            workspace = Path(folder)
            with self.fake_connection(response):
                with self.assertRaisesRegex(CollectionError, "truncated"):
                    collect(validate_manifest(manifest_data()), ["fictional-hr"],
                            workspace=workspace, transport=open_https, download=True)
            root = workspace / "data/raw"
            self.assertFalse(list(root.glob("blobs/*")))
            self.assertFalse(list(root.glob("records/**/*.json")))
            self.assertFalse(list((root / ".staging").iterdir()))
            self.assertFalse((root / ".collection.lock").exists())

    def test_dns_timeout_is_bounded_before_connection(self) -> None:
        with patch("enterprise_mind.ingestion.collector.Thread") as worker:
            with patch("enterprise_mind.ingestion.collector.Queue") as queue:
                queue.return_value.get.side_effect = Empty
                with self.assertRaisesRegex(CollectionError, "DNS resolution timed out"):
                    public_addresses("documents.example.com", 0.01)
                queue.return_value.get.assert_called_once_with(timeout=0.01)
                self.assertTrue(worker.call_args.kwargs["daemon"])

    def test_mixed_public_and_private_dns_answers_are_rejected(self) -> None:
        for private in ("127.0.0.1", "10.0.0.1", "169.254.169.254", "::1"):
            for addresses in (("1.1.1.1", private), (private, "1.1.1.1")):
                answers = [(2, 1, 6, "", (address, 443)) for address in addresses]
                with self.subTest(addresses=addresses):
                    with patch("socket.getaddrinfo", return_value=answers):
                        with self.assertRaisesRegex(CollectionError, "non-public"):
                            public_addresses("documents.example.com", 1)

    def test_watchdog_interrupts_headers_and_rejects_apparent_success(self) -> None:
        for header_result in ("returns", "raises"):
            response = Mock(status=200)
            response.getheaders.return_value = [("Content-Length", "3")]
            with self.subTest(header_result=header_result):
                with self.fake_connection(response) as connection:
                    with patch("enterprise_mind.ingestion.collector.Timer") as timer:
                        def get_headers():
                            timer.call_args.args[1]()
                            if header_result == "raises":
                                raise OSError("synthetic watchdog interruption")
                            return response

                        connection.getresponse.side_effect = get_headers
                        with self.assertRaisesRegex(CollectionError, "deadline"):
                            with open_https(manifest_data()["sources"][0]["url"], 10):
                                self.fail("expired headers accepted")
                        connection.sock.shutdown.assert_called_once()
                        connection.close.assert_called_once()
                        timer.return_value.cancel.assert_called_once()
                        timer.return_value.join.assert_called_once()

    def test_watchdog_expiration_during_final_body_read_fails(self) -> None:
        for chunk in (b"abc", b""):
            response = Mock(status=200)
            response.getheaders.return_value = [("Content-Length", "3")]
            with self.fake_connection(response):
                with patch("enterprise_mind.ingestion.collector.Timer") as timer:
                    def delayed_read(size):
                        timer.call_args.args[1]()
                        return chunk

                    response.read1.side_effect = delayed_read
                    with self.subTest(chunk=chunk):
                        with self.assertRaisesRegex(CollectionError, "deadline"):
                            with open_https(manifest_data()["sources"][0]["url"], 10) as result:
                                result.read(3)

    def test_connection_uses_pinned_ip_and_original_tls_hostname(self) -> None:
        raw_socket, tls_socket, context = Mock(), Mock(), Mock()
        context.wrap_socket.return_value = tls_socket
        with patch("ssl.create_default_context", return_value=context):
            connection = _PinnedHTTPSConnection("documents.example.com", "1.1.1.1", 10)
            with patch("socket.create_connection", return_value=raw_socket) as connect:
                connection.connect()
        self.assertEqual(connect.call_args.args[0], ("1.1.1.1", 443))
        context.wrap_socket.assert_called_once_with(
            raw_socket, server_hostname="documents.example.com"
        )
        self.assertIs(connection.sock, tls_socket)
        connection.close()

    def test_redirect_is_exposed_without_following_it(self) -> None:
        response = Mock(status=302)
        response.getheaders.return_value = [("Location", "https://127.0.0.1/private")]
        with patch("enterprise_mind.ingestion.collector.public_addresses",
                   return_value=["1.1.1.1"]):
            with patch("enterprise_mind.ingestion.collector._PinnedHTTPSConnection") as factory:
                connection = factory.return_value
                connection.getresponse.return_value = response
                with open_https(manifest_data()["sources"][0]["url"], 10) as result:
                    self.assertEqual(result.status, 302)
                connection.request.assert_called_once()
                self.assertEqual(connection.request.call_args.args, ("GET", "/fictional.txt"))
                self.assertEqual(
                    connection.request.call_args.kwargs["headers"]["Accept-Encoding"], "identity"
                )
                connection.close.assert_called_once()
                response.close.assert_called_once()

    def test_ambiguous_headers_rejected_and_connections_closed(self) -> None:
        response = Mock(status=200)
        response.getheaders.return_value = [("Content-Length", "10"), ("content-length", "20")]
        with patch("enterprise_mind.ingestion.collector.public_addresses",
                   return_value=["1.1.1.1"]):
            with patch("enterprise_mind.ingestion.collector._PinnedHTTPSConnection") as factory:
                connection = factory.return_value
                connection.getresponse.return_value = response
                with self.assertRaises(CollectionError):
                    with open_https(manifest_data()["sources"][0]["url"], 10):
                        self.fail("ambiguous headers were accepted")
                connection.close.assert_called_once()
                response.close.assert_called_once()

    def test_private_dns_failure_occurs_before_connection(self) -> None:
        with patch("enterprise_mind.ingestion.collector.public_addresses",
                   side_effect=CollectionError("non-public destination")):
            with patch("enterprise_mind.ingestion.collector._PinnedHTTPSConnection") as factory:
                with self.assertRaises(CollectionError):
                    with open_https(manifest_data()["sources"][0]["url"], 10):
                        self.fail("private destination was accepted")
                factory.assert_not_called()


if __name__ == "__main__":
    unittest.main()
