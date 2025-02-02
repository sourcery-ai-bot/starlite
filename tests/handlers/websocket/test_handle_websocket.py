from typing import List

from starlite import Controller, Router, WebSocket, websocket
from starlite.testing import create_test_client


def test_handle_websocket() -> None:
    @websocket(path="/")
    async def simple_websocket_handler(socket: WebSocket) -> None:
        await socket.accept()
        data = await socket.receive_json()
        assert data
        await socket.send_json({"data": "123"})
        await socket.close()

    client = create_test_client(route_handlers=simple_websocket_handler)

    with client.websocket_connect("/") as ws:
        ws.send_json({"data": "123"})
        data = ws.receive_json()
        assert data


def test_websocket_signature_namespace() -> None:
    class MyController(Controller):
        path = "/ws"
        signature_namespace = {"c": float}

        @websocket(path="/", signature_namespace={"d": List[str]})
        async def simple_websocket_handler(
            self, socket: WebSocket, a: "a", b: "b", c: "c", d: "d"  # type:ignore[name-defined]  # noqa: F821
        ) -> None:
            await socket.accept()
            data = await socket.receive_json()
            assert data
            await socket.send_json({"a": a, "b": b, "c": c, "d": d})
            await socket.close()

    router = Router("/", route_handlers=[MyController], signature_namespace={"b": str})

    client = create_test_client(route_handlers=[router], signature_namespace={"a": int})

    with client.websocket_connect("/ws?a=1&b=two&c=3.0&d=d") as ws:
        ws.send_json({"data": "123"})
        data = ws.receive_json()
        assert data == {"a": 1, "b": "two", "c": 3.0, "d": ["d"]}
