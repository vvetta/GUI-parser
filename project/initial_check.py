import socket


def _ethernet_checker() -> bool:
    """Проверяет наличие интернет соединения"""

    try:
        socket.create_connection(("www.google.com", 80))
        # Тут будет лог о том, что интернет соединение есть!
        return True

    except OSError:
        # Тут будет лог о том, что интернет соединения нет!
        return False



if __name__ == "__main__":
    _ethernet_checker()
