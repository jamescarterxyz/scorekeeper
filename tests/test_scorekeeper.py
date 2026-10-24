"""ScoreKeeper self-test — headless Chromium assertions.

Run:  python3 tests/test_scorekeeper.py
Exit code 0 = all assertions pass.
"""

import functools
import http.server
import json
import os
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def board_totals(page):
    rows = page.query_selector_all("#board tbody tr")
    out = {}
    order = []
    for r in rows:
        cells = r.query_selector_all("td")
        name = cells[1].inner_text()
        out[name] = int(cells[2].inner_text())
        order.append(name)
    return out, order


def add_round(page, scores):
    for name, val in scores.items():
        page.fill('input[data-player="{}"]'.format(name), str(val))
    page.click("#addRoundBtn")


def main():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler,
                                directory=ROOT)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.on("dialog", lambda d: d.accept())
        page.goto("http://127.0.0.1:{}/index.html".format(port))

        for name in ("Alex", "Sam", "Jo"):
            page.fill("#playerName", name)
            page.click("#addPlayerBtn")
        page.click("#startBtn")

        add_round(page, {"Alex": 5, "Sam": 8, "Jo": 3})
        totals, _ = board_totals(page)
        assert totals == {"Alex": 5, "Sam": 8, "Jo": 3}, totals

        add_round(page, {"Alex": 8, "Sam": 9, "Jo": 9})
        totals, order = board_totals(page)
        assert totals == {"Alex": 13, "Sam": 17, "Jo": 12}, totals
        assert order[0] == "Sam", order
        leader = page.query_selector("#board tbody tr.leader")
        assert leader is not None, "leader row not highlighted"
        assert "Sam" in leader.inner_text(), leader.inner_text()

        # Reload: the game must persist.
        page.reload()
        totals, _ = board_totals(page)
        assert totals == {"Alex": 13, "Sam": 17, "Jo": 12}, totals

        # Undo reverts the last round.
        page.click("#undoBtn")
        totals, _ = board_totals(page)
        assert totals == {"Alex": 5, "Sam": 8, "Jo": 3}, totals

        # Re-add, then end the game: winner banner + saved game.
        add_round(page, {"Alex": 8, "Sam": 9, "Jo": 9})
        page.click("#endBtn")
        banner = page.inner_text("#winnerBanner")
        assert "Sam" in banner and "17" in banner, banner
        saved = page.inner_text("#savedList")
        assert "Sam" in saved, saved

        # JSON export round-trip.
        with page.expect_download() as dl:
            page.click("#exportBtn")
        download = dl.value
        path = "/tmp/scorekeeper-export.json"
        download.save_as(path)
        data = json.load(open(path))
        assert data["players"] == ["Alex", "Sam", "Jo"], data["players"]
        assert data["rounds"] == [{"Alex": 5, "Sam": 8, "Jo": 3},
                                  {"Alex": 8, "Sam": 9, "Jo": 9}], data["rounds"]
        assert data["finished"] is True

        page.click("#newGameBtn")
        assert page.query_selector("#game").is_hidden(), "game not cleared"
        page.set_input_files("#importFile", path)
        page.wait_for_timeout(500)
        totals, _ = board_totals(page)
        assert totals == {"Alex": 13, "Sam": 17, "Jo": 12}, totals
        assert "Sam" in page.inner_text("#winnerBanner")

        browser.close()
    server.shutdown()
    print("ALL SCOREKEEPER TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
