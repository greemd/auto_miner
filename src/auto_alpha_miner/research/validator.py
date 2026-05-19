"""Validate generated strategy files before running backtests."""

from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path

    import numpy as np
    import pandas as pd
    import subprocess


def validate_strategy_file(file_path: Path) -> tuple[bool, str]:
    """Validate a strategy .py file.

    Checks:
    1. Valid Python syntax (AST parse)
    2. Imports BaseStrategy and register_strategy
    3. Has a class with @register_strategy decorator
    4. Class has name, prepare, generate_signals
    5. Smoke test: instantiate and run on synthetic data

    Returns (True, "") on success, (False, error_message) on failure.
    """
    if not file_path.exists():
        return False, f"File not found: {file_path}"

    source = file_path.read_text(encoding="utf-8")

    # Step 1: Valid Python syntax
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return False, f"Syntax error: {e}"

    # Step 2: Static analysis with flake8
    try:
        result = subprocess.run(
            ["flake8", str(file_path)],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            return False, f"Flake8 issues:\n{result.stdout}"
    except FileNotFoundError:
        return False, "Flake8 not found. Please install it (pip install flake8)."

    # Step 3: Check for BaseStrategy class with register_strategy
    has_register = False
    strategy_class_name = None

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for decorator in node.decorator_list:
                dec_name = ""
                if isinstance(decorator, ast.Name):
                    dec_name = decorator.id
                elif isinstance(decorator, ast.Attribute):
                    dec_name = decorator.attr
                if dec_name == "register_strategy":
                    has_register = True
                    strategy_class_name = node.name
                    break

    # Step 3: Check for BaseStrategy class with register_strategy
    if not has_register or not strategy_class_name:
        return False, "No class found with @register_strategy decorator"

    # Step 4: Check class has required attributes/methods
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == strategy_class_name:
            method_names = {n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
            attr_names = set()
            for n in node.body:
                if isinstance(n, ast.Assign):
                    for target in n.targets:
                        if isinstance(target, ast.Name):
                            attr_names.add(target.id)

            if "name" not in attr_names:
                return False, f"Class {strategy_class_name} missing 'name' attribute"
            if "prepare" not in method_names:
                return False, f"Class {strategy_class_name} missing 'prepare' method"
            if "generate_signals" not in method_names:
                return False, f"Class {strategy_class_name} missing 'generate_signals' method"

    # Step 5: Smoke test — import and run on synthetic data
    try:
        module_name = f"auto_alpha_miner.strategy.{file_path.stem}"

        # Remove from cache if previously imported
        if module_name in sys.modules:
            del sys.modules[module_name]

        module = importlib.import_module(module_name)

        # Find the strategy class
        from auto_alpha_miner.strategy.base import BaseStrategy
        strat_cls = None
        for attr_name in dir(module):
            obj = getattr(module, attr_name)
            if isinstance(obj, type) and issubclass(obj, BaseStrategy) and obj is not BaseStrategy:
                strat_cls = obj
                break

        if strat_cls is None:
            return False, "Could not find a BaseStrategy subclass in the module"

        # Create synthetic data
        np.random.seed(42)
        n = 100
        dates = pd.bdate_range("2020-01-01", periods=n)
        close = 100 + np.cumsum(np.random.randn(n) * 2)
        close = np.maximum(close, 10)  # Ensure positive
        df = pd.DataFrame(
            {
                "Open": close * (1 + np.random.randn(n) * 0.005),
                "High": close * (1 + abs(np.random.randn(n) * 0.01)),
                "Low": close * (1 - abs(np.random.randn(n) * 0.01)),
                "Close": close,
                "Volume": np.random.randint(100_000, 1_000_000, n),
            },
            index=dates,
        )

        strat = strat_cls()
        prepared = strat.prepare(df.copy())

        if not isinstance(prepared, pd.DataFrame):
            return False, "prepare() must return a pd.DataFrame"
        if len(prepared) == 0:
            return False, "prepare() returned an empty DataFrame"

        signals = strat.generate_signals(prepared)

        if not isinstance(signals, list):
            return False, "generate_signals() must return a list"

    except Exception as e:
        return False, f"Smoke test failed: {type(e).__name__}: {e}"

    return True, ""
