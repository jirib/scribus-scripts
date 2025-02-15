import scribus
import sys

def create_text_frame(page, columns, gap):
    """Creates a text frame inside the page margins with specified columns and gap."""
    scribus.gotoPage(page)
    
    margins = scribus.getPageMargins()
    page_width, page_height = scribus.getPageSize()
    x = margins[0]
    y = margins[2]
    width = page_width - margins[0] - margins[1]
    height = page_height - margins[2] - margins[3]
    
    frame_name = f"TextFrame_{page}"
    frame = scribus.createText(x, y, width, height, frame_name)
    
    scribus.setColumns(columns, frame_name)
    
    scribus.setColumnGap(float(gap), frame_name)
    
    return frame_name

def manage_text_overflow():
    """Handles checking text overflow and adding pages if necessary."""
    if not scribus.haveDoc():
        scribus.messageBox(
            "Error", "No document open. Please open a Scribus document first.", scribus.ICON_WARNING
        )
        sys.exit(1)
    
    frame_name = scribus.getSelectedObject()
    if not frame_name:
        scribus.messageBox(
            "Warning", "No text frame selected. Please select a text frame first.", scribus.ICON_WARNING
        )
        return
    
    columns = int(scribus.valueDialog("Columns", "Enter number of columns:", "2"))
    gap = float(scribus.valueDialog("Column Gap", "Enter column gap in mm:", "4"))
    
    current_page = scribus.currentPage()
    left_master, right_master = None, None
    
    while scribus.textOverflows(frame_name):
        new_page = current_page + 1
        
        try:
            scribus.newPage(new_page)

        except IndexError:
            if new_page % 2 == 0:
                if left_master is None:
                    left_master = scribus.valueDialog(
                        "Master Page Needed", "Enter left master page name (or leave blank):", ""
                    )
                scribus.newPage(new_page, left_master)

            else:
                if right_master is None:
                    right_master = scribus.valueDialog(
                        "Master Page Needed", "Enter right master page name (or leave blank):", ""
                    )
                scribus.newPage(new_page, right_master)
        
        new_frame_name = create_text_frame(new_page, columns, gap)
        scribus.linkTextFrames(frame_name, new_frame_name)

        frame_name = new_frame_name
        current_page = new_page
    
    scribus.messageBox("Success", "Text overflow handled. Pages added as needed.")

# Run the function
manage_text_overflow()
