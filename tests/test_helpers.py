"""Tests for helper functions."""

import json
from pathlib import Path
from unittest.mock import MagicMock

import click
import pytest

from frappecli.helpers import (
    create_simple_table,
    get_output_format,
    load_data,
    output_as_json,
    output_data,
)


class TestLoadData:
    """Test load_data function."""

    def test_load_inline_json(self) -> None:
        """Test loading inline JSON string."""
        data = load_data('{"key": "value"}')
        assert data == {"key": "value"}

    def test_load_from_file(self, tmp_path: Path) -> None:
        """Test loading JSON from file."""
        test_file = tmp_path / "data.json"
        test_file.write_text('{"key": "value"}')

        data = load_data(f"@{test_file}")
        assert data == {"key": "value"}

    def test_load_complex_json(self) -> None:
        """Test loading complex JSON."""
        json_str = '{"name": "Test", "nested": {"key": "value"}, "array": [1, 2, 3]}'
        data = load_data(json_str)
        assert data["name"] == "Test"
        assert data["nested"]["key"] == "value"
        assert data["array"] == [1, 2, 3]


class TestOutputAsJson:
    """Test output_as_json function."""

    def test_output_dict(self, capsys: pytest.CaptureFixture) -> None:
        """Test outputting dictionary as JSON."""
        output_as_json({"key": "value"})
        captured = capsys.readouterr()
        assert json.loads(captured.out) == {"key": "value"}

    def test_output_list(self, capsys: pytest.CaptureFixture) -> None:
        """Test outputting list as JSON."""
        output_as_json([1, 2, 3])
        captured = capsys.readouterr()
        assert json.loads(captured.out) == [1, 2, 3]


class TestGetOutputFormat:
    """Test get_output_format function."""

    def test_json_format(self) -> None:
        """Test JSON format detection."""
        ctx = MagicMock(spec=click.Context)
        ctx.obj = {"output_json": True}
        assert get_output_format(ctx) == "json"

    def test_table_format(self) -> None:
        """Test table format detection (default)."""
        ctx = MagicMock(spec=click.Context)
        ctx.obj = {"output_json": False}
        assert get_output_format(ctx) == "table"

    def test_table_format_default(self) -> None:
        """Test table format when output_json not in context."""
        ctx = MagicMock(spec=click.Context)
        ctx.obj = {}
        assert get_output_format(ctx) == "table"


class TestOutputData:
    """Test output_data function."""

    def test_output_json_format(self, capsys: pytest.CaptureFixture) -> None:
        """Test outputting data in JSON format."""
        data = {"key": "value"}
        output_data(data, "json")
        captured = capsys.readouterr()
        assert json.loads(captured.out) == data

    def test_output_table_format(self, capsys: pytest.CaptureFixture) -> None:
        """Test outputting data in table format."""
        data = {"key": "value"}
        called = False

        def render_table(d: dict) -> None:
            nonlocal called
            called = True
            assert d == data

        output_data(data, "table", render_table)
        assert called is True

    def test_output_table_without_renderer(self, capsys: pytest.CaptureFixture) -> None:
        """Test outputting data without custom renderer falls back to console.print."""
        data = "test string"
        output_data(data, "table")
        captured = capsys.readouterr()
        assert "test string" in captured.out


class TestCreateSimpleTable:
    """Test create_simple_table function."""

    def test_create_table_basic(self) -> None:
        """Test creating a basic table."""
        data = [
            {"name": "Alice", "age": "30"},
            {"name": "Bob", "age": "25"},
        ]
        columns = [("name", "Name"), ("age", "Age")]

        table = create_simple_table("Test Table", data, columns)

        assert table.title == "Test Table"
        assert len(table.columns) == 2
        assert len(table.rows) == 2

    def test_create_table_with_max_columns(self) -> None:
        """Test creating table with column limit."""
        data = [
            {"name": "Alice", "age": "30", "city": "NYC"},
        ]
        columns = [("name", "Name"), ("age", "Age"), ("city", "City")]

        table = create_simple_table("Test Table", data, columns, max_columns=2)

        assert len(table.columns) == 2  # Only first 2 columns

    def test_create_table_empty_data(self) -> None:
        """Test creating table with empty data."""
        data: list[dict] = []
        columns = [("name", "Name")]

        table = create_simple_table("Test Table", data, columns)

        assert table.title == "Test Table"
        assert len(table.rows) == 0

    def test_create_table_missing_field(self) -> None:
        """Test creating table with missing field in data."""
        data = [
            {"name": "Alice"},  # Missing 'age' field
        ]
        columns = [("name", "Name"), ("age", "Age")]

        table = create_simple_table("Test Table", data, columns)

        assert len(table.rows) == 1
        # Should handle missing field gracefully (empty string)
