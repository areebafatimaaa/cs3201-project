"""Client for the Online Image Description System."""
import os
import socket
import sys

HEADER_SIZE = 10
MAX_MESSAGE_BYTES = 5 * 1024 * 1024
MAX_UPLOAD_BYTES = 5 * 1024 * 1024



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
        chunk = conn.recv(count - len(data))
        if chunk == b"":
            if data == b"":
                return None
            raise ConnectionError("Connection closed during a message")
        data += chunk
    return data


def receive_message(sock):
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
    text = data.decode("utf-8", errors="replace")
    for line in text.splitlines():
        print(f"server: {line}")


# def do_upload(sock):
    # path = input("client: ").split()
    # if not os.path.isfile(path):
    #     print("client: ERROR - File not found")
    #     return
    # size = os.path.getsize(path)
    # if size == 0 or size > MAX_UPLOAD_BYTES:
    #     print("client: ERROR - File must be between 1 byte and 5 MiB")
    #     return
    # try:
    #     with open(path, "rb") as f:
    #         data = f.read()
    # except OSError:
    #     print("client: ERROR - Cannot read file")
    #     return
    #  if not os.path.isfile(path):
    #     print("client: ERROR - File not found")
    #     return
    # size = os.path.getsize(path)
    # if size == 0 or size > MAX_UPLOAD_BYTES:
    #     print("client: ERROR - File must be between 1 byte and 5 MiB")
    #     return
    # try:
    #     with open(path, "rb") as f:
    # filename = os.path.basename(path)
    # if len(filename) > 255:
    #     print("client: ERROR - Filename too long")
    #     return
    # command = f"UPLOAD {filename}".encode("utf-8")
    # if len(command) > 1024:
    #     print("client: ERROR - Invalid command length")
    #     return
    # send_message(sock, command)
    # send_message(sock, data)
    # print_reply(receive_message(sock))
def do_upload(sock):
    path = input("client: ").strip()
    if not os.path.isfile(path):
        print("client: ERROR - File not found")
        return
    size = os.path.getsize(path)
    if size == 0 or size > MAX_UPLOAD_BYTES:
        print("client: ERROR - File must be between 1 byte and 5 MiB")
        return
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError:
        print("client: ERROR - Cannot read file")
        return

    filename = os.path.basename(path)
    if len(filename) > 255:
        print("client: ERROR - Filename too long")
        return
    command = f"UPLOAD {filename}".encode("utf-8")
    if len(command) > 1024:
        print("client: ERROR - Invalid command length")
        return
    send_message(sock, command)
    send_message(sock, data)
    print_reply(receive_message(sock))


# def do_download(sock):
#     image_id = input("client: ").split()
#     out_path = input("client: ").split()


#     if os.path.exists(out_path):
#         print("client: ERROR - Output file already exists")
#         return

#     command = f"DOWNLOAD {image_id}".encode("utf-8")
#     if len(command) > 1024:
#         print("client: ERROR - Invalid command length")
#         return
#     send_message(sock, command)

#     reply = receive_message(sock)
#     print_reply(reply)
#     if not reply.decode("utf-8", errors="replace").startswith("OK"):
#         return  

#     image_bytes = receive_message(sock)  
#     try:
#         with open(out_path, "xb") as f:  
#             f.write(image_bytes)
#     except OSError:
#         print("client: ERROR - Cannot save file")
#         return
#     print(f"client: Saved to {out_path}")
def do_download(sock):
    image_id = input("client: ").strip()
    out_path = input("client: ").strip()

    if os.path.exists(out_path):
        print("client: ERROR - Output file already exists")
        return

    command = f"DOWNLOAD {image_id}".encode("utf-8")
    if len(command) > 1024:
        print("client: ERROR - Invalid command length")
        return
    send_message(sock, command)

    reply = receive_message(sock)
    print_reply(reply)
    if not reply.startswith(b"OK"):
        return  # error reply: no image message follows

    image_bytes = receive_message(sock)
    try:
        with open(out_path, "xb") as f:
            f.write(image_bytes)
    except FileExistsError:
        print("client: ERROR - Output file already exists")
        return
    except OSError:
        print("client: ERROR - Cannot save file")
        return
    print(f"client: Saved to {out_path}")

def do_simple(sock, text):
    """Send one text command and print the one reply (LIST, unknown commands)."""
    data = text.encode("utf-8")
    if len(data) == 0 or len(data) > 1024:
        print("client: ERROR - Invalid command length")
        return
    send_message(sock, data)
    print_reply(receive_message(sock))




#main part of the pogram

def main():
    if len(sys.argv) != 3:
        print("Usage: python ImageDescriptionClient.py <server_ip> <port>")
        sys.exit(1)
    host = sys.argv[1]
    try:
        port = int(sys.argv[2])
    except ValueError:
        print("client: ERROR - Port must be a number")
        sys.exit(1)

    try:
        sock= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
    except OSError as error:
        print(f"client: ERROR - {error}")
        sock.close()
        sys.exit(1)

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
            elif command in ("DESCRIBE", "REMOVE"):
                image_id = input("client: ").strip()
                text_command = command + " " + image_id 
                do_simple(sock, text_command)
            elif command == "QUIT":
                do_simple(sock, line)
                break
            else:
                do_simple(sock, line)
    except (EOFError, KeyboardInterrupt):
        pass
    except (ConnectionError, OSError, ValueError) as error:
        print(f"client: ERROR - {error}")
    finally:
        sock.close()



if __name__ == "__main__":
    main()


