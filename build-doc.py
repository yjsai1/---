"""Build the share document: taste-skill (plugin) + design-taste-frontend (skill) on DeepSeek Harness."""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

INK = RGBColor(0x0D, 0x2A, 0x1C)
MUTED = RGBColor(0x5F, 0x6B, 0x64)
BODY = RGBColor(0x1E, 0x2A, 0x24)
ACCENT = "F6E016"
SURFACE = "F2F2F0"

CN = "微软雅黑"
LATIN = "Segoe UI"
MONO = "Consolas"

doc = Document()

# ---------- page ----------
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.4)
sec.top_margin = Cm(2.2)
sec.bottom_margin = Cm(2.0)

CONTENT_W = 21 - 4.8  # cm

# w:noProof must sit before these siblings in a w:rPr, per the schema order
_AFTER_NOPROOF = {
    "w:snapToGrid", "w:vanish", "w:webHidden", "w:color", "w:spacing", "w:w", "w:kern",
    "w:position", "w:sz", "w:szCs", "w:highlight", "w:u", "w:effect", "w:bdr", "w:shd",
    "w:fitText", "w:vertAlign", "w:rtl", "w:cs", "w:em", "w:lang", "w:eastAsianLayout",
    "w:specVanish", "w:oMath",
}


def add_no_proof(rpr):
    """Turn off spell/grammar squiggles for this run without touching its text."""
    if rpr is None or rpr.find(qn("w:noProof")) is not None:
        return
    no_proof = OxmlElement("w:noProof")
    for child in list(rpr):
        if child.tag in {qn(t) for t in _AFTER_NOPROOF}:
            child.addprevious(no_proof)
            return
    rpr.append(no_proof)


def silence_proofing():
    """Set noProof in docDefaults so inherited runs stay clean in Word."""
    styles_el = doc.styles.element
    doc_defaults = styles_el.find(qn("w:docDefaults"))
    if doc_defaults is None:
        return
    rpr_default = doc_defaults.find(qn("w:rPrDefault"))
    if rpr_default is None:
        return
    rpr = rpr_default.find(qn("w:rPr"))
    if rpr is None:
        rpr = OxmlElement("w:rPr")
        rpr_default.append(rpr)
    add_no_proof(rpr)
    lang = rpr.find(qn("w:lang"))
    if lang is None:
        lang = OxmlElement("w:lang")
        rpr.append(lang)
    lang.set(qn("w:val"), "zh-CN")
    lang.set(qn("w:eastAsia"), "zh-CN")


def set_run(run, size=10.5, color=BODY, bold=False, mono=False, italic=False):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    name = MONO if mono else LATIN
    run.font.name = name
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:ascii"), name)
    rfonts.set(qn("w:hAnsi"), name)
    rfonts.set(qn("w:eastAsia"), CN if not mono else CN)
    add_no_proof(rpr)
    lang = rpr.find(qn("w:lang"))
    if lang is None:
        lang = OxmlElement("w:lang")
        rpr.append(lang)
    lang.set(qn("w:val"), "zh-CN")
    lang.set(qn("w:eastAsia"), "zh-CN")


def shade(paragraph_or_cell, hex_color):
    el = paragraph_or_cell._element
    pr = el.get_or_add_pPr() if hasattr(el, "get_or_add_pPr") else el.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    pr.append(shd)


def bottom_border(paragraph, hex_color, size=8):
    pPr = paragraph._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(size))
    bottom.set(qn("w:space"), "6")
    bottom.set(qn("w:color"), hex_color)
    pbdr.append(bottom)
    pPr.append(pbdr)


def para(text="", size=10.5, color=BODY, bold=False, space_after=8, space_before=0,
         align=None, line=1.55, mono=False, indent_first=False):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_after = Pt(space_after)
    pf.space_before = Pt(space_before)
    pf.line_spacing = line
    if align:
        p.alignment = align
    if indent_first:
        pf.first_line_indent = Pt(size * 2)
    if text:
        r = p.add_run(text)
        set_run(r, size=size, color=color, bold=bold, mono=mono)
    return p


