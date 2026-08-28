"""MCP SERVER minh hoạ — công bố tool `get_weather` qua giao thức MCP.

Khác với function calling: tool nằm ở một server ĐỘC LẬP. Server tự "khai
báo" tool của mình; bất kỳ MCP client nào (Claude Code, Claude Desktop,
Cursor, hoặc weather_client.py) cũng cắm vào dùng được mà không cần biết
code bên trong.

Schema của tool được TỰ ĐỘNG sinh ra từ type hints + docstring.

Chạy trực tiếp:
    pip install -r ../requirements.txt
    python weather_server.py

Đăng ký với Claude Code (làm 1 lần, dùng mãi):
    claude mcp add weather -- python /đường/dẫn/tới/weather_server.py
"""

from mcp.server.mcpserver import MCPServer

mcp = MCPServer("weather")

_MOCK_DB = {
    "Hanoi": "29°C, trời mưa",
    "Haiphong": "33°C, mưa rào",
    "Danang": "30°C, nhiều mây",
}


@mcp.tool()
def get_weather(city: str) -> str:
    """Lấy thời tiết hiện tại của một thành phố."""
    return f"{city}: {_MOCK_DB.get(city, '28°C, không có dữ liệu chi tiết')}"


@mcp.tool()
def search_logs(keyword: str = "ERROR", limit: int = 5) -> str:
    """Tìm các dòng log gần nhất chứa keyword (mặc định: lỗi).

    Đọc file app.log ngay cạnh server; nếu chưa có file thì tạo một file
    log mẫu để minh hoạ. Dữ liệu là ĐỘNG — tool xử lý công việc thực tế.

    Args:
        keyword: Từ khoá cần tìm trong log (mặc định "ERROR")
        limit: Số dòng kết quả tối đa (mặc định 5)
    """
    from pathlib import Path

    log_file = Path(__file__).parent / "app.log"
    if not log_file.exists():
        # Tạo log mẫu lần đầu để demo — production sẽ có file log thật
        sample = (
            "2026-08-28 10:00:01 INFO  server started on :8085\n"
            "2026-08-28 10:05:22 ERROR connection refused to db:5432\n"
            "2026-08-28 10:07:45 WARN  retry 1/3 for db connection\n"
            "2026-08-28 10:09:11 ERROR timeout after 30s calling weatherapi\n"
            "2026-08-28 10:12:00 INFO  request /weather?city=Hanoi 200\n"
            "2026-08-28 10:15:33 ERROR 500 internal error: key 'temp' missing\n"
            "2026-08-28 10:18:02 INFO  cache refreshed 42 entries\n"
            "2026-08-28 10:20:19 ERROR failed to parse payload: unexpected EOF\n"
        )
        log_file.write_text(sample, encoding="utf-8")

    lines = log_file.read_text(encoding="utf-8").splitlines()
    matches = [ln for ln in lines if keyword.upper() in ln.upper()]
    matches = matches[-limit:]  # các dòng GẦN NHẤT khớp

    if not matches:
        return f"Không tìm thấy dòng nào chứa '{keyword}' trong {log_file.name}."
    return "\n".join(reversed(matches))  # mới nhất lên đầu


if __name__ == "__main__":
    mcp.run()  # mặc định chạy qua stdio
