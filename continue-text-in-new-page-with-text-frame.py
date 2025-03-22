import scribus
import sys

def check_prerequisites(frame_name):
    checks = [
        (
            not scribus.haveDoc(),
            'Error',
            'No document open. Please open a Scribus document first.',
            True
        ),
        (
            not frame_name,
            'Warning',
            'No text frame selected. Please select a text frame first.',
            False
        )
    ]

    for condition, level, message, should_exit in checks:
        if condition:
            scribus.messageBox(level, message, scribus.ICON_WARNING)
            if should_exit:
                sys.exit(1)
            else:
                return False

    return True


class PageManager:
    def __init__(self, columns, gap):
        self.columns = columns
        self.gap = gap

        self.margins = scribus.getPageMargins()
        self.page_width, self.page_height = scribus.getPageSize()

        # height resize hack
        self.hack = True
        self.unit = scribus.getUnit()  # inch, mm, picas, points
        self.units = [0.79, 2.0, 0.48, 5.67]  # 2mm into other units

        self.current_page = scribus.currentPage()
        self.master = None
        self.left_master = None
        self.right_master = None
        self.facing_pages = not scribus.NOFACINGPAGES


    def get_master_page(self, side=None):
        all_masters = scribus.masterPageNames()

        if len(all_masters) == 1:
            return all_masters[0]

        fallback = all_masters[0]

        if side is None:  # no facing page
            prompt = 'Enter master page name'
            default = fallback
        else:
            candidate = f'Normal {side.title()}'
            default = candidate if candidate in all_masters else fallback
            prompt = f'Enter {side} master page name'

        message = f'{prompt} (or press enter for "{default}"):'
        master = scribus.valueDialog('Master Page Needed', message, default)

        return master


    def get_master(self, new_page):
        if not self.facing_pages:
            if self.master is None:
                self.master = self.get_master_page()
            return self.master

        side = 'left' if new_page % 2 == 0 else 'right'
        attr = f'{side}_master'
        master = getattr(self, attr)

        if master is None:
            master = self.get_master_page(side)
            setattr(self, attr, master)

        return master


    def create_text_frame(self, page_num):
        x = self.margins[0]
        y = self.margins[2]
        width = self.page_width - self.margins[0] - self.margins[1]
        height = self.page_height - self.margins[2] - self.margins[3]

        # hack: some chars do not fit into the frame
        height += self.units[self.unit] if self.hack else 0

        name = f"TextFrame_{page_num}"

        scribus.gotoPage(page_num)
        scribus.createText(x, y, width, height, name)
        scribus.setColumns(self.columns, name)
        scribus.setColumnGap(self.gap, name)

        return name


    def add_page_with_frame(self, previous_frame):
        self.current_page += 1
        master = self.get_master(self.current_page)
        scribus.newPage(self.current_page, master)
        new_frame = self.create_text_frame(self.current_page)
        scribus.linkTextFrames(previous_frame, new_frame)
        return new_frame


def manage_text_overflow(frame_name):
    columns = scribus.getColumns(frame_name)
    gap = scribus.getColumnGap(frame_name)

    p = PageManager(columns=columns, gap=gap)

    while scribus.textOverflows(frame_name):
        frame_name = p.add_page_with_frame(frame_name)

    scribus.messageBox("Success", "Text overflow handled. Pages added as needed.")


def main():
    frame_name = scribus.getSelectedObject()
    if not check_prerequisites(frame_name):
        return

    manage_text_overflow(frame_name)

if __name__ == '__main__':
    main()
