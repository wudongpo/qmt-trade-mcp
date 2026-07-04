"""日志配置：控制台 + 按日切割的文件日志。"""
from __future__ import annotations

from pathlib import Path


def make_log_config(log_dir: str, log_level: str = "INFO") -> dict:
    """生成 uvicorn 可用的 log_config 字典。

    Args:
        log_dir: 日志目录路径。
        log_level: 日志级别（DEBUG/INFO/WARNING/ERROR）。
    """
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    return {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "default": {
                "format": "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "filename": str(log_path / "mcp.log"),
                "when": "midnight",
                "interval": 1,
                "backupCount": 30,
                "encoding": "utf-8",
                "formatter": "default",
            },
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["file", "console"],
                "level": log_level,
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["file", "console"],
                "level": log_level,
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["file", "console"],
                "level": log_level,
                "propagate": False,
            },
        },
        "root": {"handlers": ["file", "console"], "level": log_level},
    }
