import logging


def setup_logger():
    logging.basicConfig(
        filename="trades.log",
        level=logging.INFO,
        format="%(asctime)s %(message)s"
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger("").addHandler(console)
