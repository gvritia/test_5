from concurrent.futures import ThreadPoolExecutor, TimeoutError


def test_connect_to_room_with_valid_username(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        assert websocket.receive_json() == {
            "type": "join",
            "room_id": "python",
            "username": "alice",
        }


def test_send_message_and_receive_response(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        websocket.receive_json()

        websocket.send_json({"type": "message", "text": "Hello"})

        assert websocket.receive_json() == {
            "type": "message",
            "room_id": "python",
            "username": "alice",
            "text": "Hello",
        }


def test_two_clients_in_same_room_receive_same_message(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as alice:
        alice.receive_json()
        with client.websocket_connect("/ws/rooms/python?username=bob") as bob:
            assert alice.receive_json()["username"] == "bob"
            assert bob.receive_json()["username"] == "bob"

            alice.send_json({"type": "message", "text": "Hi Bob"})

            expected = {
                "type": "message",
                "room_id": "python",
                "username": "alice",
                "text": "Hi Bob",
            }
            assert alice.receive_json() == expected
            assert bob.receive_json() == expected


def test_users_from_different_rooms_do_not_receive_foreign_messages(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as alice:
        alice.receive_json()
        with client.websocket_connect("/ws/rooms/go?username=bob") as bob:
            bob.receive_json()

            with ThreadPoolExecutor(max_workers=1) as executor:
                pending_bob_receive = executor.submit(bob.receive_json)

                alice.send_json({"type": "message", "text": "Python only"})
                assert alice.receive_json()["room_id"] == "python"

                try:
                    pending_bob_receive.result(timeout=0.2)
                    assert False, "Bob received a message from another room"
                except TimeoutError:
                    pass

                bob.send_json({"type": "message", "text": "Go only"})
                assert pending_bob_receive.result(timeout=1)["room_id"] == "go"


def test_too_long_message_returns_error(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        websocket.receive_json()

        websocket.send_json({"type": "message", "text": "x" * 301})

        assert websocket.receive_json() == {
            "type": "error",
            "detail": "Message is too long",
        }


def test_disconnected_user_is_removed_from_room_users(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        websocket.receive_json()
        response = client.get("/rooms/python/users")
        assert response.status_code == 200
        assert response.json() == {"room_id": "python", "users": ["alice"]}

    response = client.get("/rooms/python/users")

    assert response.status_code == 200
    assert response.json() == {"room_id": "python", "users": []}
