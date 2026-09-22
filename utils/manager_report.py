import json
from pathlib import Path


REPORT_DIR = Path("reports")
RESULTS_FILE = REPORT_DIR / "test-results.json"
MANAGER_REPORT_FILE = REPORT_DIR / "manager-summary.html"


def generate_manager_report():
    with RESULTS_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    test_rows = ""

    for test_case in data["test_cases"]:
        status = test_case["status"]

        if status == "PASSED":
            css_class = "passed"
        elif status == "FAILED":
            css_class = "failed"
        else:
            css_class = "skipped"

        test_rows += f"""
        <tr>
            <td>{test_case["name"]}</td>
            <td class="{css_class}">{status}</td>
        </tr>
        """

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Manager Test Summary</title>

    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f5f6f8;
        }}

        .report {{
            max-width: 1000px;
            margin: auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
        }}

        h1 {{
            margin-bottom: 5px;
        }}

        .subtitle {{
            color: #666;
            margin-bottom: 25px;
        }}

        .summary {{
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
        }}

        .box {{
            padding: 18px;
            border: 1px solid #ddd;
            border-radius: 6px;
            min-width: 120px;
            text-align: center;
        }}

        .number {{
            font-size: 28px;
            font-weight: bold;
        }}

        .label {{
            color: #666;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th, td {{
            padding: 12px;
            border-bottom: 1px solid #ddd;
            text-align: left;
        }}

        th {{
            background-color: #eeeeee;
        }}

        .passed {{
            color: green;
            font-weight: bold;
        }}

        .failed {{
            color: red;
            font-weight: bold;
        }}

        .skipped {{
            color: orange;
            font-weight: bold;
        }}

        .overall {{
            margin-top: 25px;
            padding: 15px;
            background-color: #e8f5e9;
            color: green;
            font-size: 20px;
            font-weight: bold;
            text-align: center;
            border-radius: 6px;
        }}
    </style>
</head>

<body>

<div class="report">

    <h1>{data["project"]}</h1>

    <div class="subtitle">
        Manager Test Summary Report
    </div>

    <p>
        <strong>Environment:</strong> {data["environment"]}<br>
        <strong>Browser:</strong> {data["browser"]}<br>
        <strong>Execution:</strong> {data["execution_type"]}<br>
        <strong>Date:</strong> {data["date"]}<br>
        <strong>Time:</strong> {data["time"]}
    </p>

    <div class="summary">

        <div class="box">
            <div class="number">{data["total"]}</div>
            <div class="label">Total</div>
        </div>

        <div class="box">
            <div class="number passed">{data["passed"]}</div>
            <div class="label">Passed</div>
        </div>

        <div class="box">
            <div class="number failed">{data["failed"]}</div>
            <div class="label">Failed</div>
        </div>

        <div class="box">
            <div class="number skipped">{data["skipped"]}</div>
            <div class="label">Skipped</div>
        </div>

    </div>

    <h2>Test Cases</h2>

    <table>

        <tr>
            <th>Test Case</th>
            <th>Result</th>
        </tr>

        {test_rows}

    </table>

    <div class="overall">
        OVERALL RESULT: {data["overall"]}
    </div>

</div>

</body>
</html>
"""

    with MANAGER_REPORT_FILE.open("w", encoding="utf-8") as file:
        file.write(html)

    print(f"Manager report created: {MANAGER_REPORT_FILE}")


if __name__ == "__main__":
    generate_manager_report()