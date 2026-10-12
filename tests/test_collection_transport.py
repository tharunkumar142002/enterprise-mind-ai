"""Exercise HTTPS policy with mocked DNS, sockets, TLS and HTTP responses."""

import unittest
from unittest.mock import Mock, patch

from collection_fixtures import manifest_data
from enterprise_mind.ingestion.collector import (
    CollectionError,
    _PinnedHTTPSConnection,
    open_https,
)


class HTTPTransportTests(unittest.TestCase):
    def setUp(self) -> None:
        for function in ("socket.getaddrinfo", "socket.create_connection"):
            guard = patch(function, side_effect=AssertionError("real network forbidden"))
            guard.start()
            self.addCleanup(guard.stop)

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
