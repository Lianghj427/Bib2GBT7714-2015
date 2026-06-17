"""
Streamlit Web UI for BibTeX to GB/T 7714-2015 conversion.

Usage:
    streamlit run app.py
    # Or: python -m streamlit run app.py
"""

import streamlit as st

from converter import convert_bibtex_string

# ---------------------------------------------------------------------------
# 页面配置
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="BibTeX → GB/T 7714-2015 转换器",
    page_icon="📚",
    layout="wide",
)

# ---------------------------------------------------------------------------
# 示例 BibTeX
# ---------------------------------------------------------------------------
EXAMPLE_BIBTEX = """@inproceedings{foerster2018counterfactual,
  title={Counterfactual multi-agent policy gradients},
  author={Foerster, Jakob and Farquhar, Gregory and Afouras, Triantafyllos and Nardelli, Nantas and Whiteson, Shimon},
  booktitle={Proceedings of the AAAI conference on artificial intelligence},
  volume={32},
  number={1},
  year={2018}
}

@article{zhang2020deep,
  title={深度学习在自然语言处理中的应用研究},
  author={Zhang, Wei and Li, Ming and Wang, Qiang and Liu, Yang and Chen, Hao},
  journal={计算机学报},
  year={2020},
  volume={43},
  number={8},
  pages={1500-1520}
}"""

# ---------------------------------------------------------------------------
# Session State 初始化
# ---------------------------------------------------------------------------
if "single_text" not in st.session_state:
    st.session_state.single_text = EXAMPLE_BIBTEX


def clear_single():
    """清空单条转换的输入框."""
    st.session_state.single_text = ""


# ---------------------------------------------------------------------------
# 标题
# ---------------------------------------------------------------------------
st.title("📚 BibTeX → GB/T 7714-2015 参考文献转换器")
st.markdown(
    "将 BibTeX 引用转换为符合 **GB/T 7714-2015** 国家标准的参考文献格式。"
    "支持期刊、图书、会议、学位论文、专利、电子文献等类型，"
    "自动区分中英文（中文用「等」，英文用「et al」）。"
)

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab1, tab2 = st.tabs(["📝 单条转换", "📁 批量上传"])

# ===== Tab 1: 单条转换 =====
with tab1:
    st.markdown("粘贴一条或多条 BibTeX 引用，点击 **转换** 按钮。")

    bibtex_input = st.text_area(
        "BibTeX 引用",
        value=st.session_state.single_text,
        height=280,
        placeholder="@article{...}\n@book{...}",
        key="single_input",
    )

    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        convert_btn = st.button("🔄 转换", type="primary", use_container_width=True)
    with col2:
        st.button("🗑 清空", on_click=clear_single, use_container_width=True)

    if convert_btn:
        text = bibtex_input.strip()
        if not text:
            st.warning("⚠ 请先粘贴 BibTeX 引用内容。")
        else:
            try:
                results = convert_bibtex_string(text)
                output = "\n\n".join(results)
                st.code(output, language=None, line_numbers=False)
                st.success(f"✅ 成功转换 {len(results)} 条参考文献")
            except ValueError as e:
                st.error(f"❌ 解析错误: {e}")
            except Exception as e:
                st.error(f"❌ 未知错误: {e}")

# ===== Tab 2: 批量上传 =====
with tab2:
    st.markdown("上传一个 `.bib` 文件，批量转换所有条目。")

    uploaded_file = st.file_uploader(
        "选择 .bib 文件",
        type=["bib"],
        key="file_uploader",
    )

    if uploaded_file is not None:
        file_name = uploaded_file.name
        st.info(f"📄 已上传: **{file_name}**")

        try:
            # 尝试 UTF-8，失败则尝试 GBK
            content = uploaded_file.read()
            try:
                bibtex_str = content.decode("utf-8")
            except UnicodeDecodeError:
                bibtex_str = content.decode("gbk")

            results = convert_bibtex_string(bibtex_str)
            output = "\n\n".join(results)
            st.code(output, language=None, line_numbers=False)
            st.success(f"✅ 成功转换 {len(results)} 条参考文献")

        except ValueError as e:
            st.error(f"❌ 解析错误: {e}")
        except Exception as e:
            st.error(f"❌ 未知错误: {e}")

# ---------------------------------------------------------------------------
# 页脚说明
# ---------------------------------------------------------------------------
with st.expander("📖 支持的文献类型与格式说明", expanded=False):
    st.markdown(
        """
        ### 支持的文献类型

        | 类型 | 标识 | 格式示例 |
        |------|------|---------|
        | 期刊文章 | [J] | 作者. 题名[J]. 刊名, 年, 卷(期): 页码. |
        | 图书 | [M] | 作者. 书名[M]. 出版地: 出版社, 年. |
        | 会议论文 | [C] | 作者. 题名[C]//会议名. 出版地: 出版者, 年. |
        | 学位论文 | [D] | 作者. 题名[D]. 出版地: 授予单位, 年. |
        | 专利 | [P] | 申请者. 专利名: 专利号[P]. 公告日期. |
        | 电子文献 | [EB/OL] | 作者. 题名[EB/OL]. (更新日)[引用日]. URL. |

        ### 中英文规则

        - **≤3 位作者**: 全部列出
        - **>3 位作者**: 中文用「等」, 英文用「et al」
        - 语言自动检测: 基于作者姓氏是否在中文姓氏表中
        """
    )
