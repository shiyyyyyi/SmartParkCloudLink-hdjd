# -*- coding: utf-8 -*-
"""Build the system design deliverable from the converted HLD template.

The source template is copied/converted into the document output directory as
``04_系统设计/_template_base.docx``. This script preserves the template's cover
tables, sections, page setup, headers, footers, and styles, then replaces the
template guidance body with SmartPark HLD content.
"""
from pathlib import Path
from copy import deepcopy

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DOC_ROOT = ROOT / "文档（项目相关的作业所需提交文档生成在这里）"
HLD_DIR = DOC_ROOT / "04_系统设计"
TEMPLATE = HLD_DIR / "_template_base.docx"
OUTPUT = HLD_DIR / "19组-程晓洋-系统设计.docx"
DIAGRAM_DIR = HLD_DIR / "_generated_hld_diagrams"

PROJECT_NAME = "AI-driven城市智慧停车管理与诱导系统"
GROUP = "第19组"
DOC_ID = "SmartPark-SD-HLD-001"
DATE = "2026.06.04"

MODULES = [
    ("M1", "路内停车位视觉检测", "P1", "模拟识别车位占用、违停和车牌，提供人工复核。", "roadside_detections, violations"),
    ("M2", "停车场数据联网接入", "P0", "接入路外停车场空位、价格和运营状态。", "parking_lots, sync_logs"),
    ("M3", "城市停车一张图", "P0", "汇总路内外停车资源，支持地图/列表查询和筛选。", "parking_lots, parking_spots"),
    ("M4", "停车诱导信息发布", "P1", "按空位与拥堵状态生成并发布诱导屏内容。", "guide_screens, publish_logs"),
    ("M5", "智能导航与车位预约", "P0", "推荐停车方案，锁定车位并管理预约状态。", "reservations, parking_spots"),
    ("M6", "车牌识别与无感支付", "P0", "模拟车牌入出场、自动计费和无感支付。", "vehicles, parking_orders"),
    ("M7", "停车行为大数据分析", "P1", "统计周转率、饱和度、停留时长和收入趋势。", "parking_orders, analytics_snapshots"),
    ("M8", "动态定价策略引擎", "P1", "按时段、热度和利用率计算价格系数。", "pricing_rules, pricing_logs"),
    ("M9", "共享停车管理平台", "P1", "支持共享车位发布、预约和收益统计。", "shared_spots, reservations"),
    ("M10", "充电车位智能管理", "P2", "管理充电车位、充电桩状态和异常占用。", "charging_piles, parking_spots"),
    ("M11", "违停自动抓拍与取证", "P2", "模拟违停抓拍、证据归档和审核处理。", "violations, review_logs"),
    ("M12", "长期停车月卡管理", "P2", "支持月卡申请、审批、续费和到期提醒。", "monthly_cards, vehicles"),
    ("M13", "车场运营管理后台", "P0", "承载车场、车位、订单、设备、价格和统计管理。", "parking_lots, parking_orders, devices"),
    ("M14", "车主移动端APP/小程序", "P0", "承载搜索、预约、支付、记录、寻车和优惠入口。", "users, vehicles, reservations"),
    ("M15", "反向寻车导航", "P1", "按车牌/订单定位车辆，生成楼层和路线指引。", "parking_orders, parking_spots"),
    ("M16", "设备运维管理平台", "P2", "管理摄像头、道闸、诱导屏、充电桩和告警。", "devices, maintenance_logs"),
    ("M17", "城市停车监管平台", "P1", "展示城市停车态势、违停、收费和政策评估。", "analytics_snapshots, violations"),
    ("M18", "商圈停车联合营销", "P2", "配置优惠活动、停车券核销和效果统计。", "marketing_campaigns, coupons"),
]


def set_run(run, size=10.5, bold=False, font="宋体", color=None):
    run.font.name = "Times New Roman"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), font)
    run.font.size = Pt(size)
    run.bold = bold
    if color:
        run.font.color.rgb = color


def set_cell(cell, text, bold=False, size=9.5):
    cell.text = ""
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    paragraph = cell.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER if len(str(text)) <= 14 else WD_ALIGN_PARAGRAPH.LEFT
    for part_index, part in enumerate(str(text).split("\n")):
        if part_index:
            paragraph.add_run().add_break()
        run = paragraph.add_run(part)
        set_run(run, size=size, bold=bold, font="黑体" if bold else "宋体")


