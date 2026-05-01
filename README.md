# api-check-tklq

API tra cứu thông tin **công khai** của tài khoản Liên Quân Mobile (Arena of Valor),
viết bằng **FastAPI + Python 3.12**.

> ⚠️ **Lưu ý quan trọng về dữ liệu:** Garena/Tencent **không** cung cấp public API chính
> thức cho thông tin người chơi Liên Quân Mobile. API này được thiết kế xoay quanh
> **provider abstraction**: bạn cấu hình provider phù hợp với môi trường deploy của
> mình. Phần rank / level / skin sở hữu là **stub** vì không có nguồn công khai.

## Tính năng

| Endpoint | Data thật / Stub | Mô tả |
|---|---|---|
| `GET /api/players/{id}/nickname` | **Thật** (qua provider) | Tra cứu nickname theo Open ID |
| `GET /api/players/{id}/profile` | Stub | Hồ sơ chi tiết: rank, level, role chính |
| `GET /api/players/{id}/heroes` | Stub | Danh sách tướng người chơi sở hữu |
| `GET /api/heroes` | **Thật** (dataset đi kèm) | Danh sách tướng (có lọc role) |
| `GET /api/heroes/{id}` | **Thật** | Chi tiết một tướng |
| `GET /` / `GET /health` | — | Metadata + healthcheck |
| `GET /docs` | — | Swagger UI tự sinh |

## Provider lookup nickname

Cấu hình qua biến môi trường `LIENQUAN_PROVIDER`:

| Provider | Mô tả | Khi nào dùng |
|---|---|---|
| `mock` (mặc định) | Sinh nickname deterministic từ player_id | Dev / test / demo |
| `garena_shop` | Gọi `shop.garena.vn/api/shop/inv_check` | Production deploy tại VN |

Để tích hợp nguồn data của riêng bạn (DB, API nội bộ, file CSV...), tạo class kế thừa
`PlayerLookupProvider` trong `app/providers/`, đăng ký trong
[`app/providers/__init__.py`](app/providers/__init__.py).

## Yêu cầu

- Python **3.12** trở lên
- [`uv`](https://github.com/astral-sh/uv) (khuyến nghị) hoặc `pip`

## Cài đặt & chạy local

```bash
# Cài dependencies (uv tự tạo virtualenv)
uv sync

# Tạo file .env (không bắt buộc — provider mặc định là mock)
cp .env.example .env

# Chạy server dev có hot-reload
uv run uvicorn app.main:app --reload --port 8000
```

Mở trình duyệt:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Healthcheck: http://localhost:8000/health

### Dùng pip (không có uv)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"   # hoặc: pip install fastapi uvicorn[standard] httpx pydantic pydantic-settings
uvicorn app.main:app --reload
```

## Ví dụ gọi API

```bash
# Tra cứu nickname (mock provider trả deterministic)
curl http://localhost:8000/api/players/123456789/nickname

# Lọc tướng theo role
curl "http://localhost:8000/api/heroes?role=MARKSMAN"

# Chi tiết tướng
curl http://localhost:8000/api/heroes/krixi

# Hồ sơ người chơi (stub)
curl http://localhost:8000/api/players/123456789/profile
```

Response mẫu:

```json
{
  "player_id": "123456789",
  "nickname": "RongLuaChua547",
  "found": true,
  "source": "mock",
  "looked_up_at": "2026-05-01T07:42:00.000000+00:00"
}
```

## Test

```bash
uv run pytest -v
uv run ruff check .
```

Test bao gồm:
- Mỗi endpoint HTTP qua `TestClient`
- `MockProvider` deterministic
- `GarenaShopProvider` mock bằng `respx` (3 trường hợp: thành công, 404, nested data)

## Cắm data source thật cho rank / skin / tướng sở hữu

Liên Quân không có public API cho phần này. Cách phổ biến:

1. **DB của bạn**: tự lưu thông tin (ví dụ trang mua bán acc tự nhập tay, screenshot OCR).
2. **In-game friend lookup**: cần auth game → ngoài phạm vi API này.
3. **Provider tự build**: tạo class trong `app/providers/`, kế thừa `PlayerLookupProvider`,
   đăng ký trong `build_provider()`.

Trong `app/routers/players.py`, hàm `player_profile()` và `player_heroes()` hiện tại
trả stub data. Thay logic đó bằng cuộc gọi tới data source của bạn:

```python
# app/routers/players.py — sau khi có data source thật
profile = await request.app.state.profile_repo.get(player_id)
return profile
```

## Triển khai production

### Docker (gợi ý)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir fastapi "uvicorn[standard]" httpx pydantic pydantic-settings
COPY app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Deploy tại Việt Nam (cần thiết cho `garena_shop` provider)

`shop.garena.vn` thường giới hạn IP Việt Nam. Nếu bạn cần dùng provider `garena_shop`
nhưng deploy ngoài VN:

- Dùng VPS đặt tại Việt Nam (Vietnix, Tinohost, BizFly, ...).
- Hoặc đặt một forward-proxy chạy ở VN, cấu hình `httpx` đi qua proxy.

## Cấu trúc thư mục

```
app/
├── main.py                    # FastAPI app factory + lifespan
├── config.py                  # Pydantic Settings từ env
├── models.py                  # Pydantic schemas request/response
├── heroes_repo.py             # Đọc dataset tướng từ JSON
├── data/
│   └── heroes.json            # Dataset tướng (curated)
├── providers/
│   ├── base.py                # PlayerLookupProvider ABC
│   ├── mock.py                # Mock provider
│   ├── garena_shop.py         # Garena VN shop provider
│   └── __init__.py            # build_provider()
└── routers/
    ├── players.py             # /api/players/*
    └── heroes.py              # /api/heroes/*
tests/
├── conftest.py                # TestClient fixture
├── test_meta.py
├── test_players.py
├── test_heroes.py
└── test_providers.py
```

## Disclaimer

API này chỉ tra cứu thông tin **công khai** (nickname qua trang nạp thẻ chính thức của
Garena, hero metadata công khai). API **không** thực hiện đăng nhập tài khoản, không
brute-force, không kiểm tra password. Đừng dùng tool này (hoặc bất kỳ tool nào) để
"check acc" từ danh sách credential leak — đó là hành vi vi phạm pháp luật và ToS.

## License

MIT
