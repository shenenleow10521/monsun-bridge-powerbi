"""Static quality gate for the standalone MonsunOfficial PBIP project."""
import argparse
import json
import re
from pathlib import Path


def walk_fields(value):
    if isinstance(value, dict):
        for kind in ("Column", "Measure"):
            node = value.get(kind)
            if isinstance(node, dict):
                entity = node.get("Expression", {}).get("SourceRef", {}).get("Entity")
                prop = node.get("Property")
                if entity and prop:
                    yield kind, entity, prop
        for child in value.values():
            yield from walk_fields(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_fields(child)


def load_model(root):
    tables = {}
    for path in (root / "MonsunOfficial.SemanticModel" / "definition" / "tables").glob("*.tmdl"):
        content = path.read_text(encoding="utf-8")
        table_match = re.search(r"^table (?:'([^']+)'|(.+))$", content, re.M)
        if not table_match:
            raise ValueError(f"No table declaration: {path}")
        name = (table_match.group(1) or table_match.group(2)).strip()
        columns = {m.group(1).strip("'") for m in re.finditer(r"^\tcolumn (.+)$", content, re.M)}
        measures = set()
        for match in re.finditer(r"^\tmeasure (?:'([^']+)'|([^=]+?)) =", content, re.M):
            measures.add((match.group(1) or match.group(2)).strip())
        tables[name] = {"columns": columns, "measures": measures, "path": str(path)}
    return tables


def validate(root):
    required = [
        root / "MonsunOfficial.pbip",
        root / "MonsunOfficial.Report" / "definition.pbir",
        root / "MonsunOfficial.Report" / "definition" / "report.json",
        root / "MonsunOfficial.Report" / "definition" / "pages" / "pages.json",
        root / "MonsunOfficial.SemanticModel" / "definition.pbism",
        root / "MonsunOfficial.SemanticModel" / "definition" / "model.tmdl",
        root / "MonsunOfficial.SemanticModel" / "definition" / "relationships.tmdl",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise ValueError(f"Missing required artifacts: {missing}")

    json_files = list(root.rglob("*.json")) + list(root.rglob("*.pbip")) + list(root.rglob("*.pbir")) + list(root.rglob("*.pbism"))
    for path in json_files:
        json.loads(path.read_text(encoding="utf-8-sig"))

    model_text = "\n".join(path.read_text(encoding="utf-8") for path in root.rglob("*.tmdl"))
    prohibited = [token for token in ("File.Contents", "Web.Contents", "DUMMY") if token in model_text]
    if prohibited:
        raise ValueError(f"External or placeholder partition found: {prohibited}")

    tables = load_model(root)
    checked_fields = 0
    visual_files = list((root / "MonsunOfficial.Report" / "definition" / "pages").glob("*/visuals/*/visual.json"))
    for path in visual_files:
        visual = json.loads(path.read_text(encoding="utf-8"))
        for kind, entity, prop in walk_fields(visual):
            if entity not in tables:
                raise ValueError(f"{path}: missing table {entity}")
            bucket = "columns" if kind == "Column" else "measures"
            if prop not in tables[entity][bucket]:
                raise ValueError(f"{path}: missing {kind.lower()} {entity}.{prop}")
            checked_fields += 1

    pages_meta = json.loads((root / "MonsunOfficial.Report" / "definition" / "pages" / "pages.json").read_text())
    page_checks = []
    for page_name in pages_meta["pageOrder"]:
        page = root / "MonsunOfficial.Report" / "definition" / "pages" / page_name
        page_json = json.loads((page / "page.json").read_text())
        width, height = page_json["width"], page_json["height"]
        visuals = [json.loads(path.read_text()) for path in (page / "visuals").glob("*/visual.json")]
        for item in visuals:
            pos = item["position"]
            if min(pos["x"], pos["y"], pos["width"], pos["height"]) < 0 or pos["x"] + pos["width"] > width or pos["y"] + pos["height"] > height:
                raise ValueError(f"{page_name}: out-of-bounds visual {item['name']}")
        page_checks.append({"page": page_json["displayName"], "visuals": len(visuals), "bounds": "PASS"})

    status = json.loads((root / "Data" / "PROJECT_DATA_STATUS.json").read_text())
    result = {
        "result": "PASS",
        "json_artifacts_parsed": len(json_files),
        "model_tables": len(tables),
        "visual_field_references_checked": checked_fields,
        "external_file_or_api_partitions": 0,
        "integrated_official_datasets": len(status["integrated"]),
        "pages": page_checks,
        "desktop_runtime_tested": False,
    }
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path, nargs="?", default=Path("MonsunOfficial"))
    validate(parser.parse_args().project)
