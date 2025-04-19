from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk

class DraggableAccessory:
    def __init__(self, path, image, x=0, y=0):
        self.path = path
        self.image = image
        self.tk_image = ImageTk.PhotoImage(image)
        self.x = x
        self.y = y
        self.canvas_id = None

class OfficerMaker:
    def __init__(self, root):
        self.root = root
        self.root.title("UTTP Officer Maker 1.0 By Rebirthyr")

        self.canvas = Canvas(root, width=512, height=512, bg="gray")
        self.canvas.grid(row=0, column=0, columnspan=4)

        Button(root, text="Load Body", command=self.load_body).grid(row=1, column=0)
        Button(root, text="Add Accessory", command=self.add_accessory).grid(row=1, column=1)
        Button(root, text="Export", command=self.export_image).grid(row=1, column=2)
        Button(root, text="Reset", command=self.reset).grid(row=1, column=3)

        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.do_drag)
        self.canvas.bind("<ButtonRelease-1>", self.end_drag)

        self.root.bind("<KeyPress-plus>", self.resize_selected_up)
        self.root.bind("<KeyPress-equal>", self.resize_selected_up)
        self.root.bind("<KeyPress-minus>", self.resize_selected_down)

        self.body_image_path = None
        self.accessories = []
        self.selected_accessory = None
        self.dragged_accessory = None
        self.offset_x = 0
        self.offset_y = 0

        self.render_preview()

    def load_body(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.webp")])
        if path:
            self.body_image_path = path
            self.render_preview()

    def add_accessory(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.webp")])
        if path:
            image = Image.open(path).convert("RGBA").resize((128, 128))
            accessory = DraggableAccessory(path, image, x=200, y=200)
            self.accessories.append(accessory)
            self.selected_accessory = accessory
            self.render_preview()

    def reset(self):
        self.body_image_path = None
        self.accessories.clear()
        self.selected_accessory = None
        self.render_preview()

    def export_image(self):
        if not self.body_image_path:
            return
        final = self.compose_image()
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if path:
            final.save(path)

    def compose_image(self):
        base = Image.open(self.body_image_path).convert("RGBA").resize((512, 512)) if self.body_image_path else Image.new("RGBA", (512, 512), (120, 120, 120, 255))
        for acc in self.accessories:
            base.paste(acc.image, (acc.x, acc.y), acc.image)
        return base

    def render_preview(self):
        self.canvas.delete("all")
        bg = self.compose_image()
        self.tk_bg = ImageTk.PhotoImage(bg)
        self.canvas.create_image(0, 0, anchor=NW, image=self.tk_bg)
        for acc in self.accessories:
            acc.tk_image = ImageTk.PhotoImage(acc.image)
            acc.canvas_id = self.canvas.create_image(acc.x, acc.y, anchor=NW, image=acc.tk_image)
            if acc == self.selected_accessory:
                self.canvas.create_rectangle(
                    acc.x, acc.y,
                    acc.x + acc.image.width, acc.y + acc.image.height,
                    outline="red", width=2
                )

    def start_drag(self, event):
        self.dragged_accessory = None
        self.selected_accessory = None
        for acc in reversed(self.accessories):
            x1, y1 = acc.x, acc.y
            x2, y2 = x1 + acc.image.width, y1 + acc.image.height
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                self.dragged_accessory = acc
                self.selected_accessory = acc
                self.offset_x = event.x - acc.x
                self.offset_y = event.y - acc.y
                break
        self.render_preview()

    def do_drag(self, event):
        if self.dragged_accessory:
            self.dragged_accessory.x = event.x - self.offset_x
            self.dragged_accessory.y = event.y - self.offset_y
            self.render_preview()

    def end_drag(self, event):
        self.dragged_accessory = None

    def resize_selected_up(self, event=None):
        if self.selected_accessory:
            self.resize_accessory(self.selected_accessory, 1.1)

    def resize_selected_down(self, event=None):
        if self.selected_accessory:
            self.resize_accessory(self.selected_accessory, 0.9)

    def resize_accessory(self, accessory, scale):
        w, h = accessory.image.size
        new_size = (int(w * scale), int(h * scale))
        image = Image.open(accessory.path).convert("RGBA").resize(new_size)
        accessory.image = image
        accessory.tk_image = ImageTk.PhotoImage(image)
        self.render_preview()

if __name__ == "__main__":
    root = Tk()
    app = OfficerMaker(root)
    root.mainloop()