def h1(text, num=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(22)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    if num:
        r = p.add_run(num + "  ")
        set_run(r, size=15, color=MUTED, bold=True)
    r = p.add_run(text)
    set_run(r, size=15, color=INK, bold=True)
    bottom_border(p, ACCENT, 10)
    return p


def h2(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    set_run(r, size=11.5, color=INK, bold=True)
    return p


def bullet(text, size=10.5, color=BODY):
    p = doc.add_paragraph(style="List Boulet" if False else "List Bullet")
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.45
    p.paragraph_format.left_indent = Cm(0.6)
    r = p.add_run(text)
    set_run(r, size=size, color=color)
    return p


def code_block(lines):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    cell = table.cell(0, 0)
    cell.width = Cm(CONTENT_W)
    shade(cell, SURFACE)
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.25
    for i, line in enumerate(lines):
        r = p.add_run(line)
        set_run(r, size=8.8, color=RGBColor(0x1F, 0x2B, 0x25), mono=True)
        if i < len(lines) - 1:
            r.add_break()
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def figure(path, caption, width_cm=CONTENT_W, space_before=6):
    if not os.path.exists(path):
        raise SystemExit("missing figure: " + path)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(path, width=Cm(width_cm))
    c = doc.add_paragraph()
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c.paragraph_format.space_after = Pt(12)
    r = c.add_run(caption)
    set_run(r, size=8.5, color=MUTED)


def table(headers, rows, widths, header_fill="EBEBEB", font_size=9.2):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    t.autofit = False
    hdr = t.rows[0].cells

    def keep_row(row, header=False):
        tr_pr = row._tr.get_or_add_trPr()
        cant = OxmlElement("w:cantSplit")
        tr_pr.append(cant)
        if header:
            th = OxmlElement("w:tblHeader")
            tr_pr.append(th)

    keep_row(t.rows[0], header=True)
    for i, h in enumerate(headers):
        hdr[i].width = Cm(widths[i])
        shade(hdr[i], header_fill)
        p = hdr[i].paragraphs[0]
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.space_before = Pt(1)
        r = p.add_run(h)
        set_run(r, size=font_size, color=INK, bold=True)
    for row in rows:
        cells = t.add_row().cells
        keep_row(t.rows[-1])
        for i, val in enumerate(row):
            cells[i].width = Cm(widths[i])
            p = cells[i].paragraphs[0]
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.line_spacing = 1.3
            r = p.add_run(val)
            set_run(r, size=font_size, color=BODY, mono=(i == 0 and False))
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


# ---------- footer with page number ----------
footer_p = sec.footer.paragraphs[0]
footer_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
r = footer_p.add_run("design-taste-frontend on DeepSeek Harness  ·  2026-11-05  ·  ")
set_run(r, size=8, color=MUTED)
fld = OxmlElement("w:fldSimple")
fld.set(qn("w:instr"), "PAGE")
run_el = OxmlElement("w:r")
t_el = OxmlElement("w:t")
t_el.text = "1"
run_el.append(t_el)
fld.append(run_el)
footer_p._p.append(fld)

# ================= 封面 =================
p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(56)
p.paragraph_format.space_after = Pt(10)
r = p.add_run("在 DeepSeek Harness 上\n使用 design-taste-frontend")
set_run(r, size=27, color=INK, bold=True)
p.paragraph_format.line_spacing = 1.18

p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(6)
r = p.add_run("一个插件（taste-skill）与一个 skill 的分享，附一次完整实跑记录")
set_run(r, size=12, color=MUTED)

p = doc.add_paragraph()
bottom_border(p, ACCENT, 18)
p.paragraph_format.space_after = Pt(18)

meta = [
    ("日期", "2026 年 11 月 5 日"),
    ("环境", "Windows 11 · DeepSeek Harness（Web GUI，127.0.0.1:58917）"),
    ("工具链", "Node 24.19 · Edge headless · Open-Meteo 预报 API"),
    ("产物", "下一班雨（index.html / styles.css / app.js / app-data.js）+ 本文档"),
]
for k, v in meta:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(k + "　")
    set_run(r, size=9.5, color=MUTED)
    r = p.add_run(v)
    set_run(r, size=9.5, color=BODY)

doc.add_paragraph().paragraph_format.space_after = Pt(20)

para("这份文档写给两类人：想在自己的 DSH 里装一套「能验收」的前端美术指导的人，"
     "以及想知道这个 skill 到底怎么跑、值不值得用的人。文档里的每一张截图都来自同一次真实运行——"
     "用 design-taste-frontend 从零做了「下一班雨」的落地页，数据取自 Open-Meteo 的实时降水预报。",
     size=10.5, line=1.7)

para("需要说明的是：「下一班雨」是一个演示品牌，用来展示 skill 的输出；页面上的城市、街道、"
     "降水数字是真实的，品牌名与按钮去处需要换成真实信息才能上线。", size=9.5, color=MUTED, line=1.6)

# ================= 一、结论 =================
h1("结论先讲", "一")

para("三句话说完这份分享：", space_after=4)
bullet("插件是分发单元，skill 是能力本体。taste-skill 把所有东西打包成一份可安装的清单；真正干活的是它里面的 design-taste-frontend。")
bullet("装一次就够。DSH 监视 %USERPROFILE%\\.dsh\\skills，把 skill 目录拷进去，下一轮对话即可生效，不用重启。")
bullet("页面质量来自三步闭环：抽方向（不自由发挥）→ 真实浏览器测量（不靠感觉）→ 打开截图再改（最多三轮）。")

# ================= 二、插件 =================
h1("插件：taste-skill", "二")

para("taste-skill 是一个仓库形态的插件包（MIT 许可，版本 2.1.5，github.com/Leonxlnx/taste-skill）。"
     "它同时提供两份插件清单：Claude Code 用的 .claude-plugin/marketplace.json，"
     "Codex 用的 .codex-plugin/plugin.json；两份清单都指向同一个 skills/taste-skill。"
     "也就是说，这里的「插件」不是新的运行时，而是一个打包与安装的约定：清单 + skill + 脚本 + 参考库 + 数据。")

table(
    ["包内路径", "作用", "规模"],
    [
        [".claude-plugin/marketplace.json", "Claude Code 插件市场清单：名称、版本、skills、作者、许可", "1 个文件"],
        [".codex-plugin/plugin.json", "Codex 插件清单，含显示名、分类与三条默认提示", "1 个文件"],
        ["skills/taste-skill/SKILL.md", "skill 本体：10 步流程、房屋规则、技法法则", "40 KB"],
        ["scripts/", "draw（抽方向）、assets（找图）、lint、inspect（真实浏览器测量）、scenes", "5 个脚本"],
        ["references/", "文案、字体、配色、版式、图像、动效、场景、点评、规律等参考", "12 篇"],
        ["library/", "方向、首屏、分节、字体系统、配色、摄影、动效数据（由脚本读取）", "JSON 数据"],
        ["assets/", "基础 CSS、滚动场景、图表、app 样式，可直接用于页面", "复用件"],
    ],
    widths=[5.4, 8.4, 2.4],
)

para("在 DSH 上，「安装」是文件层面的：skill 目录是 %USERPROFILE%\\.dsh\\skills，"
     "每个子目录一个 skill。仓库自带更新脚本 update-design-taste-frontend.ps1，先 git pull，"
     "再把 skills\\taste-skill 覆盖到 %USERPROFILE%\\.dsh\\skills\\design-taste-frontend。"
     "下图是安装完成后 DSH 的 skill 目录（终端输出原文）。", space_before=4)

figure("shots/term-install.png", "图 1｜安装完成后 DSH 的 skill 目录：design-taste-frontend 与它带来的脚本、参考库（终端输出原文）", width_cm=14)

# ================= 三、skill =================
h1("Skill：design-taste-frontend", "三")

para("它解决的是一种很具体的问题：模型生成的页面「哪都没错，也没有任何决定」——居中的大标题、"
     "上面一行小标签、三个图标卡、一些细线、一句等宽字体的注释。这个 skill 用四种方式取代这套默认值。")

h2("1. 抽方向，人来选")
para("draw.mjs 从研究过的方向库里发三个候选，你根据「哪一种构图能承载这个主体独有的东西」选一个；"
     "脚本随后发它的字体系统、配色、首屏蓝图与每一节的版式。不自由发挥，是为了避开「品类的平均脸」。")

h2("2. 想法来自主体")
para("先清点八到十二件只属于这个客户的事（名字的含义、门牌与街道、数字、材料、时辰、印刷物），"
     "想法从这张清单里长出来，而不是从品类里长出来。判断标准是一句话：把最近的竞品放进这句话，"
     "如果依然成立，这个想法就是品类的，不是客户的。")

h2("3. 无装饰的房屋规则，用真实浏览器量")
para("渐变、投影、细线、图标卡、等宽小标签、奶油底配赤陶色等一律禁止。lint.mjs 扫源码，"
     "inspect.mjs 用本机 Chrome/Edge 在 1440、768、390 三个宽度上量：标题几行、字号、字体是否真的加载、"
     "对比度、页边距是否相等、有没有超过半屏的空白段、有多少元素真的在动。")

h2("4. 看自己做了什么")
para("三个宽度的截图、十四项评审、Awwwards 加权打分；改影响最大的三处，再看一遍，最多三轮。"
     "通过检查器只是地板，不是分数。")

table(
    ["命令", "作用"],
    [
        ["draw.mjs --sector … --brief … --options 3", "发三个方向候选，选出要用的那一个"],
        ["draw.mjs … --direction <id>", "发完整方向单：首屏、分节、字体、配色、动效、参考站点"],
        ["assets.mjs \"<关键词>\"（--get / --credits）", "在开放馆藏里找主体世界的真实图片，下载并记许可"],
        ["lint.mjs .  ·  inspect.mjs index.html", "静态检查 + 真实浏览器测量，截图写到 .taste-skill/inspect/"],
    ],
    widths=[6.6, 9.6],
)

para("适用：落地页、产品页、应用界面（用 --app 走另一套规则）、以及「改版/评审」（先记录 before）。"
     "不适用：纯后端；单组件微调（可跳过抽方向）；没有任何真实内容可写的页面——它会先逼你写论点。", space_before=2)

# ================= 四、实跑 =================
h1("一次完整实跑", "四")

para("下面是把这套流程走完的实际记录：从空目录到一张能截图的页面，中间发生了什么。")

steps = [
    ("读 brief 与项目", "目录是空的；确定主体是「给城市通勤者的 15 分钟降水预报」。影像现状：没有自有素材，"
     "但开放馆藏可用（大都会艺术博物馆，公有领域）。"),
    ("写论点", "把页面写成「主张 + 证据」的清单：一张表，两个答案（带不带伞、几点出门），共五段。没有主张的段落直接删。"),
    ("抽方向", "以 consumer-app 品类、五段结构抽三个方向，选中 product-performs（软件最可信的时候，是它在替你干活）。"
     "方向单给出：字体 Switzer、配色 Bottle ink + Yellow、首屏「黄底舞台上的真实控件」。seed 394207075。"),
    ("找想法", "填一句话：「在这个页面上，广州一个区的 15 分钟降水格，变成一张发车时刻表。」"
     "可操作的那一件事：切区、切小时，表会重排。"),
    ("写文案与构建", "先写完整中文文案再写标签。页面单文件结构（HTML + CSS + JS），数据由 build-data.mjs 从三个坐标的"
     " Open-Meteo 响应生成，写进 app-data.js——断网也能看，页面底部写明更新时间。"),
    ("过门槛", "lint 先报 2 处阴影，改成下划线；inspect 先报 6 个 FAIL（没有图片、没有动效、偏离中心、文字贴边……），逐条修到 0 FAIL。"),
    ("看截图再改", "打开三视口截图，改了三处：首屏右下空块、功能段只占左半、图片超出页边距。"),
    ("动效", "快门式揭幕（clip-path）、分段入场（标题→文字→图，70ms 错开）、控件反馈、一张缓慢漂移的照片；"
     "prefers-reduced-motion 全部降级为静态。"),
]
for i, (title, body) in enumerate(steps, start=1):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.keep_with_next = True
    r = p.add_run("%02d  " % i)
    set_run(r, size=8.5, color=MUTED, bold=True)
    r = p.add_run(title)
    set_run(r, size=10.5, color=INK, bold=True)
    para(body, size=10, space_after=2)

doc.add_page_break()
para("方向单的实际输出（截取前半：方向、想法、构图、字体、配色、图像策略）：", space_before=0, space_after=2)
figure("shots/term-draw-top.png", "图 2｜draw.mjs 打印的方向单（真实输出，截取前 1,150 像素）")

doc.add_page_break()
para("过程中检查器实际拦下来的问题，以及改法：", space_before=0, space_after=4)
table(
    ["检查器报的", "真实原因", "改法"],
    [
        ["few-pictures / still-page / 0 张图", "HTML 被编码问题弄坏，整页以无样式渲染", "重写 HTML（UTF-8），重新跑"],
        ["off-centre / edge-text", "图片带负边距「满幅出血」，文字贴到屏幕边", "取消出血，图片回到页边距内"],
        ["hero-void（38% 空块）", "首屏舞台按蓝图从 42% 开始，右上留空", "舞台提到 26%，并把 12 格条塞进控件，让它被下缘裁切"],
        ["lopsided（右半 775px 空）", "功能段是单列列表", "改成 7/5 双栏：左边模块，右边吸附的规格面板"],
        ["blank-gap（1036px 空段）", "图片在截取时还处于「未揭示」状态", "把 IntersectionObserver 换成滚动驱动的揭示，保证滚到就出现"],
    ],
    widths=[5.2, 6.4, 4.6],
)

para("最后一条命令的输出（节选：测量结果与结论）：", space_before=6, space_after=2)
figure("shots/term-inspect.png", "图 3｜inspect.mjs 的测量结果：0 FAIL、1 WARN（真实输出）", width_cm=15.6)

para("唯一的 WARN 是「没有视频」。assets.mjs 的视频检索在本次环境里连不上任何来源"
     "（Wikimedia、Internet Archive 均超时，NASA 无结果），页面改用一张缓慢漂移的照片作为「会动的画面」，"
     "这一条按实际情况保留。", size=9.5, color=MUTED)

# ================= 五、成品 =================
doc.add_page_break()
h1("成品：三个视口", "五")

para("下面六张桌面截图对应页面的六个段落，最后两张是平板与手机。所有截图都由本机 Edge 无头模式在真实渲染后截取，"
     "不是设计稿。", space_after=6)

figure("shots/desktop-fold.jpg", "图 4｜首屏（1440 × 900）：左边一句话，右边黄底舞台上是一块能点的真实控件", width_cm=13.2)
figure("shots/desktop-features.jpg", "图 5｜功能段：左边四个模块，右边是吸附的规格面板", width_cm=13.2)

doc.add_page_break()
figure("shots/desktop-board.jpg", "图 6｜降水时刻表：一小时一行，点开的那行整块变黄", width_cm=13.2, space_before=0)
figure("shots/desktop-how.jpg", "图 7｜钉住的演示面板：左侧滚动的三段话，右侧面板换状态", width_cm=13.2)

doc.add_page_break()
figure("shots/desktop-faq.jpg", "图 8｜常见问题：手风琴，左边一张 1860 年代的雨", width_cm=13.2, space_before=0)
figure("shots/tablet-fold.jpg", "图 9｜平板 768：同一套内容换成单栏，控件仍然是真的", width_cm=9.6)

doc.add_page_break()
figure("shots/mobile-fold.jpg", "图 10｜手机 390：标题两行、控件铺满、右侧裁切而不是缩小", width_cm=7.2, space_before=0)

# ================= 六、安装 =================
h1("安装、更新、卸载", "六")

para("在 DSH 里，skill 就是目录；安装、更新、卸载都是文件操作，不需要重启。", space_after=4)

code_block([
    "# 更新已安装的 taste-skill（仓库 clone 在 ~\\.dsh\\skill-sources\\taste-skill）",
    "powershell -ExecutionPolicy Bypass -File \"$env:USERPROFILE\\.dsh\\skill-sources\\update-design-taste-frontend.ps1\"",
    "",
    "# 卸载：删掉目录即可",
    "Remove-Item -Recurse -Force \"$env:USERPROFILE\\.dsh\\skills\\design-taste-frontend\"",
    "",
    "# 在项目根目录里跑（不装依赖）",
    "node \"$env:USERPROFILE\\.dsh\\skills\\design-taste-frontend\\scripts\\draw.mjs\" --list sectors",
    "node \"$env:USERPROFILE\\.dsh\\skills\\design-taste-frontend\\scripts\\inspect.mjs\" index.html",
])

para("依赖：Node 22 以上；本机装有 Chrome、Edge 或 Chromium（检查器要用它跑真实浏览器）；"
     "assets.mjs 需要联网。页面本身不依赖任何框架，构建产物就是几个静态文件。", size=9.5, color=MUTED)

# ================= 七、边界 =================
h1("边界与注意事项", "七")

bullet("0 FAIL 只是地板。它说明没有测量到被禁的东西，不说明页面好看；分数要看截图与评审。")
bullet("图片必须真实。本次四张图全部来自大都会艺术博物馆的公有领域藏品，页面与本文都署名；没有任何占位图或假截图。")
bullet("数字必须可追溯。页面上的每个降水数字都来自 data/ 下的 Open-Meteo 响应，由 build-data.mjs 生成；页脚写明更新时间。")
bullet("中文字体需要处理。Switzer 没有中文字形，页面回退到系统中文字体；要严格控制外观，请换成含中文的等价字体。")
bullet("网络会影响取图。本次 Openverse、Wikimedia Commons 的视频与图片检索均不可达，只有大都会博物馆可用；换环境结果可能不同。")
bullet("演示内容要替换。「下一班雨」是虚构品牌，按钮指向锚点；上线前需要接真实信息与真实数据源。")

# ================= 附录 =================
h1("附录", "八")

h2("A. 截图清单")
table(
    ["文件", "尺寸", "内容"],
    [
        ["term-install.png", "880 × 311", "DSH skill 目录（终端输出）"],
        ["term-draw-top.png", "1236 × 1150", "方向单输出（截取）"],
        ["term-inspect.png", "1236 × 575", "检查器结果：0 FAIL"],
        ["desktop-fold.jpg", "1440 × 900", "首屏"],
        ["desktop-features.jpg", "1440 × 900", "功能段"],
        ["desktop-board.jpg", "1440 × 900", "降水时刻表"],
        ["desktop-how.jpg", "1440 × 900", "钉住的演示面板"],
        ["desktop-faq.jpg", "1440 × 900", "常见问题"],
        ["tablet-fold.jpg", "768 × 1024", "平板首屏"],
        ["mobile-fold.jpg", "390 × 844", "手机首屏"],
    ],
    widths=[4.6, 3.6, 7.6],
)

h2("B. 图片来源与许可")
para("四张历史图片均为大都会艺术博物馆 Open Access 藏品，公有领域（CC0），页面与本文均已署名。", size=9.5, color=MUTED, space_after=4)
table(
    ["作品", "作者 / 年代", "出处"],
    [
        ["《御茶之水之雨》", "歌川国芳，19 世纪中叶", "The Met, 51084"],
        ["美国制伞（兽首伞柄）", "美国制，1888 年", "The Met, 158043"],
        ["Street in Kadhin; Shanghai", "约翰·汤普森，约 1869 年", "The Met, 289373"],
        ["[Broadway in the Rain]", "爱德华·安东尼，约 1860 年代", "The Met, 262762"],
    ],
    widths=[5.2, 6.0, 4.8],
)

h2("C. 本次生成的文件")
table(
    ["文件", "说明"],
    [
        ["index.html / styles.css / app.js", "页面本体：结构、样式、交互（Tab 切区、时刻表展开、滚动揭示）"],
        ["build-data.mjs → app-data.js", "把三个坐标的 Open-Meteo 响应整理成窗口表与逐时表"],
        ["data/gz-*.json", "原始预报响应（天河、越秀、海珠），可复核"],
        ["capture.mjs / shot.mjs / term-shots.mjs", "截图脚本：分节截图、整页截图、终端输出渲染"],
    ],
    widths=[6.4, 10.8],
)

para("— 完 —", size=9, color=MUTED, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=16)

out = os.environ.get("DOCX_OUT", "design-taste-frontend-on-dsh.docx")
silence_proofing()
doc.save(out)
print("saved", out, os.path.getsize(out), "bytes")
