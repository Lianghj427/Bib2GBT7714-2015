"""
BibTeX to GB/T 7714-2015 转换核心模块.

支持 6 种主要文献类型: 期刊[J], 图书[M], 会议[C], 学位论文[D], 专利[P], 电子文献[EB/OL].
中英文自动区分: 中文用「等」, 英文用「et al」.
纯逻辑层, 不依赖 Gradio, 可独立使用或 CLI 调用.
"""

import csv
import datetime
import os
import re

import bibtexparser

# ---------------------------------------------------------------------------
# 加载中文姓氏表
# ---------------------------------------------------------------------------
_csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "data", "Chinese_surname.csv")
CHINESE_SURNAMES: set[str] = set()
with open(_csv_path, "r", encoding="utf-8") as _f:
    for _row in csv.reader(_f):
        if _row:
            CHINESE_SURNAMES.add(_row[0].strip().upper())

# ---------------------------------------------------------------------------
# BibTeX 类型 → GB/T 7714 类型代码
# ---------------------------------------------------------------------------
TYPE_MAP: dict[str, str] = {
    'article':        'J',
    'book':           'M',
    'booklet':        'M',
    'conference':     'C',
    'inbook':         'M',
    'incollection':   'M',
    'inproceedings':  'C',
    'manual':         'R',
    'mastersthesis':  'D',
    'phdthesis':      'D',
    'proceedings':    'C',
    'techreport':     'R',
    'unpublished':    'C',
    'collection':     'G',
    'newspaper':      'N',
    'standard':       'S',
    'patent':         'P',
    'database':       'DB',
    'software':       'CP',
    'online':         'EB',
    'archive':        'A',
    'map':            'CM',
    'dataset':        'DS',
    'misc':           'Z',
}

# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------

def _extract_surname(author_str: str) -> str:
    """从作者字符串中提取姓氏."""
    a = author_str.strip()
    if ',' in a:
        return a.split(',')[0].strip()
    parts = a.strip().split()
    if len(parts) >= 2:
        return parts[-1].strip().replace('.', '')
    return parts[0].strip().replace('.', '') if parts else ''


def _is_chinese(surname: str) -> bool:
    """判断姓氏是否为中文."""
    return surname.upper() in CHINESE_SURNAMES


def _detect_language(raw_authors: list[str]) -> str:
    """通过作者姓氏判断文献语言. 任一作者为中文姓氏则判定为中文文献."""
    for a in raw_authors:
        if _is_chinese(_extract_surname(a)):
            return 'zh'
    return 'en'


def _capitalize_title(title: str) -> str:
    """首字母大写, 其余保持原样."""
    if not title:
        return ''
    return title[0].upper() + title[1:]

# ---------------------------------------------------------------------------
# 作者格式化
# ---------------------------------------------------------------------------

def format_authors(author_field: str, lang: str = 'en') -> str:
    """将 BibTeX author 字段格式化为 GB/T 7714 作者列表.

    Args:
        author_field: BibTeX 的 author 字段值 (e.g. "Foerster, Jakob and Farquhar, Gregory")
        lang: 'zh' 中文文献, 'en' 英文文献.

    Returns:
        格式化后的作者字符串. >3人时中文用「等」, 英文用「et al」.
    """
    if not author_field:
        return ''

    # 按 and 分割 (全词匹配, 大小写不敏感)
    raw_authors = [a.strip() for a in re.split(r'\band\b', author_field, flags=re.IGNORECASE)]
    if not raw_authors:
        return ''

    # --- 逐个规范化姓名 ---
    normalized: list[str] = []
    for author in raw_authors:
        if not author:
            continue
        if ',' in author:
            # 格式: "Surname, Given Names"
            surname = author.split(',')[0].strip().upper()
            given_raw = author.split(',')[1].strip().lower()
        else:
            # 格式: "Given Names Surname"
            parts = author.strip().split()
            if len(parts) >= 2:
                surname = ' '.join(parts[1:]).upper().replace('.', '')
                given_raw = parts[0].lower()
            else:
                surname = parts[0].upper().replace('.', '')
                given_raw = ''

        given_raw = given_raw.replace('.', '').strip()

        if _is_chinese(surname):
            # 中文作者: 保留完整名, 首字母大写
            given = given_raw.capitalize() if given_raw else ''
        else:
            # 英文作者: 名缩写为首字母
            given_parts = [p.capitalize() for p in given_raw.split() if p]
            given = ' '.join([p[0] for p in given_parts]) if given_parts else ''

        full = f"{surname} {given}".strip()
        normalized.append(full)

    # --- 应用 >3 人规则 ---
    if len(normalized) > 3:
        if lang == 'zh':
            return ', '.join(normalized[:3]) + ', 等'
        else:
            return ', '.join(normalized[:3]) + ', et al'

    return ', '.join(normalized)


