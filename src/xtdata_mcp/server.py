from __future__ import annotations

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from fastmcp import FastMCP

mcp = FastMCP("XtQuant.XtData MCP")


def _xtdata():
    """
    延迟导入 xtquant.xtdata，避免在未安装 xtquant 的环境下启动即崩溃。
    """
    try:
        from xtquant import xtdata  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "无法导入 xtquant.xtdata。请先安装并配置 QMT/xtquant 运行环境。"
        ) from exc
    return xtdata


def _ok(data: Any) -> dict[str, Any]:
    return {"ok": True, "data": data}


def _err(message: str) -> dict[str, Any]:
    return {"ok": False, "error": message}


def _run(callable_obj, *args, **kwargs) -> dict[str, Any]:
    try:
        result = callable_obj(*args, **kwargs)
        return _ok(result)
    except Exception as exc:  # pragma: no cover
        return _err(f"{type(exc).__name__}: {exc}")


@mcp.tool()
def reconnect(ip: str = "", port: int = 0) -> dict[str, Any]:
    """
    连接或重连 xtdata 服务端。
    """
    xtdata = _xtdata()
    return _run(xtdata.reconnect, ip, port)


@mcp.tool()
def subscribe_quote(
    stock_code: str,
    period: str = "1d",
    start_time: str = "",
    end_time: str = "",
    count: int = 0,
) -> dict[str, Any]:
    """
    订阅单股行情。返回订阅号 seq。
    注意：MCP 无法直接传 Python 回调，此接口只创建订阅。
    """
    xtdata = _xtdata()
    return _run(
        xtdata.subscribe_quote,
        stock_code,
        period,
        start_time,
        end_time,
        count,
        None,
    )


@mcp.tool()
def subscribe_whole_quote(code_list: list[str]) -> dict[str, Any]:
    """
    订阅全推行情。返回订阅号 seq。
    """
    xtdata = _xtdata()
    return _run(xtdata.subscribe_whole_quote, code_list, None)


@mcp.tool()
def unsubscribe_quote(seq: int) -> dict[str, Any]:
    """
    反订阅行情。
    """
    xtdata = _xtdata()
    return _run(xtdata.unsubscribe_quote, seq)


@mcp.tool()
def get_full_tick(code_list: list[str]) -> dict[str, Any]:
    """
    获取全推切面数据。
    """
    xtdata = _xtdata()
    return _run(xtdata.get_full_tick, code_list)


@mcp.tool()
def get_market_data(
    field_list: list[str] | None = None,
    stock_list: list[str] | None = None,
    period: str = "1d",
    start_time: str = "",
    end_time: str = "",
    count: int = -1,
    dividend_type: str = "none",
    fill_data: bool = True,
) -> dict[str, Any]:
    """
    从缓存获取行情数据。
    """
    xtdata = _xtdata()
    return _run(
        xtdata.get_market_data,
        field_list or [],
        stock_list or [],
        period,
        start_time,
        end_time,
        count,
        dividend_type,
        fill_data,
    )


@mcp.tool()
def get_local_data(
    field_list: list[str] | None = None,
    stock_list: list[str] | None = None,
    period: str = "1d",
    start_time: str = "",
    end_time: str = "",
    count: int = -1,
    dividend_type: str = "none",
    fill_data: bool = True,
    data_dir: str = "",
) -> dict[str, Any]:
    """
    从本地文件读取行情数据。
    """
    xtdata = _xtdata()
    kwargs = {
        "field_list": field_list or [],
        "stock_list": stock_list or [],
        "period": period,
        "start_time": start_time,
        "end_time": end_time,
        "count": count,
        "dividend_type": dividend_type,
        "fill_data": fill_data,
    }
    if data_dir:
        kwargs["data_dir"] = data_dir
    return _run(xtdata.get_local_data, **kwargs)


@mcp.tool()
def get_full_kline(
    field_list: list[str] | None = None,
    stock_list: list[str] | None = None,
    period: str = "1m",
    start_time: str = "",
    end_time: str = "",
    count: int = 1,
    dividend_type: str = "none",
    fill_data: bool = True,
) -> dict[str, Any]:
    """
    获取最新交易日K线全推数据。
    """
    xtdata = _xtdata()
    return _run(
        xtdata.get_full_kline,
        field_list or [],
        stock_list or [],
        period,
        start_time,
        end_time,
        count,
        dividend_type,
        fill_data,
    )


@mcp.tool()
def download_history_data(
    stock_code: str,
    period: str,
    start_time: str = "",
    end_time: str = "",
    incrementally: bool | None = None,
) -> dict[str, Any]:
    """
    下载单标的历史行情数据。
    """
    xtdata = _xtdata()
    return _run(
        xtdata.download_history_data,
        stock_code,
        period,
        start_time,
        end_time,
        incrementally,
    )


@mcp.tool()
def download_history_data2(
    stock_list: list[str],
    period: str,
    start_time: str = "",
    end_time: str = "",
    incrementally: bool | None = None,
) -> dict[str, Any]:
    """
    批量下载历史行情数据。
    """
    xtdata = _xtdata()
    return _run(
        xtdata.download_history_data2,
        stock_list,
        period,
        start_time,
        end_time,
        None,
        incrementally,
    )


