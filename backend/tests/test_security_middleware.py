import asyncio
import unittest

from starlette.requests import Request
from starlette.responses import JSONResponse

from app import main


def _request(path: str, headers: dict[str, str] | None = None) -> Request:
    raw = [(key.lower().encode(), value.encode()) for key, value in (headers or {}).items()]
    return Request({"type": "http", "method": "POST", "path": path, "headers": raw, "query_string": b""})


async def _ok(_request):
    return JSONResponse({"ok": True})


class SecurityMiddlewareTests(unittest.TestCase):
    def run_guard(self, request):
        return asyncio.run(main.guard_requests(request, _ok))

    def test_oversized_body_is_rejected_before_the_handler(self):
        response = self.run_guard(_request("/api/ask", {"content-length": str(main.MAX_BODY_BYTES + 1)}))
        self.assertEqual(response.status_code, 413)

    def test_malformed_content_length_is_rejected(self):
        self.assertEqual(self.run_guard(_request("/api/ask", {"content-length": "-5"})).status_code, 413)

    def test_security_headers_and_no_store_on_answers(self):
        response = self.run_guard(_request("/api/ask", {"content-length": "40"}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["x-content-type-options"], "nosniff")
        self.assertEqual(response.headers["x-frame-options"], "DENY")
        self.assertIn("default-src 'none'", response.headers["content-security-policy"])
        self.assertEqual(response.headers["cache-control"], "no-store")

    def test_docs_page_is_exempt_from_the_json_only_csp(self):
        response = self.run_guard(_request("/api/docs"))
        self.assertNotIn("content-security-policy", response.headers)


if __name__ == "__main__":
    unittest.main()