# ---------------------------------------------------------------------------
# 各类型格式化器
# ---------------------------------------------------------------------------

def _fmt_journal(entry: dict, authors: str, title: str, _lang: str) -> str:
    """期刊文章 [J]: 作者. 题名[J]. 刊名, 年, 卷(期): 页码."""
    result = f"{authors}. {title}[J]."
    journal = entry.get('journal', '')
    if journal:
        result += f" {journal}"
    year = entry.get('year', '')
    if year:
        result += f", {year}"
    volume = entry.get('volume', '')
    if volume:
        result += f", {volume}"
    number = entry.get('number', '')
    if number:
        result += f"({number})"
    pages = entry.get('pages', '')
    if pages:
        result += f": {pages}"
    result += '.'
    doi = entry.get('doi', '')
    if doi:
        result += f" doi:{doi}."
    return result


def _fmt_book(entry: dict, authors: str, title: str, _lang: str) -> str:
    """图书 [M]: 作者. 书名[M]. 出版地: 出版社, 年: 页码."""
    result = f"{authors}. {title}[M]."
    address = entry.get('address', '')
    publisher = entry.get('publisher', '')
    if address and publisher:
        result += f" {address}: {publisher}"
    elif publisher:
        result += f" {publisher}"
    year = entry.get('year', '')
    if year:
        result += f", {year}"
    pages = entry.get('pages', '')
    if pages:
        result += f": {pages}"
    result += '.'
    return result


def _fmt_conference(entry: dict, authors: str, title: str, _lang: str) -> str:
    """会议论文 [C]: 作者. 题名[C]//会议名. 出版地: 出版者, 年: 页码."""
    result = f"{authors}. {title}[C]"
    booktitle = entry.get('booktitle', '')
    if booktitle:
        result += f"//{booktitle}"
    result += '.'
    address = entry.get('address', '')
    publisher = entry.get('publisher', '')
    has_pub = bool(address or publisher)
    if address and publisher:
        result += f" {address}: {publisher}"
    elif publisher:
        result += f" {publisher}"
    year = entry.get('year', '')
    if year:
        if has_pub:
            result += f", {year}"
        else:
            result += f" {year}"
    volume = entry.get('volume', '')
    number = entry.get('number', '')
    if volume:
        result += f", {volume}"
        if number:
            result += f"({number})"
    pages = entry.get('pages', '')
    if pages:
        result += f": {pages}"
    result += '.'
    doi = entry.get('doi', '')
    if doi:
        result += f" doi:{doi}."
    return result


def _fmt_thesis(entry: dict, authors: str, title: str, _lang: str) -> str:
    """学位论文 [D]: 作者. 题名[D]. 出版地: 授予单位, 年."""
    result = f"{authors}. {title}[D]."
    address = entry.get('address', '')
    school = entry.get('school', '')
    if address and school:
        result += f" {address}: {school}"
    elif school:
        result += f" {school}"
    year = entry.get('year', '')
    if year:
        result += f", {year}"
    result += '.'
    return result


def _fmt_patent(entry: dict, authors: str, title: str, _lang: str) -> str:
    """专利 [P]: 申请者. 专利名: 专利号[P]. 公告日期."""
    result = f"{authors}. {title}"
    number = entry.get('number', '')
    if number:
        result += f": {number}"
    result += '[P].'
    year = entry.get('year', '')
    if year:
        result += f" {year}"
    # 尝试更具体的日期字段
    month = entry.get('month', '')
    if month:
        result += f"-{month}"
    result += '.'
    url = entry.get('url', '')
    if url:
        result += f" {url}."
    return result


def _fmt_online(entry: dict, authors: str, title: str, _lang: str) -> str:
    """电子文献 [EB/OL]: 作者. 题名[EB/OL]. (更新日)[引用日]. URL."""
    now = datetime.datetime.now().strftime('%Y-%m-%d')
    result = f"{authors}. {title}[EB/OL]."
    update_date = entry.get('year', '')
    if update_date:
        result += f" ({update_date})"
    result += f"[{now}]."
    url = entry.get('url', '')
    if url:
        result += f" {url}."
    doi = entry.get('doi', '')
    if doi:
        result += f" doi:{doi}."
    return result


def _fmt_report(entry: dict, authors: str, title: str, _lang: str) -> str:
    """技术报告 [R]: 作者. 题名[R]. 出版地: 机构, 年."""
    result = f"{authors}. {title}[R]."
    address = entry.get('address', '')
    institution = entry.get('institution', '')
    if address and institution:
        result += f" {address}: {institution}"
    elif institution:
        result += f" {institution}"
    year = entry.get('year', '')
    if year:
        result += f", {year}"
    result += '.'
    return result


def _fmt_generic(entry: dict, authors: str, title: str, lang: str) -> str:
    """通用格式 [Z]: 回退到期刊格式."""
    return _fmt_journal(entry, authors, title, lang)


