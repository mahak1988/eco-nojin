from __future__ import annotations

import ast
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple

# ریشه پروژه
PROJECT_ROOT = Path(r"D:\econojin.com")

# ریشه کدهای API
API_ROOT = PROJECT_ROOT / "api"

# خروجی‌ها
OUTPUT_DIR = PROJECT_ROOT / "structure_reports"
OUTPUT_JSON = OUTPUT_DIR / "api_endpoints.json"
OUTPUT_MD = OUTPUT_DIR / "api_endpoints.md"

# فقط این پوشه‌ها را برای روترها و اسکیم‌ها اسکن می‌کنیم
ROUTER_GLOB_PATTERNS = [
    "domains/**/routers/*.py",
    "modules/**/router.py",
    "modules/**/admin_router.py",
    "scientific_core/router.py",
]

SCHEMAS_GLOB_PATTERNS = [
    "domains/**/schemas/*.py",
    "modules/**/schemas.py",
    "core/schemas.py",
]


@dataclass
class ModelField:
    name: str
    type: str
    default: Optional[str]


@dataclass
class ModelInfo:
    name: str
    module: str
    fields: List[ModelField]


@dataclass
class EndpointInfo:
    domain: str
    layer: str  # "domain" یا "module" یا "core"
    file: str
    function_name: str
    http_method: str
    path: str
    summary: Optional[str]
    request_models: List[str]
    response_models: List[str]


def find_python_files(base: Path, patterns: List[str]) -> List[Path]:
    files: List[Path] = []
    for pattern in patterns:
        for f in base.glob(pattern):
            if f.is_file():
                files.append(f)
    return files


def is_router_decorator(dec: ast.expr) -> Optional[Tuple[str, str]]:
    """
    اگر decorator به‌شکل router.get("/path") یا router.post(...) بود،
    (method, path) را برمی‌گرداند؛ در غیر این صورت None.
    """
    if not isinstance(dec, ast.Call):
        return None
    func = dec.func
    if not isinstance(func, ast.Attribute):
        return None
    if not isinstance(func.value, ast.Name):
        return None
    if func.value.id != "router":
        return None

    method = func.attr.lower()
    if method not in {"get", "post", "put", "delete", "patch"}:
        return None

    path = ""
    if dec.args:
        first = dec.args[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            path = first.value

    return method, path


def get_function_docstring(fn: ast.FunctionDef) -> Optional[str]:
    doc = ast.get_docstring(fn)
    if doc:
        lines = [line.strip() for line in doc.splitlines() if line.strip()]
        if lines:
            return lines[0]
    return None


def extract_type_names(node: ast.AST) -> List[str]:
    """
    از annotation یا expression، نام تایپ‌های استفاده‌شده را استخراج می‌کند
    (به شکل ساده؛ برای استفاده در request/response models).
    """
    names: List[str] = []

    def visit(n: ast.AST):
        if isinstance(n, ast.Name):
            names.append(n.id)
        elif isinstance(n, ast.Attribute):
            names.append(n.attr)
        elif isinstance(n, (ast.Subscript, ast.Call)):
            if hasattr(n, "func"):
                visit(n.func)  # type: ignore
            if hasattr(n, "value"):
                visit(n.value)  # type: ignore
            if hasattr(n, "slice"):
                visit(n.slice)  # type: ignore
        elif isinstance(n, ast.Tuple):
            for el in n.elts:
                visit(el)

    visit(node)
    return names


def parse_router_file(path: Path, api_root: Path) -> List[EndpointInfo]:
    rel = path.relative_to(api_root).as_posix()
    text = path.read_text(encoding="utf-8", errors="ignore")
    tree = ast.parse(text)

    endpoints: List[EndpointInfo] = []

    # domain/module/core layer تشخیص
    parts = rel.split("/")
    if parts[0] == "domains":
        layer = "domain"
        domain_name = parts[1]
    elif parts[0] == "modules":
        layer = "module"
        domain_name = parts[1]
    elif parts[0] == "scientific_core":
        layer = "scientific_core"
        domain_name = "scientific_core"
    else:
        layer = "core"
        domain_name = "core"

    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        http_method = None
        path_str = ""
        for dec in node.decorator_list:
            info = is_router_decorator(dec)
            if info:
                http_method, path_str = info
                break
        if not http_method:
            continue

        summary = get_function_docstring(node)

        # request models (از پارامترهای تابع)
        request_models: List[str] = []
        for arg in node.args.args:
            if arg.annotation:
                request_models.extend(extract_type_names(arg.annotation))

        # response models (از return annotation در صورت وجود)
        response_models: List[str] = []
        if node.returns:
            response_models.extend(extract_type_names(node.returns))

        ep = EndpointInfo(
            domain=domain_name,
            layer=layer,
            file=rel,
            function_name=node.name,
            http_method=http_method.upper(),
            path=path_str,
            summary=summary,
            request_models=sorted(set(request_models)),
            response_models=sorted(set(response_models)),
        )
        endpoints.append(ep)

    return endpoints


def parse_schemas_file(path: Path, api_root: Path) -> List[ModelInfo]:
    rel = path.relative_to(api_root).as_posix()
    text = path.read_text(encoding="utf-8", errors="ignore")
    tree = ast.parse(text)

    models: List[ModelInfo] = []

    class_bases: Dict[str, List[str]] = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            bases: List[str] = []
            for b in node.bases:
                bases.extend(extract_type_names(b))
            class_bases[node.name] = bases

    # کلاس‌هایی که BaseModel یا Schema-based هستند را به‌عنوان مدل در نظر می‌گیریم
    schema_like_classes = {
        cls
        for cls, bases in class_bases.items()
        if any("BaseModel" in b or "Schema" in b or "Model" in b for b in bases)
    }

    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name in schema_like_classes:
            fields: List[ModelField] = []
            for stmt in node.body:
                if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                    fname = stmt.target.id
                    ftype = ""
                    if stmt.annotation:
                        ftypes = extract_type_names(stmt.annotation)
                        ftype = ", ".join(sorted(set(ftypes))) if ftypes else ""
                    default_repr: Optional[str] = None
                    if stmt.value is not None:
                        default_repr = ast.unparse(stmt.value) if hasattr(ast, "unparse") else "..."
                    fields.append(ModelField(name=fname, type=ftype, default=default_repr))

            models.append(
                ModelInfo(
                    name=node.name,
                    module=rel,
                    fields=fields,
                )
            )

    return models


def build_catalog() -> Dict[str, Any]:
    if not API_ROOT.exists():
        raise FileNotFoundError(f"API root not found: {API_ROOT}")

    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

    # روترها
    router_files = find_python_files(API_ROOT, ROUTER_GLOB_PATTERNS)

    all_endpoints: List[EndpointInfo] = []
    for f in router_files:
        try:
            eps = parse_router_file(f, API_ROOT)
            all_endpoints.extend(eps)
        except SyntaxError:
            # اگر فایلی از نظر AST مشکل داشت، فعلاً رد می‌کنیم
            continue

    # اسکیم‌ها/مدل‌ها
    schema_files = find_python_files(API_ROOT, SCHEMAS_GLOB_PATTERNS)
    all_models: List[ModelInfo] = []
    for f in schema_files:
        try:
            ms = parse_schemas_file(f, API_ROOT)
            all_models.extend(ms)
        except SyntaxError:
            continue

    # اندیس مدل‌ها برای lookup سریع
    models_by_name: Dict[str, List[ModelInfo]] = {}
    for m in all_models:
        models_by_name.setdefault(m.name, []).append(m)

    # خروجی ساختاریافته
    endpoints_out: List[Dict[str, Any]] = []
    for ep in sorted(all_endpoints, key=lambda e: (e.layer, e.domain, e.path, e.http_method, e.function_name)):
        endpoints_out.append(asdict(ep))

    models_out: List[Dict[str, Any]] = []
    for m in sorted(all_models, key=lambda x: (x.module, x.name)):
        models_out.append(
            {
                "name": m.name,
                "module": m.module,
                "fields": [asdict(f) for f in m.fields],
            }
        )

    catalog: Dict[str, Any] = {
        "project_root": str(PROJECT_ROOT),
        "api_root": str(API_ROOT),
        "endpoints": endpoints_out,
        "models": models_out,
    }
    return catalog


def write_json(catalog: Dict[str, Any]) -> None:
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)


