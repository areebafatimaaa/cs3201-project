"""Client for the Online Image Description System."""
import os
import socket
import sys

HEADER_SIZE = 10
MAX_MESSAGE_BYTES = 5 * 1024 * 1024
MAX_UPLOAD_BYTES = 5 * 1024 * 1024


# ===== Message helpers (same format as the server) =====

def send_message(conn, payload):
    """Send the supplied bytes as one complete message.

    Message format: 10 ASCII length digits (with leading zeros) + data.
    The length counts data bytes only (1..MAX_MESSAGE_BYTES), excluding the header.
    Returns None on successful completion.
    """
    length = len(payload)
    if length < 1 or length > MAX_MESSAGE_BYTES:
        raise ValueError("Message length out of range")
    header = f"{length:010d}".encode("ascii")
    conn.sendall(header + payload)


def recv_exact(conn, count):
    """Read exactly count bytes, or report that the connection closed."""
    data = b""
    while len(data) < count:
        # One recv call may return fewer bytes than requested.
        chunk = conn.recv(count - len(data))
        if chunk == b"":
            if data == b"":
                return None
            raise ConnectionError("Connection closed during a message")
        data += chunk
    return data


def receive_message(sock):
    """Receive one complete message and return its data bytes."""
    # TODO: read the 10-byte header, check it, then read that many bytes
    # If the server closed, raise ConnectionError so main() can exit cleanly
    header = recv_exact(sock, HEADER_SIZE)
    if header is None:
        raise ConnectionError("Server closed the connection")
    if not header.isdigit():
        raise ConnectionError("Invalid message header from server")
    length = int(header)
    if length < 1 or length > MAX_MESSAGE_BYTES:
        raise ConnectionError("Invalid message length from server")
    data = recv_exact(sock, length)
    if data is None:
        raise ConnectionError("Server closed the connection")
    return data

def print_reply(data):
    """Print every line of a text reply with the 'server: ' prefix."""
    # TODO: decode, split into lines, print each with "server: " in front
    text = data.decode("utf-8", errors="replace")
    for line in text.splitlines():
        print(f"server: {line}")

# ===== One function per command =====

def do_upload(sock):
    # TODO: ask for the path, check it locally, send 2 messages, print 1 reply
    pass


def do_download(sock):
    # TODO: ask for the ID and the output path, send, read 1 or 2 messages, save
    pass


def do_simple(sock, text):
    """Send one text command and print the one reply (LIST, unknown commands)."""
    # TODO
    pass


# ===== Main program =====

def main():
    # TODO: read host and port from sys.argv; print usage and exit if wrong

    # TODO: create the socket and connect; print a clean error and exit if it fails

    try:
        while True:
            line = input("client: ").strip()
            if not line:
                continue
            command = line.upper()

            if command == "UPLOAD":
                do_upload(sock)
            elif command == "DOWNLOAD":
                do_download(sock)
            # TODO: DESCRIBE and REMOVE (ask for an ID, then send "DESCRIBE <id>")
            # TODO: QUIT (send, print reply, close socket, break)
            else:
                do_simple(sock, line)
    except (EOFError, KeyboardInterrupt):
        pass
    # TODO: also catch ConnectionError / OSError and print a clean error
    finally:
        sock.close()


if __name__ == "__main__":
    main()

