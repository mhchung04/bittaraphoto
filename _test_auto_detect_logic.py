import os
from PIL import Image

def test_auto_detect(filename):
    print(f"Testing auto-detection on {filename}...")
    
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return

    try:
        img = Image.open(filename).convert("RGBA")
        width, height = img.size
        print(f"Image size: {width}x{height}")
        
        visited = set()
        regions = []
        pixels = img.load()
        step = 5 
        
        for y in range(0, height, step):
            for x in range(0, width, step):
                if (x, y) in visited:
                    continue
                    
                r, g, b, a = pixels[x, y]
                if a < 10: # Transparent
                    min_x, min_y, max_x, max_y = x, y, x, y
                    stack = [(x, y)]
                    visited.add((x, y))
                    
                    while stack:
                        cx, cy = stack.pop()
                        
                        min_x = min(min_x, cx)
                        min_y = min(min_y, cy)
                        max_x = max(max_x, cx)
                        max_y = max(max_y, cy)
                        
                        for dx, dy in [(-step, 0), (step, 0), (0, -step), (0, step)]:
                            nx, ny = cx + dx, cy + dy
                            if 0 <= nx < width and 0 <= ny < height:
                                if (nx, ny) not in visited:
                                    nr, ng, nb, na = pixels[nx, ny]
                                    if na < 10:
                                        visited.add((nx, ny))
                                        stack.append((nx, ny))
                    
                    if (max_x - min_x) > 50 and (max_y - min_y) > 50:
                        regions.append([min_x, min_y, max_x + step, max_y + step])

        print(f"Found {len(regions)} regions (unsorted):")
        for r in regions:
            print(r)

        # Sort logic
        regions.sort(key=lambda r: (r[1], r[0]))
        
        final_regions = []
        if regions:
            rows = []
            current_row = [regions[0]]
            
            for i in range(1, len(regions)):
                prev = current_row[-1]
                curr = regions[i]
                
                prev_cy = (prev[1] + prev[3]) // 2
                curr_cy = (curr[1] + curr[3]) // 2
                prev_h = prev[3] - prev[1]
                
                if abs(curr_cy - prev_cy) < (prev_h / 2):
                    current_row.append(curr)
                else:
                    rows.append(current_row)
                    current_row = [curr]
            rows.append(current_row)
            
            for row in rows:
                row.sort(key=lambda r: r[0])
                final_regions.extend(row)
        
        print(f"\nFinal sorted regions ({len(final_regions)}):")
        for i, r in enumerate(final_regions):
            print(f"Region {i+1}: {r}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test with frame/01.png if it exists
    test_file = os.path.join("frame", "01.png")
    test_auto_detect(test_file)
