import logging

from app.logger import Logger


def test_setup_writes_records_to_the_log_file(config):
    Logger.setup(config)
    Logger.get("test").warning("something happened")
    for handler in logging.getLogger().handlers:
        handler.flush()
    text = config.log_file.read_text()
    assert "WARNING - test - something happened" in text


def test_setup_replaces_earlier_handlers(config):
    Logger.setup(config)
    Logger.setup(config)
    assert len(logging.getLogger().handlers) == 1
