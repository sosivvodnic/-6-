#!/usr/bin/env python3
"""Generate a diploma-style Word document for ParkPass appendices.

The script uses only Python's standard library and writes a minimal DOCX
package directly, so it can run in lightweight environments without extra
dependencies.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "проект диплом" / "parkpass-diploma-appendices.docx"

NS_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_CP = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
NS_DC = "http://purl.org/dc/elements/1.1/"
NS_DCTERMS = "http://purl.org/dc/terms/"
NS_DCMITYPE = "http://purl.org/dc/dcmitype/"
NS_XSI = "http://www.w3.org/2001/XMLSchema-instance"


def cm(value: float) -> int:
    return round(value * 567)


def text(value: str) -> str:
    return escape(value, {'"': "&quot;"})


def r(
    value: str,
    *,
    bold: bool = False,
    italic: bool = False,
    size: int = 28,
    font: str = "Times New Roman",
    color: str | None = None,
) -> str:
    props = [
        f'<w:rFonts w:ascii="{font}" w:hAnsi="{font}" w:eastAsia="{font}" w:cs="{font}"/>',
        f'<w:sz w:val="{size}"/>',
        f'<w:szCs w:val="{size}"/>',
    ]
    if bold:
        props.append("<w:b/><w:bCs/>")
    if italic:
        props.append("<w:i/><w:iCs/>")
    if color:
        props.append(f'<w:color w:val="{color}"/>')

    escaped = text(value)
    preserve = ' xml:space="preserve"' if value != value.strip() or "  " in value else ""
    return f"<w:r><w:rPr>{''.join(props)}</w:rPr><w:t{preserve}>{escaped}</w:t></w:r>"


def p(
    runs: str | Sequence[str],
    *,
    style: str = "BodyText",
    align: str | None = None,
    first_line: bool | None = None,
    spacing_before: int | None = None,
    spacing_after: int | None = None,
    line: int | None = None,
    shade: str | None = None,
    keep_next: bool = False,
    page_break_before: bool = False,
) -> str:
    if isinstance(runs, str):
        runs_xml = r(runs)
    else:
        runs_xml = "".join(runs)

    props = [f'<w:pStyle w:val="{style}"/>']
    if align:
        props.append(f'<w:jc w:val="{align}"/>')
    if first_line is not None:
        props.append(f'<w:ind w:firstLine="{cm(1.25) if first_line else 0}"/>')
    if spacing_before is not None or spacing_after is not None or line is not None:
        attrs = []
        if spacing_before is not None:
            attrs.append(f'w:before="{spacing_before}"')
        if spacing_after is not None:
            attrs.append(f'w:after="{spacing_after}"')
        if line is not None:
            attrs.append(f'w:line="{line}" w:lineRule="auto"')
        props.append(f"<w:spacing {' '.join(attrs)}/>")
    if shade:
        props.append(f'<w:shd w:val="clear" w:color="auto" w:fill="{shade}"/>')
    if keep_next:
        props.append("<w:keepNext/>")
    if page_break_before:
        props.append("<w:pageBreakBefore/>")

    return f"<w:p><w:pPr>{''.join(props)}</w:pPr>{runs_xml}</w:p>"


def page_break() -> str:
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def code_block(lines: Iterable[str]) -> str:
    return "".join(
        p(
            [r(line, size=20, font="Consolas")],
            style="CodeBlock",
            first_line=False,
            spacing_before=0,
            spacing_after=0,
            line=240,
            shade="F2F2F2",
        )
        for line in lines
    )


def cell(content: str, *, width: int, header: bool = False) -> str:
    fill = "D9EAF7" if header else "FFFFFF"
    weight = "bold" if header else "single"
    props = (
        f'<w:tcW w:w="{width}" w:type="dxa"/>'
        f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>'
        '<w:tcMar><w:top w:w="80" w:type="dxa"/><w:left w:w="100" w:type="dxa"/>'
        '<w:bottom w:w="80" w:type="dxa"/><w:right w:w="100" w:type="dxa"/></w:tcMar>'
    )
    run = r(content, bold=header, size=24)
    paragraph = p([run], style="TableText", first_line=False, spacing_after=0, line=240)
    return f"<w:tc><w:tcPr>{props}</w:tcPr>{paragraph}</w:tc>"


def table(headers: Sequence[str], rows: Sequence[Sequence[str]], widths: Sequence[int]) -> str:
    borders = (
        '<w:tblBorders><w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
        '<w:left w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
        '<w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
        '<w:right w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
        '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/></w:tblBorders>'
    )
    grid = "".join(f'<w:gridCol w:w="{width}"/>' for width in widths)
    rows_xml = [
        "<w:tr>"
        + "".join(cell(value, width=width, header=True) for value, width in zip(headers, widths))
        + "</w:tr>"
    ]
    for row in rows:
        rows_xml.append(
            "<w:tr>"
            + "".join(cell(value, width=width) for value, width in zip(row, widths))
            + "</w:tr>"
        )
    return (
        "<w:tbl><w:tblPr><w:tblStyle w:val=\"TableGrid\"/>"
        '<w:tblW w:w="0" w:type="auto"/>'
        f"{borders}</w:tblPr><w:tblGrid>{grid}</w:tblGrid>{''.join(rows_xml)}</w:tbl>"
    )


def appendix_header(letter: str, title: str, kind: str = "справочное") -> str:
    return "".join(
        [
            p(
                [r(f"ПРИЛОЖЕНИЕ {letter}", bold=True, size=28)],
                style="AppendixLabel",
                align="center",
                first_line=False,
                spacing_after=120,
                keep_next=True,
            ),
            p(
                [r(f"({kind})", size=28)],
                style="AppendixKind",
                align="center",
                first_line=False,
                spacing_after=240,
                keep_next=True,
            ),
            p(
                [r(title, bold=True, size=28)],
                style="AppendixTitle",
                align="center",
                first_line=False,
                spacing_after=360,
            ),
        ]
    )


def document_body() -> str:
    request_lines = [
        "{",
        '  "guests": 2,',
        '  "totalAmount": 298',
        "}",
    ]
    response_lines = [
        "HTTP/1.1 201 Created",
        "{",
        '  "id": "...",',
        '  "qrCode": "PP-1718640000000",',
        '  "status": "paid",',
        '  "totalAmount": 298',
        "}",
    ]
    index_rows = [
        ("city", "быстрый поиск парков по городу"),
        ("category", "фильтрация парков по тематической категории"),
        ("rating", "сортировка и выборка популярных парков"),
        ("park_id", "связь билетов, отзывов и заказов с парком"),
        ("user_id", "выборка пользовательских заказов и активности"),
        ("visit_date", "поиск посещений и бронирований по дате"),
    ]
    screenshot_rows = [
        ("Рисунок Д.1", "Главная страница ParkPass", "Главный экран приложения"),
        ("Рисунок Д.2", "Каталог парков", "/parks"),
        ("Рисунок Д.3", "Themed-лендинг Star Wars", "/worlds/star-wars"),
        ("Рисунок Д.4", "Многошаговый checkout", "Оформление заказа"),
        ("Рисунок Д.5", "Личный кабинет", "/account"),
        ("Рисунок Д.6", "Административная панель", "/admin"),
        ("Рисунок Д.7", "Результат автотестов npm test", "13 passed"),
    ]

    parts = [
        p(
            [r("Приложения к дипломной работе", bold=True, size=32)],
            style="Title",
            align="center",
            first_line=False,
            spacing_before=1200,
            spacing_after=360,
        ),
        p(
            [r("Веб-приложение ParkPass", bold=True, size=28)],
            style="AppendixTitle",
            align="center",
            first_line=False,
            spacing_after=240,
        ),
        p(
            [r("ASTANA POLYTECHNIC · ИС-23-19б · 2026", size=26)],
            style="BodyText",
            align="center",
            first_line=False,
            spacing_after=720,
        ),
        p(
            "Документ подготовлен для включения в дипломную работу и содержит оформленные приложения: пример ответа API, описание схемы базы данных и перечень скриншотов интерфейса.",
            first_line=True,
        ),
        page_break(),
        appendix_header("В", "Пример HTTP-запроса и ответа API", "обязательное"),
        p(
            "В данном приложении приведен пример обмена данными при оформлении заказа в системе ParkPass. Формат ответа демонстрирует успешное создание оплаченного билета и формирование QR-кода.",
            first_line=True,
        ),
        p([r("Тело запроса", bold=True)], style="BodyText", first_line=False, keep_next=True),
        code_block(request_lines),
        p([r("Ответ сервера", bold=True)], style="BodyText", first_line=False, keep_next=True, spacing_before=240),
        code_block(response_lines),
        page_break(),
        appendix_header("Г", "Схема базы данных"),
        p(
            [
                r("См. файл "),
                r("database/schema.sql", italic=True),
                r(". Схема базы данных включает 7 таблиц, 4 ENUM-типа и набор индексов, обеспечивающих быстрый доступ к основным сущностям системы."),
            ],
            first_line=True,
        ),
        p([r("Перечень основных индексов", bold=True)], style="BodyText", first_line=False, keep_next=True),
        table(("Поле", "Назначение индекса"), index_rows, (2400, 6400)),
        page_break(),
        appendix_header("Д", "Скриншоты интерфейса"),
        p(
            "В приложении перечислены экранные формы, отражающие основные пользовательские и административные сценарии веб-приложения ParkPass.",
            first_line=True,
        ),
        table(("Обозначение", "Наименование", "Раздел / маршрут"), screenshot_rows, (2200, 4300, 2300)),
        p(
            [r("© 2026 ParkPass · Дипломный проект · ASTANA POLYTECHNIC · ИС-23-19б", italic=True, size=24)],
            style="FooterText",
            align="center",
            first_line=False,
            spacing_before=720,
        ),
    ]

    sect = (
        "<w:sectPr>"
        '<w:pgSz w:w="11906" w:h="16838"/>'
        f'<w:pgMar w:top="{cm(2)}" w:right="{cm(1.5)}" w:bottom="{cm(2)}" '
        f'w:left="{cm(3)}" w:header="{cm(1.25)}" w:footer="{cm(1.25)}" w:gutter="0"/>'
        '<w:cols w:space="708"/>'
        '<w:docGrid w:linePitch="360"/>'
        "</w:sectPr>"
    )
    return "".join(parts) + sect


def content_types() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>
"""