@mcp.tool()
def get_divid_factors(
    stock_code: str,
    start_time: str = "",
    end_time: str = "",
) -> dict[str, Any]:
    """
    获取除权除息因子。
    """
    xtdata = _xtdata()
    return _run(xtdata.get_divid_factors, stock_code, start_time, end_time)


@mcp.tool()
def get_period_list() -> dict[str, Any]:
    """
    获取可用周期列表。
    """
    xtdata = _xtdata()
    return _run(xtdata.get_period_list)


@mcp.tool()
def get_holidays() -> dict[str, Any]:
    """
    获取节假日数据。
    """
    xtdata = _xtdata()
    return _run(xtdata.get_holidays)


@mcp.tool()
def get_trading_calendar(
    market: str,
    start_time: str = "",
    end_time: str = "",
) -> dict[str, Any]:
    """
    获取交易日历。
    """
    xtdata = _xtdata()
    return _run(xtdata.get_trading_calendar, market, start_time, end_time)


@mcp.tool()
def get_trading_dates(
    market: str,
    start_time: str = "",
    end_time: str = "",
    count: int = -1,
) -> dict[str, Any]:
    """
    获取交易日列表（时间戳）。
    """
    xtdata = _xtdata()
    return _run(xtdata.get_trading_dates, market, start_time, end_time, count)


@mcp.tool()
def get_instrument_detail(stock_code: str, iscomplete: bool = False) -> dict[str, Any]:
    """
    获取合约基础信息。
    """
    xtdata = _xtdata()
    return _run(xtdata.get_instrument_detail, stock_code, iscomplete)


@mcp.tool()
def get_instrument_type(stock_code: str) -> dict[str, Any]:
    """
    获取合约类型。
    """
    xtdata = _xtdata()
    return _run(xtdata.get_instrument_type, stock_code)


@mcp.tool()
def get_sector_list() -> dict[str, Any]:
    """
    获取板块列表。
    """
    xtdata = _xtdata()
    return _run(xtdata.get_sector_list)


@mcp.tool()
def get_stock_list_in_sector(sector_name: str, real_timetag: int = 0) -> dict[str, Any]:
    """
    获取板块成分股。
    """
    xtdata = _xtdata()
    return _run(xtdata.get_stock_list_in_sector, sector_name, real_timetag)


@mcp.tool()
def download_sector_data() -> dict[str, Any]:
    """
    下载板块分类信息。
    """
    xtdata = _xtdata()
    return _run(xtdata.download_sector_data)


@mcp.tool()
def get_index_weight(index_code: str) -> dict[str, Any]:
    """
    获取指数成分权重。
    """
    xtdata = _xtdata()
    return _run(xtdata.get_index_weight, index_code)


@mcp.tool()
def download_index_weight() -> dict[str, Any]:
    """
    下载指数成分权重信息。
    """
    xtdata = _xtdata()
    return _run(xtdata.download_index_weight)


@mcp.tool()
def get_financial_data(
    stock_list: list[str],
    table_list: list[str] | None = None,
    start_time: str = "",
    end_time: str = "",
    report_type: str = "report_time",
) -> dict[str, Any]:
    """
    获取财务数据。
    """
    xtdata = _xtdata()
    return _run(
        xtdata.get_financial_data,
        stock_list,
        table_list or [],
        start_time,
        end_time,
        report_type,
    )


@mcp.tool()
def download_financial_data(
    stock_list: list[str],
    table_list: list[str] | None = None,
) -> dict[str, Any]:
    """
    下载财务数据。
    """
    xtdata = _xtdata()
    return _run(xtdata.download_financial_data, stock_list, table_list or [])


@mcp.tool()
def get_cb_info(stockcode: str) -> dict[str, Any]:
    """
    获取可转债基础信息。
    """
    xtdata = _xtdata()
    return _run(xtdata.get_cb_info, stockcode)


@mcp.tool()
def download_cb_data() -> dict[str, Any]:
    """
    下载可转债基础信息。
    """
    xtdata = _xtdata()
    return _run(xtdata.download_cb_data)


@mcp.tool()
def get_ipo_info(start_time: str = "", end_time: str = "") -> dict[str, Any]:
    """
    获取新股申购信息。
    """
    xtdata = _xtdata()
    return _run(xtdata.get_ipo_info, start_time, end_time)


@mcp.tool()
def download_etf_info() -> dict[str, Any]:
    """
    下载 ETF 申赎清单信息。
    """
    xtdata = _xtdata()
    return _run(xtdata.download_etf_info)


@mcp.tool()
def get_etf_info() -> dict[str, Any]:
    """
    获取 ETF 申赎清单信息。
    """
    xtdata = _xtdata()
    return _run(xtdata.get_etf_info)


@mcp.tool()
def download_holiday_data() -> dict[str, Any]:
    """
    下载节假日数据。
    """
    xtdata = _xtdata()
    return _run(xtdata.download_holiday_data)


def get_app() -> Any:
    """获取 ASGI 应用，供 uvicorn 等服务器使用。"""
    return mcp.streamable_http_app()


def main() -> None:
    import os
    host = os.getenv("MCP_HOST", "127.0.0.1")
    port = int(os.getenv("MCP_PORT", "8000"))
    mcp.run(transport="sse", host=host, port=port)


if __name__ == "__main__":
    main()