def write_markdown(catalog: Dict[str, Any]) -> None:
    lines: List[str] = []

    lines.append(f"# API Endpoint Catalog\n")
    lines.append(f"- Project root: `{catalog['project_root']}`")
    lines.append(f"- API root: `{catalog['api_root']}`")
    lines.append(f"- Total endpoints: {len(catalog['endpoints'])}")
    lines.append(f"- Total models: {len(catalog['models'])}")
    lines.append("")

    # گروه‌بندی endpointها بر اساس لایه/دامین برای خوانایی در فرانت‌اند و ایجنت
    grouped: Dict[str, Dict[str, List[EndpointInfo]]] = {}
    for ep_dict in catalog["endpoints"]:
        ep = EndpointInfo(**ep_dict)  # type: ignore
        key_layer = ep.layer
        key_domain = ep.domain
        grouped.setdefault(key_layer, {}).setdefault(key_domain, []).append(ep)

    for layer, domains in grouped.items():
        lines.append(f"## Layer: {layer}")
        lines.append("")
        for domain, eps in sorted(domains.items()):
            lines.append(f"### Domain/Module: {domain}")
            lines.append("")
            lines.append("| Method | Path | Function | Request Models | Response Models | Summary |")
            lines.append("|--------|------|----------|----------------|-----------------|---------|")
            for ep in sorted(eps, key=lambda x: (x.path, x.http_method)):
                rq = ", ".join(ep.request_models) if ep.request_models else "-"
                rs = ", ".join(ep.response_models) if ep.response_models else "-"
                sm = ep.summary or ""
                lines.append(
                    f"| {ep.http_method} | `{ep.path}` | `{ep.function_name}` | "
                    f"{rq} | {rs} | {sm} |"
                )
            lines.append("")

    # مدل‌ها (برای طراحی فرم‌ها و جداول)
    lines.append("## Models (Schemas)\n")
    for m in catalog["models"]:
        lines.append(f"### {m['name']}  \n`{m['module']}`")
        lines.append("")
        if not m["fields"]:
            lines.append("_No fields detected_\n")
            continue
        lines.append("| Field | Type | Default |")
        lines.append("|-------|------|---------|")
        for fld in m["fields"]:
            default = fld["default"] if fld["default"] is not None else "-"
            lines.append(f"| {fld['name']} | {fld['type']} | {default} |")
        lines.append("")

    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")


def pretty_print(catalog: Dict[str, Any]) -> None:
    total_eps = len(catalog["endpoints"])
    total_models = len(catalog["models"])
    print("=" * 80)
    print("API ENDPOINT CATALOG")
    print("=" * 80)
    print(f"Endpoints: {total_eps}")
    print(f"Models: {total_models}")
    print(f"JSON: {OUTPUT_JSON}")
    print(f"Markdown: {OUTPUT_MD}")
    print("=" * 80)


def main() -> None:
    catalog = build_catalog()
    write_json(catalog)
    write_markdown(catalog)
    pretty_print(catalog)


if __name__ == "__main__":
    main()