#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

def compress_images():
    print("🔍 搜尋並壓縮所有 featured.png 圖片...\n")
    
    base_dir = Path("content")
    png_files = list(base_dir.glob("**/featured.png"))
    
    total = len(png_files)
    success = 0
    skipped = 0
    total_before = 0
    total_after = 0
    
    for idx, png_file in enumerate(sorted(png_files), 1):
        # 跳過已處理的
        backup_file = png_file.with_suffix('.png.backup')
        if backup_file.exists():
            continue
            
        size_before = png_file.stat().st_size
        kb_before = size_before / 1024
        
        print(f"[{idx}/{total}] 處理: {png_file} ({kb_before:.1f} KB)")
        
        # 備份
        subprocess.run(['cp', str(png_file), str(backup_file)], check=True, capture_output=True)
        
        # 壓縮
        result = subprocess.run(
            ['pngquant', '--quality=65-80', '--force', '--ext', '.png', str(png_file)],
            capture_output=True
        )
        
        size_after = png_file.stat().st_size
        
        if size_after >= size_before:
            # 還原
            subprocess.run(['mv', str(backup_file), str(png_file)], check=True, capture_output=True)
            print(f"    ⚠️  壓縮後無改善，已還原\n")
            skipped += 1
        else:
            kb_after = size_after / 1024
            reduction = (size_before - size_after) / size_before * 100
            saved_kb = (size_before - size_after) / 1024
            print(f"    ✅ {kb_before:.1f} KB → {kb_after:.1f} KB (減少 {reduction:.1f}%, 節省 {saved_kb:.1f} KB)\n")
            success += 1
            total_before += size_before
            total_after += size_after
    
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
    print("   - 刪除所有備份: find content -name 'featured.png.backup' -delete")
    print("   - 還原所有圖片: find content -name 'featured.png.backup' -exec bash -c 'mv \"$0\" \"${0%.backup}\"' {} \\;")

if __name__ == "__main__":
    compress_images()
