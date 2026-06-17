[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

<!-- 项目LOGO -->
<br />
<div align="center">
  <img src="https://i.ibb.co/zQvJf2L/Vector.png" alt="Vector" height="200"/>
  <h3 align="center">BibTeX 转 GB/T 7714-2015 转换器</h3>

  <p align="center">
    将 BibTeX 引用转换为符合 GB/T 7714-2015 国家标准的参考文献格式
    <br />
    <a href="https://openstd.samr.gov.cn/bzgk/gb/newGbInfo?hcno=7FA63E9BBA56E60471AEDAEBDE44B14C"><strong>了解 GB/T 7714-2015 »</strong></a>
    <br />
    <a href="https://github.com/54dbd/Bibtex-to-gbt7714/issues">报告错误</a>
  </p>
</div>

---

## 关于本项目

本项目将 BibTeX 文件转换为 **GB/T 7714-2015** 格式，该格式是中国学术出版物常用的标准引用格式。

**✨ 新功能：Web 界面支持！** 除了命令行，现在还可以通过浏览器直接粘贴 BibTeX 并即时转换。

### 核心特性

- 🖥 **Web UI** — 浏览器中粘贴 BibTeX，一键转换，即时显示结果
- 📋 **CLI 支持** — 命令行批量转换 `.bib` 文件
- 🌐 **中英文区分** — 自动检测文献语言，中文用「等」、英文用「et al」
- 📚 **6 种文献类型** — 期刊、图书、会议、学位论文、专利、电子文献全覆盖
- 🔄 **arXiv 支持** — 自动识别 arXiv 预印本并生成电子文献格式

---

## 快速开始

本项目运行于 Python 3.9+。

### 环境

* Python 3.9+
* pip 或 conda

### 安装

```sh
git clone https://github.com/54dbd/Bibtex-to-gbt7714-converter.git
cd Bibtex-to-gbt7714-converter

# 推荐：用 conda 创建独立环境
conda create -n bib2gbt python=3.12 -y
conda activate bib2gbt

# 安装依赖
pip install -r requirements.txt
```

### 使用方式

#### 方式 1：Web 界面（推荐）

```sh
streamlit run app.py
```

浏览器会自动打开 `http://127.0.0.1:7860`。

- **单条转换**：粘贴 BibTeX → 点击「转换」→ 结果下方显示
- **批量上传**：上传 `.bib` 文件 → 自动转换全部条目
- 点击结果右上角复制按钮即可复制

#### 方式 2：命令行

```sh
python main.py data/ref.bib
```

将 `data/ref.bib` 替换为你的文件路径。输出文件为 `xxx_bgt7714.txt`。

---

## 支持的文献类型

| 类型 | 标识 | 格式 |
|------|------|------|
| 期刊文章 | [J] | 作者. 题名[J]. 刊名, 年, 卷(期): 页码. |
| 图书 | [M] | 作者. 书名[M]. 出版地: 出版社, 年. |
| 会议论文 | [C] | 作者. 题名[C]//会议名. 出版地: 出版者, 年: 页码. |
| 学位论文 | [D] | 作者. 题名[D]. 出版地: 授予单位, 年. |
| 专利 | [P] | 申请者. 专利名: 专利号[P]. 公告日期. |
| 电子文献 | [EB/OL] | 作者. 题名[EB/OL]. (更新日)[引用日]. URL. |

### 中英文规则

- **≤3 位作者**：全部列出
- **>3 位作者**：中文文献用「等」，英文文献用「et al」
- 语言基于作者姓氏自动检测（中文姓氏表位于 `data/Chinese_surname.csv`）

---

## 项目结构

```
Bibtex-to-GBT7714-2015/
├── converter.py          # 核心转换逻辑（无 UI 依赖）
├── app.py                # Streamlit Web UI
├── main.py               # CLI 命令行入口
├── requirements.txt
├── data/
│   ├── Chinese_surname.csv   # 中文姓氏表
│   ├── ref.bib               # 示例 BibTeX 文件
│   └── ref_bgt7714.txt       # 示例转换输出
└── utility/
    └── chineseSurnameCombination.py  # 中文姓氏维护工具
```

---

## 添加自定义中文姓氏

如果你的参考文献包含不在默认列表中的中文姓氏，可以添加：

```sh
python utility/chineseSurnameCombination.py <surname1> <surname2> ...
```

---

## 开发规划

- [x] 支持 arXiv 格式
- [x] 支持常见格式（期刊、图书、会议、学位论文、专利、电子文献）
- [x] Web UI 界面
- [x] 中英文自动区分（等 / et al）
- [ ] 支持所有 BibTeX 类型
- [ ] 多语言输入（中文未完全测试）

查看 [open issues](https://github.com/54dbd/Bibtex-to-gbt7714/issues) 了解完整待实现功能。

---

## 贡献者

本项目基于 [54dbd/Bibtex-to-GBT7714-2015](https://github.com/54dbd/Bibtex-to-GBT7714-2015) 二次开发。

- Lhong427

---

## 许可证

本项目基于 GPL-3.0 许可证分发。详情请查看 LICENSE 文件。

<!-- MARKDOWN LINKS -->
[contributors-shield]: https://img.shields.io/github/contributors/54dbd/Bibtex-to-gbt7714.svg?style=for-the-badge
[contributors-url]: https://github.com/54dbd/Bibtex-to-gbt7714/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/54dbd/Bibtex-to-gbt7714.svg?style=for-the-badge
[forks-url]: https://github.com/54dbd/Bibtex-to-gbt7714/network/members
[stars-shield]: https://img.shields.io/github/stars/54dbd/Bibtex-to-gbt7714.svg?style=for-the-badge
[stars-url]: https://github.com/54dbd/Bibtex-to-gbt7714/stargazers
[issues-shield]: https://img.shields.io/github/issues/54dbd/Bibtex-to-gbt7714.svg?style=for-the-badge
[issues-url]: https://github.com/54dbd/Bibtex-to-gbt7714/issues
[license-shield]: https://img.shields.io/github/license/54dbd/Bibtex-to-gbt7714.svg?style=for-the-badge
[license-url]: https://github.com/54dbd/Bibtex-to-gbt7714/blob/master/LICENSE.txt
