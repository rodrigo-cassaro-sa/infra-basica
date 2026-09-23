#!/usr/bin/env python3
"""
build-tokens.py — gera tokens.css (web) e tokens.ts (Expo/React Native) a partir de um
arquivo de tokens no formato DTCG 2025.10, e confere contraste WCAG dos pares de cor.

Uso:
  python3 build-tokens.py tokens.json --css src/styles/tokens.css --ts src/theme/tokens.ts
  python3 build-tokens.py tokens.json --check          # só relatório de contraste (sai 1 se falhar)

Convenções esperadas no arquivo (ver assets/tokens/tokens.json da skill ux-ui):
  color.light.* e color.dark.*  -> mesmas chaves semânticas (modos)
  spacing.*, radius.*, typography.*, font.family.base, shadow.*, motion.*, breakpoint.*, size.*
Só usa a biblioteca padrão do Python.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ALIAS = re.compile(r"^\{([^}]+)\}$")


# ---------- leitura e resolução de aliases ----------

def load(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def get_node(root: dict[str, Any], dotted: str) -> Any:
    node: Any = root
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            raise KeyError(f"Alias não encontrado: {{{dotted}}}")
        node = node[part]
    return node


def resolve(root: dict[str, Any], value: Any, seen: tuple[str, ...] = ()) -> Any:
    if isinstance(value, str):
        m = ALIAS.match(value)
        if m:
            ref = m.group(1)
            if ref in seen:
                raise ValueError(f"Alias circular: {' -> '.join(seen + (ref,))}")
            node = get_node(root, ref)
            if not isinstance(node, dict) or "$value" not in node:
                raise ValueError(f"Alias {{{ref}}} não aponta para um token")
            return resolve(root, node["$value"], seen + (ref,))
        return value
    if isinstance(value, dict):
        return {k: resolve(root, v, seen) for k, v in value.items()}
    if isinstance(value, list):
        return [resolve(root, v, seen) for v in value]
    return value


def tokens_in(root: dict[str, Any], group_path: str) -> dict[str, Any]:
    """Tokens (com $value resolvido) de um grupo, na ordem do arquivo."""
    try:
        group = get_node(root, group_path)
    except KeyError:
        return {}
    out: dict[str, Any] = {}
    for key, node in group.items():
        if key.startswith("$") or not isinstance(node, dict):
            continue
        if "$value" in node:
            out[key] = resolve(root, node["$value"])
    return out


# ---------- conversões ----------

def color_hex(v: Any) -> str:
    if isinstance(v, str):
        return v.upper()
    if isinstance(v, dict):
        if "hex" in v:
            return str(v["hex"]).upper()
        comps = v.get("components")
        if v.get("colorSpace", "srgb") == "srgb" and isinstance(comps, list) and len(comps) == 3:
            return "#" + "".join(f"{round(max(0, min(1, float(c))) * 255):02X}" for c in comps)
    raise ValueError(f"Cor sem hex/sRGB: {v!r}")


def color_css(v: Any) -> str:
    h = color_hex(v)
    alpha = v.get("alpha", 1) if isinstance(v, dict) else 1
    if alpha == 1:
        return h
    r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
    return f"rgba({r}, {g}, {b}, {alpha})"


def dim(v: Any) -> tuple[float, str]:
    if isinstance(v, dict):
        return float(v["value"]), str(v.get("unit", "px"))
    if isinstance(v, (int, float)):
        return float(v), "px"
    m = re.match(r"^(-?[\d.]+)([a-z%]*)$", str(v))
    if not m:
        raise ValueError(f"Dimensão inválida: {v!r}")
    return float(m.group(1)), m.group(2) or "px"


def num(x: float) -> str:
    return str(int(x)) if float(x).is_integer() else f"{x:g}"


def css_dim(v: Any) -> str:
    n, u = dim(v)
    return f"{num(n)}{u}"


def kebab(name: str) -> str:
    return re.sub(r"(?<=[a-z0-9])([A-Z])", r"-\1", name).lower()


def shadow_css(v: Any) -> str:
    layers = v if isinstance(v, list) else [v]
    parts = []
    for s in layers:
        inset = "inset " if s.get("inset") else ""
        parts.append(
            f"{inset}{css_dim(s['offsetX'])} {css_dim(s['offsetY'])} {css_dim(s['blur'])} "
            f"{css_dim(s.get('spread', 0))} {color_css(s['color'])}"
        )
    return ", ".join(parts)


# ---------- contraste WCAG ----------

def luminance(h: str) -> float:
    def ch(c: int) -> float:
        s = c / 255
        return s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4

    r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


# (frente, fundo, mínimo, descrição)
PAIRS = [
    ("text", "background", 4.5, "texto"),
    ("text", "surface", 4.5, "texto em surface"),
    ("text", "surfaceVariant", 4.5, "texto em surfaceVariant"),
    ("textMuted", "background", 4.5, "texto secundário"),
    ("textMuted", "surface", 4.5, "texto secundário em surface"),
    ("onPrimary", "primary", 4.5, "rótulo do botão primário"),
    ("primary", "background", 4.5, "link/texto primário"),
    ("primary", "surface", 3.0, "componente primário em surface"),
    ("border", "background", 3.0, "borda de input (1.4.11)"),
    ("border", "surface", 3.0, "borda de input em surface"),
    ("focus", "background", 3.0, "anel de foco"),
    ("focus", "surface", 3.0, "anel de foco em surface"),
    ("danger", "background", 4.5, "texto de erro"),
    ("danger", "surface", 4.5, "texto de erro em surface"),
    ("success", "background", 4.5, "texto de sucesso"),
    ("warning", "background", 4.5, "texto de atenção"),
    ("info", "background", 4.5, "texto informativo"),
]


def check(modes: dict[str, dict[str, str]]) -> bool:
    ok = True
    for mode, colors in modes.items():
        print(f"\n[{mode}]")
        for fg, bg, minimum, desc in PAIRS:
            if fg not in colors or bg not in colors:
                continue
            ratio = contrast(colors[fg], colors[bg])
            passed = ratio >= minimum
            ok &= passed
            mark = "OK  " if passed else "FALHA"
            print(f"  {mark} {ratio:5.2f}:1 (mín {minimum}) {fg} sobre {bg} — {desc}")
    return ok


# ---------- geração ----------

def build_modes(root: dict[str, Any]) -> dict[str, dict[str, str]]:
    modes = {}
    for mode in ("light", "dark"):
        toks = tokens_in(root, f"color.{mode}")
        if toks:
            modes[mode] = {k: color_hex(v) for k, v in toks.items()}
    if "light" not in modes:
        raise SystemExit("Arquivo sem grupo color.light")
    if "dark" in modes and set(modes["dark"]) != set(modes["light"]):
        diff = set(modes["dark"]) ^ set(modes["light"])
        raise SystemExit(f"color.light e color.dark precisam das mesmas chaves. Diferença: {sorted(diff)}")
    return modes


def generate_css(root: dict[str, Any], modes: dict[str, dict[str, str]]) -> str:
    lines = ["/* GERADO por build-tokens.py — não edite à mão; edite tokens.json. */", ":root {"]
    lines += [f"  --color-{kebab(k)}: {v};" for k, v in modes["light"].items()]
    lines.append("  color-scheme: light dark;")
    for k, v in tokens_in(root, "spacing").items():
        lines.append(f"  --space-{k}: {css_dim(v)};")
    for k, v in tokens_in(root, "radius").items():
        lines.append(f"  --radius-{kebab(k)}: {css_dim(v)};")
    fam = tokens_in(root, "font.family").get("base")
    if fam:
        stack = fam if isinstance(fam, list) else [fam]
        lines.append("  --font-family-base: " + ", ".join(f'"{f}"' if " " in f else f for f in stack) + ";")
    for k, t in tokens_in(root, "typography").items():
        n = kebab(k)
        lines.append(f"  --font-size-{n}: {num(dim(t['fontSize'])[0] / 16)}rem;")
        lines.append(f"  --line-height-{n}: {num(t['lineHeight'])};")
        lines.append(f"  --font-weight-{n}: {t['fontWeight']};")
    for k, v in tokens_in(root, "shadow").items():
        lines.append(f"  --shadow-{kebab(k)}: {shadow_css(v)};")
    for k, v in tokens_in(root, "motion").items():
        lines.append(f"  --duration-{kebab(k)}: {css_dim(v)};")
    for k, v in tokens_in(root, "size").items():
        lines.append(f"  --size-{kebab(k)}: {css_dim(v)};")
    lines.append("}")
    if "dark" in modes:
        dark = [f"  --color-{kebab(k)}: {v};" for k, v in modes["dark"].items()]
        lines += ["", "@media (prefers-color-scheme: dark) {", '  :root:not([data-theme="light"]) {']
        lines += ["  " + d for d in dark]
        lines += ["  }", "}", "", ':root[data-theme="dark"] {', *dark, "}"]
    bps = tokens_in(root, "breakpoint")
    if bps:
        lines += ["", "/* Breakpoints (CSS não aceita var() em @media):"]
        lines += [f"   {k}: {css_dim(v)}" for k, v in bps.items()]
        lines.append("*/")
    return "\n".join(lines) + "\n"


EXPO_SPACING = {"xs": "1", "sm": "2", "md": "4", "lg": "6", "xl": "8", "xxl": "12"}
EXPO_TYPO_ALIAS = {"title": "h3", "subtitle": "h4"}


def ts_obj(d: dict[str, Any], indent: int = 2) -> str:
    pad = " " * indent
    body = []
    for k, v in d.items():
        key = k if re.match(r"^[A-Za-z_$][\w$]*$", k) else json.dumps(k)
        if isinstance(v, dict):
            body.append(f"{pad}{key}: {ts_obj(v, indent + 2)},")
        else:
            body.append(f"{pad}{key}: {json.dumps(v)},")
    return "{\n" + "\n".join(body) + "\n" + " " * (indent - 2) + "}"


def generate_ts(root: dict[str, Any], modes: dict[str, dict[str, str]]) -> str:
    out = [
        "// GERADO por build-tokens.py — não edite à mão; edite tokens.json.",
        "// DESTINO: src/theme/tokens.ts — consumido por src/theme/index.ts (useTheme). Fonte: tokens/tokens.json",
        "",
        f"export const lightColors = {ts_obj(modes['light'])} as const;",
        "",
    ]
    if "dark" in modes:
        out += [f"export const darkColors = {ts_obj(modes['dark'])} as const;", ""]
    out += ["export type ThemeColors = { [K in keyof typeof lightColors]: string };", ""]

    space = {k: dim(v)[0] for k, v in tokens_in(root, "spacing").items()}
    out += [f"export const space = {ts_obj({k: int(v) if v.is_integer() else v for k, v in space.items()})} as const;", ""]
    expo_sp = {name: int(space[k]) for name, k in EXPO_SPACING.items() if k in space}
    out += ["/** Nomes compatíveis com o theme.ts da skill expo-app. */",
            f"export const spacing = {ts_obj(expo_sp)} as const;", ""]

    radius = {k: int(dim(v)[0]) for k, v in tokens_in(root, "radius").items()}
    if "full" in radius:
        radius["pill"] = radius["full"]
    out += [f"export const radius = {ts_obj(radius)} as const;", ""]

    typo: dict[str, Any] = {}
    for k, t in tokens_in(root, "typography").items():
        size = dim(t["fontSize"])[0]
        typo[k] = {
            "fontSize": int(size) if size.is_integer() else size,
            "lineHeight": int(round(size * float(t["lineHeight"]) / 4) * 4),  # grade de 4
            "fontWeight": str(t["fontWeight"]),
        }
    for alias, src in EXPO_TYPO_ALIAS.items():
        if src in typo and alias not in typo:
            typo[alias] = typo[src]
    out += [f"export const typography = {ts_obj(typo)} as const;", ""]

    shadows = {k: shadow_css(v) for k, v in tokens_in(root, "shadow").items()}
    if shadows:
        out += ["/** Strings para a prop boxShadow (RN 0.76+ / New Architecture) ou CSS. */",
                f"export const shadow = {ts_obj(shadows)} as const;", ""]

    motion = {k: int(dim(v)[0]) for k, v in tokens_in(root, "motion").items()}
    if motion:
        out += [f"export const motion = {ts_obj(motion)} as const;", ""]

    bps = {k: int(dim(v)[0]) for k, v in tokens_in(root, "breakpoint").items()}
    if bps:
        if "md" in bps:
            bps["tablet"] = bps["md"]
        if "lg" in bps:
            bps["desktop"] = bps["lg"]
        out += [f"export const breakpoints = {ts_obj(bps)} as const;", ""]

    native = tokens_in(root, "font.native")
    if native:
        fams = {w: (None if str(resolve(root, t)).strip().lower() in ("", "system") else str(resolve(root, t))) for w, t in native.items()}
        body = ",\n".join(f'  "{w}": {"undefined" if f is None else chr(34) + f + chr(34)}' for w, f in fams.items())
        out += ["/** Fonte carregada (expo-font) por peso; undefined = fonte do sistema. */",
                "export const fontFamilies: Record<string, string | undefined> = {\n" + body + ",\n};", ""]

    sizes = tokens_in(root, "size")
    if "touchTargetMin" in sizes:
        out += ["/** Área mínima de toque: 48 atende Android (48dp) e iOS (44pt). */",
                f"export const MIN_TOUCH_TARGET = {int(dim(sizes['touchTargetMin'])[0])};", ""]
    return "\n".join(out)


def main() -> None:
    p = argparse.ArgumentParser(description="Gera tokens.css/tokens.ts de um tokens.json DTCG.")
    p.add_argument("tokens", type=Path)
    p.add_argument("--css", type=Path, help="saída CSS")
    p.add_argument("--ts", type=Path, help="saída TypeScript")
    p.add_argument("--check", action="store_true", help="relatório de contraste WCAG (sai 1 se falhar)")
    a = p.parse_args()

    root = load(a.tokens)
    modes = build_modes(root)

    if a.css:
        a.css.parent.mkdir(parents=True, exist_ok=True)
        a.css.write_text(generate_css(root, modes), encoding="utf-8")
        print(f"CSS -> {a.css}")
    if a.ts:
        a.ts.parent.mkdir(parents=True, exist_ok=True)
        a.ts.write_text(generate_ts(root, modes), encoding="utf-8")
        print(f"TS  -> {a.ts}")
    if a.check or not (a.css or a.ts):
        if not check(modes):
            print("\nHá pares abaixo do mínimo WCAG 2.2 AA. Ajuste a paleta antes de usar.")
            sys.exit(1)
        print("\nTodos os pares conferidos passam no WCAG 2.2 AA.")


if __name__ == "__main__":
    main()