def clear_paragraph(paragraph):
    p_pr = paragraph._p.pPr
    for child in list(paragraph._p):
        if child is not p_pr:
            paragraph._p.remove(child)


def set_paragraph(paragraph, text, bold=False, size=10.5, font="宋体"):
    clear_paragraph(paragraph)
    run = paragraph.add_run(text)
    set_run(run, size=size, bold=bold, font=font)


def rebuild_table(table, headers, rows):
    while len(table.rows) > 1:
        tr = table.rows[-1]._tr
        tr.getparent().remove(tr)
    while len(table.rows) < len(rows) + 1:
        table.add_row()
    for col, header in enumerate(headers):
        set_cell(table.cell(0, col), header, bold=True)
    for row_index, row in enumerate(rows, start=1):
        for col, value in enumerate(row):
            set_cell(table.cell(row_index, col), value, size=9)


def paragraph_text(element):
    return "".join(node.text or "" for node in element.iter(qn("w:t")))


def strip_template_body(doc):
    body = doc.element.body
    children = list(body)
    start = None
    for index, child in enumerate(children):
        if child.tag == qn("w:p") and "Keywords 关键词" in paragraph_text(child):
            start = index
            break
    if start is None:
        raise RuntimeError("Cannot locate HLD template body start")
    for child in children[start:]:
        if child.tag != qn("w:sectPr"):
            body.remove(child)


def add_heading(doc, text, level=1):
    paragraph = doc.add_paragraph(style=f"Heading {min(level, 4)}")
    paragraph.paragraph_format.keep_with_next = True
    run = paragraph.add_run(text)
    set_run(run, size={1: 16, 2: 14, 3: 12, 4: 11}.get(level, 10.5), bold=True, font="黑体")
    return paragraph


def add_para(doc, text="", bold=False):
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.line_spacing = 1.2
    paragraph.paragraph_format.space_after = Pt(5)
    run = paragraph.add_run(text)
    set_run(run, bold=bold)
    return paragraph


def add_bullet(doc, text):
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.left_indent = Inches(0.24)
    paragraph.paragraph_format.first_line_indent = Inches(-0.12)
    run = paragraph.add_run(f"• {text}")
    set_run(run)


def add_code(doc, lines):
    for line in lines:
        paragraph = doc.add_paragraph()
        paragraph.paragraph_format.space_after = Pt(0)
        run = paragraph.add_run(line)
        set_run(run, size=8.5, font="Consolas")


def add_table(doc, headers, rows):
    table = doc.add_table(rows=1, cols=len(headers))
    try:
        table.style = "Table Grid"
    except KeyError:
        pass
    for col, header in enumerate(headers):
        set_cell(table.cell(0, col), header, bold=True)
    for row in rows:
        cells = table.add_row().cells
        for col, value in enumerate(row):
            set_cell(cells[col], value, size=8.8)
    doc.add_paragraph()
    return table


