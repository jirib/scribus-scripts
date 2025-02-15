import scribus
import sys

def shrink_text_frame():
    """Shrinks a selected text frame to its minimum vertical size without causing text overflow."""
    if not scribus.haveDoc():
        scribus.messageBox("Error", "No document open. Please open a Scribus document first.", scribus.ICON_WARNING)
        sys.exit(1)
    
    frame_name = scribus.getSelectedObject()
    if not frame_name:
        scribus.messageBox("Warning", "No text frame selected. Please select a text frame first.", scribus.ICON_WARNING)
        return
    
    x, y = scribus.getPosition(frame_name)
    margins = scribus.getPageMargins()
    page_width, page_height = scribus.getPageSize()
    
    width = page_width - margins[0] - margins[1]
    max_height = page_height - margins[2] - margins[3]  # Vertical area inside margins
    min_height = 1  # Minimum height in mm
    current_height = min_height
    
    scribus.sizeObject(width, min_height, frame_name)
    
    while scribus.textOverflows(frame_name):
        if current_height >= max_height:
            scribus.messageBox("Warning", f"Text still overflows at max height ({max_height} mm). Consider adjusting layout.", 
                               scribus.ICON_WARNING)
            break
        current_height += 2  # Increase height gradually
        scribus.sizeObject(width, current_height, frame_name)
    
    scribus.messageBox("Success", f"Text frame {frame_name} resized to fit text without overflow.")

# Run the function
shrink_text_frame()
