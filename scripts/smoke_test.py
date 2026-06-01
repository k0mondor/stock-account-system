"""本地冒烟测试：健康检查 + 开户申请全流程"""

import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8000"


def call(method: str, path: str, body: dict | None = None) -> dict:
    url = f"{BASE}{path}"
    data = None
    headers = {"Content-Type": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode())


def main() -> int:
    print("1. GET /health")
    health = call("GET", "/health")
    print(json.dumps(health, ensure_ascii=False, indent=2))
    if health.get("status") != "ok":
        print("FAIL: health check")
        return 1

    suffix = __import__("uuid").uuid4().hex[:8]
    username = f"test_{suffix}"
    id_card = f"1101011990{suffix[:2]}01{suffix[2:6]}"

    print("\n2. POST submit application")
    submit = call(
        "POST",
        "/api/v1/account/applications/submit",
        {
            "username": username,
            "real_name": "测试用户",
            "id_card": id_card,
            "phone": f"138{suffix[:8]}",
            "email": f"{username}@example.com",
        },
    )
    print(json.dumps(submit, ensure_ascii=False, indent=2, default=str))
    if not submit.get("success"):
        print("FAIL: submit")
        return 1

    app_id = submit["data"]["application_id"]

    print("\n3. GET query PENDING")
    query = call("GET", f"/api/v1/account/applications/query?status=PENDING&username={username}")
    print(f"   found {len(query.get('data') or [])} item(s), success={query.get('success')}")

    print("\n4. POST approve")
    approve = call(
        "POST",
        "/api/v1/account/applications/approve",
        {
            "application_id": app_id,
            "approver_id": "ADMIN001",
            "approver_name": "管理员",
            "action": "APPROVE",
            "reason": "冒烟测试通过",
        },
    )
    print(json.dumps(approve, ensure_ascii=False, indent=2, default=str))
    if not approve.get("success"):
        print("FAIL: approve")
        return 1

    print("\n5. GET approval-history")
    history = call("GET", f"/api/v1/account/applications/{app_id}/approval-history")
    print(json.dumps(history, ensure_ascii=False, indent=2, default=str))
    if not history.get("success"):
        print("FAIL: history")
        return 1

    print("\n=== ALL SMOKE TESTS PASSED ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
