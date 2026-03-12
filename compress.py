#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

def compress_png(png_file, idx, total):
    """壓縮單個 PNG 圖片"""
    backup_file = Path(str(png_file) + '.backup')
    
    # 跳過已處理的
    if backup_file.exists():
        return None
    
    size_before = png_file.stat().st_size
    kb_before = size_before / 1024
    
    print(f"[{idx}/{total}] 處理: {png_file} ({kb_before:.1f} KB)")
    
    # 備份
    subprocess.run(['cp', str(png_file), str(backup_file)], check=True, capture_output=True)
    
    # 壓縮
    subprocess.run(
        ['pngquant', '--quality=65-80', '--force', '--ext', '.png', str(png_file)],
        capture_output=True
    )
    
    size_after = png_file.stat().st_size
    
    if size_after >= size_before:
        # 還原
        subprocess.run(['mv', str(backup_file), str(png_file)], check=True, capture_output=True)
        print(f"    ⚠️  壓縮後無改善，已還原\n")
        return {'status': 'skipped', 'before': size_before, 'after': size_before}
    else:
        kb_after = size_after / 1024
        reduction = (size_before - size_after) / size_before * 100
        saved_kb = (size_before - size_after) / 1024
        print(f"    ✅ {kb_before:.1f} KB → {kb_after:.1f} KB (減少 {reduction:.1f}%, 節省 {saved_kb:.1f} KB)\n")
        return {'status': 'success', 'before': size_before, 'after': size_after}

def list_articles_with_featured():
    """列出所有包含 featured.png 的文章"""
    content_dir = Path("content")
    if not content_dir.exists():
        return []
    
    articles = []
    for featured_file in sorted(content_dir.glob("**/featured.png")):
        article_dir = featured_file.parent
        backup_exists = Path(str(featured_file) + '.backup').exists()
        
        # 獲取相對路徑
        rel_path = article_dir.relative_to(content_dir)
        
        articles.append({
            'path': featured_file,
            'dir': article_dir,
            'rel_path': rel_path,
            'compressed': backup_exists,
            'size': featured_file.stat().st_size
        })
    
    return articles

def select_articles_interactive():
    """互動式選擇要壓縮的文章"""
    articles = list_articles_with_featured()
    
    if not articles:
        print("❌ 沒有找到任何文章封面圖！")
        return []
    
    print(f"\n📋 找到 {len(articles)} 篇文章：\n")
    
    for idx, article in enumerate(articles, 1):
        status = "✓ 已壓縮" if article['compressed'] else "○ 未壓縮"
        size_kb = article['size'] / 1024
        print(f"  [{idx:2d}] {status} {article['rel_path']} ({size_kb:.1f} KB)")
    
    print("\n選項：")
    print("  a) 全部壓縮")
    print("  n) 僅壓縮未處理的")
    print("  數字) 選擇特定文章（例如：1,3,5 或 1-5）")
    print("  q) 退出")
    
    choice = input("\n請選擇: ").strip().lower()
    
    if choice == 'q':
        return []
    elif choice == 'a':
        return articles
    elif choice == 'n':
        return [a for a in articles if not a['compressed']]
    else:
        # 解析數字選擇
        selected = []
        try:
            for part in choice.split(','):
                part = part.strip()
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    for i in range(start, end + 1):
                        if 1 <= i <= len(articles):
                            selected.append(articles[i - 1])
                else:
                    i = int(part)
                    if 1 <= i <= len(articles):
                        selected.append(articles[i - 1])
            return selected
        except ValueError:
            print("❌ 輸入格式錯誤！")
            return []

def compress_jpg(jpg_file, idx, total):
    """壓縮 JPG/JPEG 圖片（使用 ImageMagick 或跳過）"""
    backup_file = Path(str(jpg_file) + '.backup')
    
    # 跳過已處理的
    if backup_file.exists():
        return None
    
    size_before = jpg_file.stat().st_size
    kb_before = size_before / 1024
    
    print(f"[{idx}/{total}] 處理: {jpg_file} ({kb_before:.1f} KB)")
    
    # JPG 已經是壓縮格式，跳過
    print(f"    ℹ️  JPG 格式，跳過壓縮\n")
    return {'status': 'skipped', 'before': size_before, 'after': size_before}