def load_font(size=26, bold=False):
    candidates = [
        Path(r"C:\Windows\Fonts\simhei.ttf"),
        Path(r"C:\Windows\Fonts\simsun.ttc"),
        Path(r"C:\Windows\Fonts\msyh.ttc"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def make_diagram(name, title, boxes, arrows=None, size=(1300, 760)):
    DIAGRAM_DIR.mkdir(exist_ok=True)
    img = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(img)
    title_font = load_font(34, bold=True)
    body_font = load_font(22)
    small_font = load_font(18)
    draw.text((40, 28), title, fill=(30, 30, 30), font=title_font)
    for box in boxes:
        x, y, w, h, label, fill = box
        draw.rounded_rectangle((x, y, x + w, y + h), radius=8, fill=fill, outline=(60, 60, 60), width=2)
        lines = label.split("\n")
        for idx, line in enumerate(lines):
            draw.text((x + 18, y + 16 + idx * 30), line, fill=(20, 20, 20), font=body_font if idx == 0 else small_font)
    for arrow in arrows or []:
        x1, y1, x2, y2, label = arrow
        draw.line((x1, y1, x2, y2), fill=(40, 70, 120), width=3)
        # simple arrow head
        if x2 >= x1:
            draw.polygon([(x2, y2), (x2 - 12, y2 - 7), (x2 - 12, y2 + 7)], fill=(40, 70, 120))
        else:
            draw.polygon([(x2, y2), (x2 + 12, y2 - 7), (x2 + 12, y2 + 7)], fill=(40, 70, 120))
        if label:
            draw.text(((x1 + x2) // 2 - 45, (y1 + y2) // 2 - 28), label, fill=(40, 70, 120), font=small_font)
    out = DIAGRAM_DIR / f"{name}.png"
    img.save(out)
    return out


def create_diagrams():
    diagrams = {}
    diagrams["context"] = make_diagram(
        "01_context",
        "第0层：系统上下文图",
        [
            (80, 170, 210, 110, "车主\n搜索/预约/支付/寻车", (230, 242, 255)),
            (80, 420, 210, 110, "停车场管理员\n车场/车位/订单", (230, 242, 255)),
            (500, 250, 300, 190, "智慧停车管理与诱导系统\nVue3 + FastAPI + SQLite\n模拟AI/GIS/支付/设备", (235, 248, 238)),
            (990, 170, 210, 110, "交管监管人员\n态势/违停/政策", (255, 242, 224)),
            (990, 420, 210, 110, "外部能力\nAI/GIS/支付/设备", (255, 242, 224)),
        ],
        [
            (290, 225, 500, 315, "REST"),
            (290, 475, 500, 375, "管理"),
            (800, 315, 990, 225, "监管数据"),
            (800, 375, 990, 475, "模拟接口"),
        ],
    )
    diagrams["architecture"] = make_diagram(
        "02_architecture",
        "第1层：系统结构图",
        [
            (90, 130, 240, 110, "表现层\n车主端/管理端/监管端", (229, 241, 255)),
            (510, 130, 260, 110, "接口层\nRESTful JSON / Session", (238, 245, 255)),
            (940, 130, 250, 110, "业务服务层\n预约/计费/分析/运维", (237, 248, 239)),
            (300, 430, 260, 110, "数据访问层\nSQLAlchemy ORM", (255, 247, 220)),
            (740, 430, 260, 110, "数据层\nSQLite + 模拟数据", (255, 237, 229)),
        ],
        [
            (330, 185, 510, 185, "HTTP"),
            (770, 185, 940, 185, "路由"),
            (1020, 240, 560, 430, "服务调用"),
            (560, 485, 740, 485, "ORM"),
        ],
    )
    diagrams["activity"] = make_diagram(
        "03_activity",
        "业务流程活动图：车主停车闭环",
        [
            (80, 140, 180, 80, "搜索目的地", (230, 242, 255)),
            (310, 140, 190, 80, "查看一张图\n筛选车场", (230, 242, 255)),
            (550, 140, 190, 80, "预约车位\n锁定15分钟", (235, 248, 238)),
            (790, 140, 180, 80, "导航入场", (235, 248, 238)),
            (1030, 140, 190, 80, "车牌识别\n生成订单", (255, 247, 220)),
            (310, 430, 190, 80, "停车记录\n反向寻车", (255, 247, 220)),
            (550, 430, 190, 80, "出场计费", (255, 237, 229)),
            (790, 430, 180, 80, "模拟支付", (255, 237, 229)),
            (1030, 430, 190, 80, "释放车位\n统计沉淀", (235, 248, 238)),
        ],
        [
            (260, 180, 310, 180, ""),
            (500, 180, 550, 180, ""),
            (740, 180, 790, 180, ""),
            (970, 180, 1030, 180, ""),
            (1125, 220, 405, 430, "停车中"),
            (500, 470, 550, 470, ""),
            (740, 470, 790, 470, ""),
            (970, 470, 1030, 470, ""),
        ],
    )
    diagrams["sequence"] = make_diagram(
        "04_sequence",
        "核心时序图：预约与无感支付",
        [
            (70, 140, 180, 90, "车主端", (230, 242, 255)),
            (300, 140, 190, 90, "API网关", (238, 245, 255)),
            (540, 140, 220, 90, "预约服务", (235, 248, 238)),
            (810, 140, 220, 90, "订单/支付服务", (255, 247, 220)),
            (1080, 140, 170, 90, "数据库", (255, 237, 229)),
            (70, 420, 1180, 110, "1 查询车场 -> 2 创建预约 -> 3 锁定车位 -> 4 入场识别 -> 5 生成订单 -> 6 出场计费 -> 7 模拟支付 -> 8 释放车位", (250, 250, 250)),
        ],
        [
            (250, 185, 300, 185, "POST"),
            (490, 185, 540, 185, "reserve"),
            (760, 185, 1080, 185, "update spot"),
            (1030, 185, 1080, 185, "order"),
        ],
    )
    diagrams["er"] = make_diagram(
        "05_er",
        "概念模型：核心ER关系",
        [
            (90, 150, 190, 90, "users\n1:N vehicles/reservations/orders", (230, 242, 255)),
            (390, 150, 210, 90, "parking_lots\n1:N spots/devices/orders", (235, 248, 238)),
            (710, 150, 210, 90, "parking_spots\nstatus/type/location", (235, 248, 238)),
            (1010, 150, 190, 90, "reservations\nlock/confirm/cancel", (255, 247, 220)),
            (260, 430, 210, 90, "parking_orders\nentry/exit/pay", (255, 237, 229)),
            (570, 430, 210, 90, "violations/devices\nreview/maintenance", (255, 237, 229)),
            (880, 430, 220, 90, "pricing/marketing\nrules/coupons", (255, 247, 220)),
        ],
        [
            (280, 195, 390, 195, "管理"),
            (600, 195, 710, 195, "包含"),
            (920, 195, 1010, 195, "预约"),
            (1010, 240, 365, 430, "生成订单"),
            (600, 240, 675, 430, "设备/违停"),
            (470, 475, 880, 475, "计费/营销"),
        ],
    )
    return diagrams


def add_figure(doc, path, caption):
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run().add_picture(str(path), width=Inches(6.5))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = cap.add_run(caption)
    set_run(run, size=9, font="宋体")


def fill_front_matter(doc):
    for paragraph in doc.paragraphs:
        if "XX 软件系统概要设计说明书" in paragraph.text:
            set_paragraph(paragraph, f"{PROJECT_NAME}概要设计说明书", bold=True, size=22, font="黑体")
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            break

    cover = doc.tables[0]
    set_cell(cover.cell(0, 1), PROJECT_NAME, bold=True)
    set_cell(cover.cell(1, 0), "项目编号：SmartPark-19")
    set_cell(cover.cell(2, 0), "项目编号")
    set_cell(cover.cell(3, 0), "SmartPark-19")
    set_cell(cover.cell(3, 1), "V1.0")
    set_cell(cover.cell(3, 2), DOC_ID)

    approval = doc.tables[1]
    set_cell(approval.cell(0, 1), "程晓洋（SA）")
    set_cell(approval.cell(0, 3), DATE)
    set_cell(approval.cell(1, 1), "程子浩、丁梓钊")
    set_cell(approval.cell(1, 3), DATE)
    set_cell(approval.cell(2, 1), "第19组")
    set_cell(approval.cell(2, 3), DATE)

    rebuild_table(
        doc.tables[2],
        ["Date / 日期", "Revision Version / 修订版本", "CR ID /Defect ID / CR/ Defect号", "Sec No. / 修改章节", "Change Description / 修改描述", "Author / 作者"],
        [
            ("2026.06.03", "V0.1", "N/A", "1-2", "根据SRS V1.0完成HLD简介、系统上下文和系统结构设计", "程晓洋（SA）"),
            ("2026.06.03", "V0.2", "N/A", "2.2", "补充系统架构图、业务流程活动图和模块分解", "全员"),
            ("2026.06.04", "V0.3", "DR-01~DR-06", "2-4", "补充核心业务时序图、接口定义、ER图、表结构和核心界面说明", "程晓洋（SA）"),
            ("2026.06.04", "V1.0", "N/A", "全部", "按概要设计模板形成正式提交版", "第19组"),
        ],
    )
    rebuild_table(
        doc.tables[3],
        ["Abbreviations缩略语", "Full spelling 英文全名", "Chinese explanation 中文解释"],
        [
            ("HLD", "High-Level Design", "概要设计"),
            ("SRS", "Software Requirement Specification", "需求规格说明书"),
            ("SA", "System Architect", "系统架构师"),
            ("REST", "Representational State Transfer", "表现层状态转移接口风格"),
            ("ORM", "Object Relational Mapping", "对象关系映射"),
            ("ERD", "Entity Relationship Diagram", "实体关系图"),
            ("SPA", "Single Page Application", "单页应用"),
            ("P0/P1/P2", "Priority Level", "需求优先级"),
        ],
    )


def update_toc(doc):
    toc_lines = [
        "目    录",
        "1 简介",
        "1.1 目的",
        "1.2 范围",
        "1.2.1 软件名称",
        "1.2.2 软件功能",
        "1.2.3 软件应用",
        "1.3 参考资料",
        "2 概要设计",
        "2.1 第0层设计描述",
        "2.1.1 软件系统上下文定义",
        "2.1.2 设计思路",
        "2.2 第1层设计描述",
        "2.2.1 系统结构",
        "2.2.1.1 系统结构描述",
        "2.2.1.2 业务流程说明",
        "2.2.2 分解描述",
        "2.2.3 接口描述",
        "3 数据结构/数据库设计",
        "3.1 概念模型",
        "3.2 数据库表设计",
        "3.3 存储过程设计",
        "3.4 视图设计",
        "3.5 触发器设计",
        "3.6 函数设计",
        "3.7 基础数据配置",
        "4 界面设计",
        "4.1 车主端核心界面",
        "4.2 管理端核心界面",
        "4.3 监管端核心界面",
        "5 出错处理设计",
    ]
    start = None
    end = None
    for i, para in enumerate(doc.paragraphs):
        if para.text.strip().startswith("目"):
            start = i
        if start is not None and "Keywords 关键词" in para.text:
            end = i
            break
    if start is None:
        return
    if end is None:
        end = min(len(doc.paragraphs), start + 40)
    for offset, line in enumerate(toc_lines):
        index = start + offset
        if index >= end:
            break
        para = doc.paragraphs[index]
        set_paragraph(para, line, bold=(offset == 0), font="黑体" if offset == 0 else "宋体")
    for index in range(start + len(toc_lines), end):
        set_paragraph(doc.paragraphs[index], "")


def add_body(doc):
    diagrams = create_diagrams()

    add_heading(doc, "Keywords 关键词：", 1)
    add_para(doc, "智慧停车；概要设计；系统上下文；模块分解；时序图；接口设计；数据库设计；界面设计")
    add_heading(doc, "Abstract 摘    要：", 1)
    add_para(
        doc,
        "本文档按照《概要设计说明书》模板编写，基于《功能需求规格说明书 SRS V1.0》对AI-driven城市智慧停车管理与诱导系统进行高层设计。文档覆盖系统上下文、架构设计、业务流程、模块分解、接口、数据库结构、核心界面和出错处理，为后续编码实现与测试提供依据。"
    )
    add_heading(doc, "List of abbreviations 缩略语清单：", 1)
    add_para(doc, "缩略语见前置表格。")

    add_heading(doc, "1 简介", 1)
    add_heading(doc, "1.1 目的", 2)
    add_para(doc, "本文档描述AI-driven城市智慧停车管理与诱导系统的概要设计，明确系统边界、总体架构、模块拆分、核心业务流程、接口和数据结构。预期读者包括项目成员、系统架构师、开发人员、测试人员和课程评审人员。")
    add_heading(doc, "1.2 范围", 2)
    add_heading(doc, "1.2.1 软件名称", 3)
    add_para(doc, PROJECT_NAME)
    add_heading(doc, "1.2.2 软件功能", 3)
    add_para(doc, "系统覆盖SRS中的18个一级业务模块。P0模块形成车主停车闭环与运营管理闭环，P1模块增强监管、分析、诱导和共享能力，P2模块通过模拟数据与预留接口表达充电、违停、月卡、设备运维和联合营销等扩展场景。")
    add_heading(doc, "1.2.3 软件应用", 3)
    add_para(doc, "软件应用于城市停车资源查询、车位预约、停车场运营、违停监管、设备运维和商圈营销等教学实训场景。实训环境下不依赖真实AI模型、GIS地图、支付通道和硬件设备，而是通过模拟接口、状态字段、初始数据和可视化页面完成业务闭环。")
    add_heading(doc, "1.3 参考资料", 2)
    for item in ["《功能需求规格说明书 SRS V1.0》", "《软件开发计划 V1.0》", "《项目立项报告 V1.0》", "教师发布的第三周项目任务作业与每日任务截图（2026.06.01-2026.06.04）"]:
        add_bullet(doc, item)

    add_heading(doc, "2 概要设计", 1)
    add_heading(doc, "2.1 第0层设计描述", 2)
    add_heading(doc, "2.1.1 软件系统上下文定义", 3)
    add_para(doc, "系统外部实体包括车主、停车场管理员、交管监管人员和外部模拟能力。车主通过车主端完成查询、预约、支付和寻车；管理员通过管理端维护车场、车位、订单、设备、价格和营销；监管人员查看汇总态势、违停和政策评估；AI识别、GIS、支付、道闸、诱导屏和充电桩在实训阶段以模拟服务接入。")
    add_figure(doc, diagrams["context"], "图2-1 软件系统上下文图")
    add_heading(doc, "2.1.2 设计思路", 3)
    add_para(doc, "系统采用前后端分离B/S结构。前端使用Vue3、Element Plus、Vite、ECharts组织车主端、管理端和监管端页面；后端使用FastAPI提供RESTful JSON接口；数据库使用SQLite和SQLAlchemy ORM；外部能力采用适配器模式预留服务接口，当前实现使用模拟数据和状态面板。")
    add_para(doc, "设计原则包括：模块边界对应SRS的18个一级业务模块；注册登录、基础CRUD、订单和统计图表作为支撑能力归入相关模块；核心闭环优先实现；高风险外部依赖采用可替换模拟服务。")

    add_heading(doc, "2.2 第1层设计描述", 2)
    add_heading(doc, "2.2.1 系统结构", 3)
    add_heading(doc, "2.2.1.1 系统结构描述", 4)
    add_figure(doc, diagrams["architecture"], "图2-2 系统结构图")
    add_table(
        doc,
        ["层次", "组成", "职责"],
        [
            ("表现层", "车主端、管理端、监管端", "提供搜索、预约、支付、运营、监管等页面"),
            ("接口层", "FastAPI Router、Session中间件", "统一鉴权、参数校验、错误码和JSON响应"),
            ("业务服务层", "预约、订单、分析、定价、运维等服务", "承载状态机、计费规则、统计聚合和模拟服务编排"),
            ("数据访问层", "SQLAlchemy ORM", "封装模型、事务、查询和数据一致性约束"),
            ("数据层", "SQLite、初始化数据、日志表", "保存业务状态、配置、订单和审计数据"),
        ],
    )
    add_heading(doc, "2.2.1.2 业务流程说明", 4)
    add_para(doc, "核心业务流程以车主停车闭环为主线：查询停车资源、预约锁定车位、导航入场、车牌识别生成订单、停车期间支持寻车、出场计费、模拟支付、释放车位并沉淀运营统计。管理端与监管端围绕该闭环读取和维护车场、订单、设备、违停、价格和分析数据。")
    add_figure(doc, diagrams["activity"], "图2-3 车主停车闭环活动图")
    add_heading(doc, "2.2.2 分解描述", 3)
    add_para(doc, "系统模块分解严格对应需求规格说明书中的18个一级业务模块，按P0/P1/P2安排实现优先级。")
    add_table(doc, ["模块ID", "模块名称", "优先级", "功能摘要", "主要数据对象"], MODULES)
    add_heading(doc, "2.2.2.1 P0核心闭环模块", 4)
    add_para(doc, "P0模块包括M2、M3、M5、M6、M13、M14，负责停车场数据接入、一张图查询、预约、车牌识别计费、运营后台和车主移动端，是课程演示必须稳定闭合的主路径。")
    add_heading(doc, "2.2.2.1.1 智能导航与车位预约", 4)
    add_para(doc, "类设计：ReservationService负责预约创建、取消、确认和过期释放；SpotService负责车位状态校验与锁定；LotService负责车场查询和推荐；Reservation模型保存预约状态、锁定到期时间和关联车位。")
    add_para(doc, "功能实现说明：车主端提交预约请求后，接口层校验登录态与参数，预约服务检查车位可用性，写入reservations并将parking_spots.status置为locked。超时任务扫描expire_at释放未确认预约。")
    add_figure(doc, diagrams["sequence"], "图2-4 预约与无感支付核心时序图")
    add_heading(doc, "2.2.2.1.2 车牌识别与无感支付", 4)
    add_para(doc, "类设计：PlateRecognitionAdapter模拟车牌识别结果；OrderService负责订单生成、计费和状态更新；PaymentAdapter模拟扣款；ParkingOrder模型记录入场、出场、金额和支付状态。")
    add_para(doc, "功能实现说明：车辆入场时系统根据车牌与预约状态生成订单；出场时按费率、免费时长和动态定价规则计算金额；模拟支付成功后订单完成并释放车位。")
    add_heading(doc, "2.2.2.2 P1/P2增强与扩展模块", 4)
    add_para(doc, "P1模块重点服务监管、分析和运营提效，P2模块采用模拟数据、状态字段和预留接口完成扩展表达。所有模块都通过统一API、统一错误码和统一数据字典与核心闭环联动。")
    add_heading(doc, "2.2.3 接口描述", 3)
    add_para(doc, "接口统一采用HTTP/1.1 + RESTful JSON，统一响应格式为 {code, msg, data}。code=0表示成功，400表示参数错误，401表示未登录，403表示无权限，404表示资源不存在，500表示服务端异常。")
    add_table(
        doc,
        ["接口组", "方法与路径", "说明", "关联模块"],
        [
            ("停车资源", "GET /api/lots/search", "按位置、区域、价格、空位查询停车资源", "M2/M3"),
            ("预约", "POST /api/reservations", "创建预约并锁定车位15分钟", "M5"),
            ("预约确认", "PUT /api/reservations/{id}/confirm", "车辆到场后确认预约", "M5/M6"),
            ("车牌事件", "POST /api/license-plate/events", "模拟入出场车牌识别事件", "M6"),
            ("支付", "POST /api/payments/mock", "模拟无感支付并更新订单", "M6"),
            ("诱导屏", "POST /api/guide-screens/publish", "生成并发布诱导内容", "M4"),
            ("动态定价", "POST /api/pricing-rules/evaluate", "按规则计算价格系数", "M8"),
            ("监管态势", "GET /api/regulation/dashboard", "查询城市停车监管汇总", "M17"),
            ("设备运维", "PUT /api/devices/{id}/status", "更新设备状态和告警处理结果", "M16"),
            ("营销核销", "POST /api/coupons/redeem", "核销商圈停车优惠", "M18"),
        ],
    )

    add_heading(doc, "3 数据结构/数据库设计", 1)
    add_heading(doc, "3.1 概念模型", 2)
    add_para(doc, "核心概念模型围绕用户、车辆、停车场、车位、预约、订单、设备、违停证据、定价规则、营销活动和统计快照展开。用户与车辆、预约、订单存在一对多关系；停车场与车位、设备、订单存在一对多关系；预约确认后生成订单；订单、违停、定价和营销数据进入统计快照供运营和监管使用。")
    add_figure(doc, diagrams["er"], "图3-1 核心实体关系图")
    add_heading(doc, "3.2 数据库表设计", 2)
    add_table(
        doc,
        ["表名", "用途", "关键字段"],
        [
            ("users", "用户与角色权限", "id, username, password_hash, phone, role, created_at"),
            ("vehicles", "车牌与车辆信息", "id, user_id, plate_number, vehicle_type, default_flag"),
            ("parking_lots", "停车场基础信息和接入状态", "id, name, address, region, total_spots, rate_per_hour, status"),
            ("parking_spots", "车位状态、类型和位置", "id, lot_id, spot_number, floor, zone, status, spot_type"),
            ("reservations", "预约锁定、确认、取消和过期", "id, user_id, spot_id, status, expire_at, confirm_at"),
            ("parking_orders", "入出场订单、计费和支付", "id, user_id, spot_id, plate_number, entry_time, exit_time, amount, status"),
            ("shared_spots", "共享车位发布与收益", "id, owner_id, spot_id, available_start, available_end, price, status"),
            ("charging_piles", "充电桩和充电车位状态", "id, spot_id, power_kw, status, fault_type, last_update"),
            ("violations", "违停证据与审核", "id, plate_number, location, evidence_url, review_status, violation_at"),
            ("monthly_cards", "月卡申请、审批和续费", "id, user_id, plate_number, lot_id, valid_to, status"),
            ("devices", "设备台账、在线状态和运维日志", "id, lot_id, device_type, status, firmware_version, last_heartbeat"),
            ("guide_screens", "诱导屏位置和发布内容", "id, location, related_lot_id, content, publish_status"),
            ("pricing_rules", "动态定价规则", "id, lot_id, period, factor, reason, enabled"),
            ("marketing_campaigns", "商圈营销活动", "id, name, merchant, rule_desc, valid_to, status"),
            ("analytics_snapshots", "统计指标快照", "id, lot_id, metric_type, metric_value, snapshot_at"),
        ],
    )
    add_heading(doc, "3.3 存储过程设计", 2)
    add_para(doc, "实训阶段使用SQLite，不设计数据库存储过程。预约超时释放、统计聚合和价格计算由后端服务层定时任务或接口逻辑实现。")
    add_heading(doc, "3.4 视图设计", 2)
    add_table(
        doc,
        ["视图名", "用途", "字段口径"],
        [
            ("v_lot_realtime_status", "停车一张图实时展示", "车场、区域、总车位、空余车位、价格、更新时间"),
            ("v_order_revenue_daily", "运营收入日报", "日期、车场、订单数、收入、平均停车时长"),
            ("v_regulation_summary", "监管汇总", "区域、车场数、总车位、占用率、违停数"),
        ],
    )
    add_heading(doc, "3.5 触发器设计", 2)
    add_para(doc, "不使用数据库触发器。订单完成、预约取消、支付成功等状态变更由服务层显式更新，并写入操作日志，避免演示环境中隐式逻辑难以追踪。")
    add_heading(doc, "3.6 函数设计", 2)
    add_para(doc, "主要函数包括calculate_fee(order, pricing_rule)、release_expired_reservations(now)、aggregate_lot_status(lot_id)、evaluate_pricing_factor(lot_id, time_range)和mask_regulation_data(records)。")
    add_heading(doc, "3.7 基础数据配置", 2)
    add_para(doc, "基础数据包括示例停车场、车位、车辆、管理员账号、设备、诱导屏、价格规则、营销活动和历史订单。初始化脚本应保证车主端、运营端和监管端都有可演示数据。")

    add_heading(doc, "4 界面设计", 1)
    add_heading(doc, "4.1 车主端核心界面", 2)
    add_table(
        doc,
        ["界面", "核心元素", "交互说明"],
        [
            ("首页/搜索", "目的地搜索框、附近车场卡片、空位/价格标签", "输入目的地后查询停车一张图并按距离与空位排序"),
            ("车场详情", "车场信息、车位网格、预约按钮、收费规则", "选择可预约车位后进入预约确认"),
            ("预约确认", "预约车位、倒计时、取消/到场确认按钮", "锁定15分钟，超时自动释放"),
            ("出场支付", "订单金额、停车时长、模拟支付按钮", "支付成功后完成订单并释放车位"),
            ("反向寻车", "车牌输入、楼层区域、路线文本", "按进行中订单生成寻车指引"),
        ],
    )
    add_heading(doc, "4.2 管理端核心界面", 2)
    add_table(
        doc,
        ["界面", "核心元素", "交互说明"],
        [
            ("运营概览", "车位利用率、收入、订单、异常卡片", "查看车场经营状态并进入明细"),
            ("数据接入", "停车场接入配置、同步状态、离线告警", "维护路外停车场模拟接口"),
            ("诱导发布", "诱导屏列表、发布内容、发布状态", "生成并模拟发布诱导信息"),
            ("动态定价", "价格规则表、时段系数、发布记录", "配置并审计价格策略"),
            ("设备运维", "设备列表、故障等级、处理记录", "处理摄像头、道闸、诱导屏和充电桩状态"),
        ],
    )
    add_heading(doc, "4.3 监管端核心界面", 2)
    add_table(
        doc,
        ["界面", "核心元素", "交互说明"],
        [
            ("监管大屏", "区域占用率、供需趋势、违停数量", "展示城市级汇总数据"),
            ("违停审核", "证据图片、车牌、位置、复核状态", "审核模拟违停取证记录"),
            ("政策评估", "价格、饱和度、投诉/违停趋势", "辅助评估停车政策效果"),
        ],
    )

    add_heading(doc, "5 出错处理设计", 1)
    add_table(
        doc,
        ["错误场景", "处理策略", "用户/管理员提示"],
        [
            ("未登录或权限不足", "接口返回401/403，前端跳转登录或提示无权限", "请先登录/无权执行该操作"),
            ("预约车位已被占用", "事务内重新校验车位状态，不创建预约", "车位已不可预约，请重新选择"),
            ("预约超时", "定时任务释放车位并更新预约状态", "预约已超时，车位已释放"),
            ("模拟支付失败", "订单保持待支付，允许重试或人工处理", "支付失败，请重试或联系管理员"),
            ("设备/诱导屏离线", "保留最近一次有效状态并生成告警", "设备离线，已记录告警"),
            ("外部模拟接口异常", "降级使用缓存/初始数据，记录日志", "数据暂不可用，展示最近一次结果"),
            ("监管数据敏感", "汇总脱敏后展示，不暴露个人手机号和完整车牌", "仅展示汇总统计"),
        ],
    )
    add_para(doc, "日志策略：关键操作记录操作者、时间、对象、原状态、新状态和结果；异常日志记录接口路径、错误码和处理方式，便于测试阶段复盘。")


def build():
    if not TEMPLATE.exists():
        raise FileNotFoundError(f"Missing template base: {TEMPLATE}")
    doc = Document(str(TEMPLATE))
    fill_front_matter(doc)
    update_toc(doc)
    strip_template_body(doc)
    add_body(doc)
    doc.save(OUTPUT)
    print(f"[保存] {OUTPUT}")


if __name__ == "__main__":
    build()
