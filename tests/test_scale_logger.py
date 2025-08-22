from tools.scale_logger import rows_to_csv


def test_rows_to_csv_scale_only():
    rows = [
        {"timestamp": 1.0, "source": "bookoo", "weight_g": 10.0, "flow_gps": 0.0, "stable": True},
        {"timestamp": 2.0, "source": "halfdecent", "weight_g": 20.0, "flow_gps": 0.1, "stable": False},
    ]
    csv_text = rows_to_csv(rows)
    lines = [ln for ln in csv_text.strip().splitlines()]
    assert lines[0].startswith('timestamp,source,weight_g,flow_gps,stable')
    assert 'bookoo' in lines[1]
    assert 'halfdecent' in lines[2]


def test_rows_to_csv_aggregate():
    rows = [
        {
            "ts": 3.0,
            "tank": {"level_pct": 42.0, "state": "ok"},
            "scale": {"source": "bookoo", "weight_g": 12.3, "flow_gps": 0.0, "stable": True},
        }
    ]
    csv_text = rows_to_csv(rows)
    lines = [ln for ln in csv_text.strip().splitlines()]
    assert lines[1].startswith('3.0,bookoo,12.3,0.0,True,42.0,ok')
