#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LaTeX 公式转图片工具

使用 matplotlib 将 LaTeX 公式渲染为 PNG 图片，适合微信公众号使用。
"""

import io
import os
import sys
import hashlib
from pathlib import Path

# Windows UTF-8 编码修复
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    import matplotlib
    matplotlib.use('Agg')  # 无 GUI 后端
    import matplotlib.pyplot as plt
    from matplotlib import mathtext
except ImportError:
    print("错误: 需要安装 matplotlib")
    print("运行: pip install matplotlib")
    sys.exit(1)


def latex_to_image(latex_code, output_path, dpi=300, fontsize=14, color='black'):
    """
    将 LaTeX 公式渲染为 PNG 图片

    Args:
        latex_code: LaTeX 公式代码（如 r"$\alpha + \beta$"）
        output_path: 输出图片路径
        dpi: 图片分辨率（默认 300，适合微信）
        fontsize: 字体大小（默认 14）
        color: 文字颜色（默认黑色）
    """
    # 确保公式被 $ 包裹
    if not latex_code.startswith('$'):
        if latex_code.startswith('$$'):
            latex_code = latex_code  # 保持 $$ 显示模式
        else:
            latex_code = f'${latex_code}$'

    # 创建图片
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.patch.set_alpha(0)  # 透明背景

    # 渲染公式
    text = fig.text(
        0, 0, latex_code,
        fontsize=fontsize,
        color=color,
        ha='left', va='bottom'
    )

    # 调整图片大小以适应公式
    fig.canvas.draw()
    bbox = text.get_window_extent(fig.canvas.get_renderer())
    bbox = bbox.transformed(fig.dpi_scale_trans.inverted())

    # 添加一些边距
    padding = 0.05
    fig.set_size_inches(bbox.width + padding, bbox.height + padding)

    # 重新定位文字到中心
    text.set_position((padding/2, padding/2))

    # 保存图片
    plt.savefig(
        output_path,
        dpi=dpi,
        bbox_inches='tight',
        pad_inches=0.05,
        transparent=True
    )
    plt.close(fig)


def convert_latex_in_markdown(md_content, output_dir):
    """
    将 Markdown 中的 LaTeX 公式转换为图片引用

    Args:
        md_content: Markdown 内容
        output_dir: 图片输出目录

    Returns:
        转换后的 Markdown 内容
    """
    import re

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 匹配行内公式 $...$
    inline_pattern = r'\$([^\$\n]+?)\$'
    # 匹配块级公式 $$...$$
    block_pattern = r'\$\$([^\$]+?)\$\$'

    converted = md_content
    formula_count = 0

    def replace_formula(match, is_block=False):
        nonlocal formula_count
        formula_count += 1

        latex_code = match.group(1).strip()

        # 生成唯一文件名（基于公式内容的 hash）
        formula_hash = hashlib.md5(latex_code.encode()).hexdigest()[:8]
        filename = f"formula_{formula_hash}.png"
        filepath = output_dir / filename

        # 生成图片
        try:
            if is_block:
                latex_to_image(f'$${latex_code}$$', filepath, fontsize=16)
            else:
                latex_to_image(f'${latex_code}$', filepath, fontsize=14)

            print(f"  ✓ 公式 {formula_count}: {latex_code[:30]}...")

            # 返回图片引用
            if is_block:
                return f'\n\n<img src="images/{filename}" alt="{latex_code}" style="display:block;margin:1em auto;">\n\n'
            else:
                return f'<img src="images/{filename}" alt="{latex_code}" style="display:inline;vertical-align:middle;margin:0 2px;">'

        except Exception as e:
            print(f"  ✗ 公式转换失败: {latex_code[:30]}... ({e})")
            return match.group(0)  # 保持原样

    # 先处理块级公式（避免被行内公式匹配）
    converted = re.sub(block_pattern, lambda m: replace_formula(m, is_block=True), converted, flags=re.DOTALL)

    # 再处理行内公式
    converted = re.sub(inline_pattern, lambda m: replace_formula(m, is_block=False), converted)

    print(f"\n✅ 转换了 {formula_count} 个公式")
    return converted


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='LaTeX 公式转图片工具')
    parser.add_argument('input', help='输入 Markdown 文件')
    parser.add_argument('--output', '-o', help='输出 Markdown 文件（默认覆盖原文件）')
    parser.add_argument('--image-dir', '-d', default='images', help='图片输出目录（默认 images）')

    args = parser.parse_args()

    input_file = Path(args.input)
    if not input_file.exists():
        print(f"错误: 文件不存在: {input_file}")
        sys.exit(1)

    output_file = Path(args.output) if args.output else input_file
    image_dir = input_file.parent / args.image_dir

    print(f"📝 读取文件: {input_file}")
    md_content = input_file.read_text(encoding='utf-8')

    print(f"🔄 转换公式...")
    converted = convert_latex_in_markdown(md_content, image_dir)

    print(f"💾 保存文件: {output_file}")
    output_file.write_text(converted, encoding='utf-8')

    print(f"\n✨ 完成！图片保存在: {image_dir}")


if __name__ == '__main__':
    main()