def compress_selected_articles(articles):
    """壓縮選定的文章封面圖"""
    if not articles:
        print("\n❌ 沒有選擇任何文章！")
        return
    
    print(f"\n📦 準備壓縮 {len(articles)} 篇文章的封面圖\n")
    
    # 統計資訊
    total = len(articles)
    success = 0
    skipped = 0
    total_before = 0
    total_after = 0
    
    # 處理選定的文章
    for idx, article in enumerate(articles, 1):
        result = compress_png(article['path'], idx, total)
        
        if result:
            if result['status'] == 'success':
                success += 1
                total_before += result['before']
                total_after += result['after']
            elif result['status'] == 'skipped':
                skipped += 1
    
    # 顯示統計
    print("\n🎉 壓縮完成！\n")
    print("📊 統計:")
    print(f"   - 總文章數: {total} 篇")
    print(f"   - 成功壓縮: {success} 張")
    print(f"   - 跳過: {skipped} 張")
    
    if success > 0:
        total_saved = (total_before - total_after) / 1024 / 1024
        percent_saved = (total_before - total_after) / total_before * 100
        print(f"   - 總計節省: {total_saved:.2f} MB ({percent_saved:.1f}%)")
    
    print("\n💡 後續操作：")
    print("   - 刪除所有備份: find . -name '*.backup' -delete")
    print("   - 還原所有圖片: find . -name '*.backup' -exec bash -c 'mv \"$0\" \"${0%.backup}\"' {} \\;")

def compress_images(include_assets=False):
    """
    壓縮圖片（舊版功能，壓縮所有圖片）
    include_assets: 是否包含 assets/img 目錄
    """
    print("🔍 搜尋圖片...")
    
    # 收集所有要處理的圖片
    image_files = []
    
    # 1. featured.png 圖片
    content_dir = Path("content")
    if content_dir.exists():
        featured_files = list(content_dir.glob("**/featured.png"))
        image_files.extend(featured_files)
        print(f"   - 找到 {len(featured_files)} 張 featured.png")
    
    # 2. assets/img 目錄中的圖片
    if include_assets:
        assets_dir = Path("assets/img")
        if assets_dir.exists():
            png_files = list(assets_dir.glob("**/*.png"))
            jpg_files = list(assets_dir.glob("**/*.jpg")) + list(assets_dir.glob("**/*.jpeg"))
            image_files.extend(png_files)
            image_files.extend(jpg_files)
            print(f"   - 找到 {len(png_files)} 張 PNG (assets/img)")
            print(f"   - 找到 {len(jpg_files)} 張 JPG/JPEG (assets/img)")
    
    if not image_files:
        print("\n❌ 沒有找到任何圖片！")
        return
    
    print(f"\n📦 總計: {len(image_files)} 張圖片\n")
    
    # 統計資訊
    total = len(image_files)
    success = 0
    skipped = 0
    total_before = 0
    total_after = 0
    
    # 處理所有圖片
    for idx, img_file in enumerate(sorted(image_files), 1):
        if img_file.suffix.lower() == '.png':
            result = compress_png(img_file, idx, total)
        elif img_file.suffix.lower() in ['.jpg', '.jpeg']:
            result = compress_jpg(img_file, idx, total)
        else:
            continue
        
        if result:
            if result['status'] == 'success':
                success += 1
                total_before += result['before']
                total_after += result['after']
            elif result['status'] == 'skipped':
                skipped += 1
    
    # 顯示統計
    print("\n🎉 壓縮完成！\n")
    print("📊 統計:")
    print(f"   - 總圖片數: {total} 張")
    print(f"   - 成功壓縮: {success} 張")
    print(f"   - 跳過: {skipped} 張")
    
    if success > 0:
        total_saved = (total_before - total_after) / 1024 / 1024
        percent_saved = (total_before - total_after) / total_before * 100
        print(f"   - 總計節省: {total_saved:.2f} MB ({percent_saved:.1f}%)")
    
    print("\n💡 後續操作：")
    print("   - 刪除所有備份: find . -name '*.backup' -delete")
    print("   - 還原所有圖片: find . -name '*.backup' -exec bash -c 'mv \"$0\" \"${0%.backup}\"' {} \\;")


if __name__ == "__main__":
    print("🖼️  圖片壓縮工具\n")
    
    # 檢查命令行參數
    if '--all' in sys.argv or '-a' in sys.argv:
        # 舊版模式：壓縮所有圖片
        include_assets = '--assets' in sys.argv
        if include_assets:
            print("🎯 模式: 壓縮所有圖片 (featured.png + assets/img)\n")
        else:
            print("🎯 模式: 壓縮所有 featured.png\n")
        compress_images(include_assets=include_assets)
    else:
        # 新版模式：選擇要壓縮的文章
        print("🎯 模式: 選擇要壓縮的文章封面圖")
        print("💡 提示: 使用 --all 參數來壓縮所有文章（不經過選擇）\n")
        selected_articles = select_articles_interactive()
        if selected_articles:
            compress_selected_articles(selected_articles)