def root_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
"""


def document_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>
</Relationships>
"""


def document_xml() -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="{NS_W}" xmlns:r="{NS_R}">
  <w:body>{document_body()}</w:body>
</w:document>
"""


def styles_xml() -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="{NS_W}">
  <w:docDefaults>
    <w:rPrDefault>
      <w:rPr>
        <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="Times New Roman" w:cs="Times New Roman"/>
        <w:sz w:val="28"/>
        <w:szCs w:val="28"/>
      </w:rPr>
    </w:rPrDefault>
    <w:pPrDefault>
      <w:pPr>
        <w:spacing w:line="360" w:lineRule="auto" w:after="160"/>
        <w:ind w:firstLine="{cm(1.25)}"/>
      </w:pPr>
    </w:pPrDefault>
  </w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:qFormat/>
    <w:rPr>
      <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="Times New Roman" w:cs="Times New Roman"/>
      <w:sz w:val="28"/>
      <w:szCs w:val="28"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="BodyText">
    <w:name w:val="Body Text"/>
    <w:basedOn w:val="Normal"/>
    <w:pPr>
      <w:spacing w:line="360" w:lineRule="auto" w:after="160"/>
      <w:ind w:firstLine="{cm(1.25)}"/>
      <w:jc w:val="both"/>
    </w:pPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Title">
    <w:name w:val="Diploma Title"/>
    <w:basedOn w:val="Normal"/>
    <w:pPr>
      <w:jc w:val="center"/>
      <w:spacing w:line="360" w:lineRule="auto" w:after="360"/>
    </w:pPr>
    <w:rPr><w:b/><w:bCs/><w:sz w:val="32"/><w:szCs w:val="32"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="AppendixLabel">
    <w:name w:val="Appendix Label"/>
    <w:basedOn w:val="Normal"/>
    <w:pPr><w:jc w:val="center"/><w:keepNext/></w:pPr>
    <w:rPr><w:b/><w:bCs/><w:sz w:val="28"/><w:szCs w:val="28"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="AppendixKind">
    <w:name w:val="Appendix Kind"/>
    <w:basedOn w:val="Normal"/>
    <w:pPr><w:jc w:val="center"/><w:keepNext/></w:pPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="AppendixTitle">
    <w:name w:val="Appendix Title"/>
    <w:basedOn w:val="Normal"/>
    <w:pPr><w:jc w:val="center"/><w:spacing w:after="360"/></w:pPr>
    <w:rPr><w:b/><w:bCs/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="CodeBlock">
    <w:name w:val="Code Block"/>
    <w:basedOn w:val="Normal"/>
    <w:pPr>
      <w:spacing w:line="240" w:lineRule="auto" w:after="0"/>
      <w:ind w:firstLine="0" w:left="240"/>
    </w:pPr>
    <w:rPr>
      <w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:eastAsia="Consolas" w:cs="Consolas"/>
      <w:sz w:val="20"/>
      <w:szCs w:val="20"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="TableText">
    <w:name w:val="Table Text"/>
    <w:basedOn w:val="Normal"/>
    <w:pPr>
      <w:spacing w:line="240" w:lineRule="auto" w:after="0"/>
      <w:ind w:firstLine="0"/>
    </w:pPr>
    <w:rPr><w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="FooterText">
    <w:name w:val="Footer Text"/>
    <w:basedOn w:val="Normal"/>
    <w:pPr><w:jc w:val="center"/><w:ind w:firstLine="0"/></w:pPr>
    <w:rPr><w:i/><w:iCs/><w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr>
  </w:style>
  <w:style w:type="table" w:styleId="TableGrid">
    <w:name w:val="Table Grid"/>
    <w:tblPr>
      <w:tblBorders>
        <w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>
        <w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>
        <w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>
        <w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>
        <w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>
        <w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>
      </w:tblBorders>
    </w:tblPr>
  </w:style>
</w:styles>
"""


