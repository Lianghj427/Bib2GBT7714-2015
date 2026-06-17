"""
CLI 入口: 将 BibTeX 文件转换为 GB/T 7714-2015 格式并保存.

用法:
    python main.py data/ref.bib
    python main.py /path/to/your.bib
"""

import logging
import os
import sys

from converter import convert_bibtex_file

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) > 1:
        bib_path = sys.argv[1]
    else:
        bib_path = "data/ref.bib"

    try:
        result = convert_bibtex_file(bib_path)
    except FileNotFoundError as e:
        logger.error(f"文件不存在: {e}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"解析失败: {e}")
        sys.exit(1)

    # 保存到文件
    folder = os.path.dirname(bib_path)
    file_name = os.path.basename(bib_path).split('.')[0]
    output_path = os.path.join(folder, f"{file_name}_bgt7714.txt")

    with open(output_path, 'w', encoding='utf-8') as f:
        for line in result:
            f.write(line + '\n')

    logger.info(f"转换完成: {len(result)} 条参考文献 → {output_path}")


if __name__ == '__main__':
    main()