# 类型分发表
_FORMATTERS = {
    'J':  _fmt_journal,
    'M':  _fmt_book,
    'C':  _fmt_conference,
    'D':  _fmt_thesis,
    'P':  _fmt_patent,
    'EB': _fmt_online,
    'R':  _fmt_report,
    'Z':  _fmt_generic,
    # 其他类型回退到通用格式
    'G':  _fmt_generic,
    'N':  _fmt_generic,
    'S':  _fmt_generic,
    'DB': _fmt_generic,
    'CP': _fmt_generic,
    'A':  _fmt_generic,
    'CM': _fmt_generic,
    'DS': _fmt_generic,
}


# ---------------------------------------------------------------------------
# 主转换逻辑
# ---------------------------------------------------------------------------

def convert_entry(entry: dict) -> str:
    """将单个 BibTeX 条目字典转换为 GB/T 7714 格式字符串.

    Args:
        entry: bibtexparser 解析出的条目字典. 必须包含 entrytype 和 author 等字段.

    Returns:
        格式化后的 GB/T 7714 参考文献字符串.

    Raises:
        KeyError: 缺少必要字段时抛出, 附带提示信息.
    """
    entry = {k.lower(): v for k, v in entry.items()}
    entry_type = entry.get('entrytype', 'misc').lower()

    # --- 处理 arXiv 电子预印本 ---
    if 'primaryclass' in entry and 'archiveprefix' in entry:
        return _fmt_arxiv(entry)

    gbt_code = TYPE_MAP.get(entry_type, 'Z')

    # --- 作者 ---
    author_field = entry.get('author', '')
    raw_authors = [a.strip() for a in re.split(r'\band\b', author_field, flags=re.IGNORECASE)] if author_field else []
    lang = _detect_language(raw_authors)
    authors = format_authors(author_field, lang)

    # --- 题名 (首字母大写) ---
    title = _capitalize_title(entry.get('title', ''))

    # --- 按类型分发 ---
    formatter = _FORMATTERS.get(gbt_code, _fmt_generic)
    try:
        return formatter(entry, authors, title, lang)
    except KeyError:
        raise
    except Exception as e:
        raise ValueError(f"格式化条目 '{entry.get('id', '?')}' 时出错: {e}")


def _fmt_arxiv(entry: dict) -> str:
    """arXiv 预印本 [EB/OL] 特殊处理."""
    now = datetime.datetime.now().strftime('%Y-%m-%d')
    author_field = entry.get('author', '')
    raw_authors = [a.strip() for a in re.split(r'\band\b', author_field, flags=re.IGNORECASE)] if author_field else []
    lang = _detect_language(raw_authors)
    authors = format_authors(author_field, lang)
    title = _capitalize_title(entry.get('title', ''))

    primaryclass = entry.get('primaryclass', '')
    eprint = entry.get('eprint', '')
    arxiv_id = f"arXiv:{primaryclass}/{eprint}" if primaryclass and eprint else f"arXiv:{eprint}"

    result = f"{authors}. {title}[EB/OL]."
    year = entry.get('year', '')
    if year:
        result += f" ({year})"
    result += f"[{now}]."
    result += f" https://arxiv.org/abs/{eprint}."
    doi = entry.get('doi', '')
    if doi:
        result += f" doi:{doi}."
    return result


# ---------------------------------------------------------------------------
# 批量转换 API
# ---------------------------------------------------------------------------

def convert_bibtex_string(bibtex_str: str) -> list[str]:
    """将 BibTeX 字符串转换为 GB/T 7714 格式列表."""
    try:
        database = bibtexparser.parse_string(bibtex_str)
    except Exception as e:
        raise ValueError(f"BibTeX 解析失败: {e}")

    results = []
    for i, entry in enumerate(database.entries):
        try:
            formatted = convert_entry(entry)
            results.append(f"[{i+1}] {formatted}")
        except KeyError as e:
            results.append(f"[{i+1}] ⚠ 错误: {e}")
        except Exception as e:
            results.append(f"[{i+1}] ⚠ 错误: {e}")
    return results


def convert_bibtex_file(file_path: str) -> list[str]:
    """将 .bib 文件转换为 GB/T 7714 格式列表."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件 '{file_path}' 不存在.")

    try:
        database = bibtexparser.parse_file(file_path)
    except Exception as e:
        raise ValueError(f"无法解析文件 '{file_path}': {e}")

    results = []
    for i, entry in enumerate(database.entries):
        try:
            formatted = convert_entry(entry)
            results.append(f"[{i+1}] {formatted}")
        except KeyError as e:
            results.append(f"[{i+1}] ⚠ 错误: {e}")
        except Exception as e:
            results.append(f"[{i+1}] ⚠ 错误: {e}")
    return results
