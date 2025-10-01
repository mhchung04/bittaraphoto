from ui.frame_manager import FrameManager
import os
import json

def test_frame_manager():
    print("Testing FrameManager...")
    
    # Setup
    manager = FrameManager('test_frames.json')
    
    # Test 1: Add Frame
    new_frame = {
        "name": "Test Frame",
        "filename": "test.png",
        "type": "four_cut",
        "regions": [[0,0,100,100]]
    }
    manager.add_frame(new_frame)
    
    frames = manager.get_all_frames()
    assert len(frames) == 1
    assert frames[0]['name'] == "Test Frame"
    print("Test 1 Passed: Add Frame")
    
    # Test 2: Persistence
    manager2 = FrameManager('test_frames.json')
    frames2 = manager2.get_all_frames()
    assert len(frames2) == 1
    assert frames2[0]['name'] == "Test Frame"
    print("Test 2 Passed: Persistence")
    
    # Test 3: Update Frame
    updated_frame = new_frame.copy()
    updated_frame['name'] = "Updated Frame"
    manager.update_frame(0, updated_frame)
    
    manager3 = FrameManager('test_frames.json')
    frames3 = manager3.get_all_frames()
    assert frames3[0]['name'] == "Updated Frame"
    print("Test 3 Passed: Update Frame")
    
    # Test 4: Delete Frame
    manager.delete_frame(0)
    frames4 = manager.get_all_frames()
    assert len(frames4) == 0
    print("Test 4 Passed: Delete Frame")
    
    # Cleanup
    if os.path.exists('test_frames.json'):
        os.remove('test_frames.json')
    print("All tests passed!")

if __name__ == "__main__":
    test_frame_manager()