def settings_xml() -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:w="{NS_W}">
  <w:zoom w:percent="100"/>
  <w:defaultTabStop w:val="708"/>
  <w:characterSpacingControl w:val="doNotCompress"/>
  <w:compat/>
</w:settings>
"""


def core_xml() -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="{NS_CP}" xmlns:dc="{NS_DC}" xmlns:dcterms="{NS_DCTERMS}" xmlns:dcmitype="{NS_DCMITYPE}" xmlns:xsi="{NS_XSI}">
  <dc:title>Приложения к дипломной работе ParkPass</dc:title>
  <dc:subject>Дипломный проект</dc:subject>
  <dc:creator>ParkPass</dc:creator>
  <cp:lastModifiedBy>ParkPass</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>
"""


def app_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Microsoft Word</Application>
  <DocSecurity>0</DocSecurity>
  <ScaleCrop>false</ScaleCrop>
  <Company>ASTANA POLYTECHNIC</Company>
  <LinksUpToDate>false</LinksUpToDate>
  <SharedDoc>false</SharedDoc>
  <HyperlinksChanged>false</HyperlinksChanged>
  <AppVersion>16.0000</AppVersion>
</Properties>
"""


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(OUTPUT, "w", ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", content_types())
        docx.writestr("_rels/.rels", root_rels())
        docx.writestr("word/_rels/document.xml.rels", document_rels())
        docx.writestr("word/document.xml", document_xml())
        docx.writestr("word/styles.xml", styles_xml())
        docx.writestr("word/settings.xml", settings_xml())
        docx.writestr("docProps/core.xml", core_xml())
        docx.writestr("docProps/app.xml", app_xml())
    print(f"Generated {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
