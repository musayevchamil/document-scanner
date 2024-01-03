import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
from image_functions import auto_detect_document, four_point_transform

class ImageSelector:
    def __init__(self, root):
        self.root = root
        self.img = None
        self.warpedImg = None
        self.anchors = []
        self.rect_coords = None
        self.drag_data = {"x": 0, "y": 0, "item": None}
        self.document_corners = None
        self.canvas_width = 600
        self.canvas_height = int(self.canvas_width * 1.41)
        self.setup_initial_ui()
        self.setup_scanned_ui()

    def setup_initial_ui(self):
        self.initial_frame = tk.Frame(self.root)
        self.initial_frame.pack(fill=tk.BOTH, expand=True)
        top_frame = self.create_top_frame(self.initial_frame)
        self.create_canvas(self.initial_frame)
        self.create_scan_button(self.initial_frame)

    def create_top_frame(self, parent):
        top_frame = tk.Frame(parent, height=40)
        top_frame.pack(side=tk.TOP, fill=tk.X, anchor='n', padx=15, pady=5)
        top_frame.pack_propagate(False)
        self.file_path_entry = tk.Entry(top_frame, width=50)
        self.file_path_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        browse_button = tk.Button(top_frame, text="Browse", command=self.browse_files)
        browse_button.pack(side=tk.RIGHT, padx=(15, 0))
        return top_frame

    def create_canvas(self, parent):
        self.canvas = tk.Canvas(parent, bg='white', width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=False, padx=15, pady=7.5)
        self.canvas_image = self.canvas.create_image(0, 0, anchor='nw')

    def create_scan_button(self, parent):
        scan_button = tk.Button(parent, text="Scan", command=self.scan_image)
        scan_button.pack(side=tk.BOTTOM, padx=15, pady=15)

    def setup_scanned_ui(self):
        self.scanned_frame = tk.Frame(self.root)
        dummy_top_frame = self.create_dummy_top_frame(self.scanned_frame)
        self.create_scanned_canvas(self.scanned_frame)
        self.create_save_button(self.scanned_frame)

    def create_dummy_top_frame(self, parent):
        dummy_top_frame = tk.Frame(parent, height=40)
        dummy_top_frame.pack(side=tk.TOP, fill=tk.X, padx=15, pady=5)
        dummy_top_frame.pack_propagate(False)
        back_button = tk.Button(dummy_top_frame, text="Back", command=self.show_initial_frame)
        back_button.pack(side=tk.LEFT, padx=5, pady=5)
        return dummy_top_frame

    def create_scanned_canvas(self, parent):
        self.scanned_canvas = tk.Canvas(parent, bg='white', width=self.canvas_width, height=self.canvas_height)
        self.scanned_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=False, padx=15, pady=7.5)
        self.scanned_canvas_image = self.scanned_canvas.create_image(0, 0, anchor='nw')

    def create_save_button(self, parent):
        save_button = tk.Button(parent, text="Save", command=self.save_image)
        save_button.pack(side=tk.BOTTOM, padx=15, pady=15)

    def browse_files(self):
        filename = filedialog.askopenfilename(initialdir="~/Desktop", title="Select a File",
                                              filetypes=(("all files", "*.*"), ("Image files", "*.jpg;*.jpeg;*.png")))
        if filename:
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, filename)
            self.display_image(filename)

    def display_image(self, filename):
        self.original_image = cv2.imread(filename)
        self.points, self.image_with_rectangle = auto_detect_document(self.original_image)
        self.canvas.update_idletasks()
        self.display_rect = self.update_canvas(self.canvas, self.image_with_rectangle)
        self.create_draggable_anchors(self.points)
        self.img = cv2.imread(filename)

    def display_scanned_image(self, cv_image):
        self.scanned_canvas.update_idletasks()
        self.update_canvas(self.scanned_canvas, cv_image, True)

    def update_canvas(self, canvas, cv_image, switch_to_scanned=False):
        img_height, img_width, _ = cv_image.shape
        scale_factor = self.canvas_width / img_width
        new_height = int(img_height * scale_factor)
        resized_image = cv2.resize(cv_image, (self.canvas_width, new_height))
        resized_display_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
        resized_display_image = Image.fromarray(resized_display_image)
        tk_resized_display_image = ImageTk.PhotoImage(resized_display_image)
        canvas.itemconfig(self.scanned_canvas_image if switch_to_scanned else self.canvas_image, image=tk_resized_display_image)
        canvas.image = tk_resized_display_image
        if switch_to_scanned:
            self.initial_frame.pack_forget()
            self.scanned_frame.pack(fill=tk.BOTH, expand=True)

    def show_initial_frame(self):
        self.scanned_frame.pack_forget()
        self.initial_frame.pack(fill=tk.BOTH, expand=True)

    def create_draggable_anchors(self, points):
        self.clear_anchors()
        self.rect_coords = points.copy()
        radius = 5
        img_height, img_width, _ = self.original_image.shape
        self.scale_factor = self.canvas_width / img_width
        for point in points:
            x, y = point.ravel()
            scaled_x = int(x * self.scale_factor)
            scaled_y = int(y * self.scale_factor)
            anchor = self.canvas.create_oval(scaled_x - radius, scaled_y - radius, scaled_x + radius, scaled_y + radius, fill='red', tags='anchor')
            self.anchors.append(anchor)
        self.canvas.tag_bind('anchor', '<ButtonPress-1>', self.start_drag)
        self.canvas.tag_bind('anchor', '<B1-Motion>', self.drag)
        self.canvas.tag_bind('anchor', '<ButtonRelease-1>', self.end_drag)

    def clear_anchors(self):
        for anchor in self.anchors:
            self.canvas.delete(anchor)
        self.anchors = []

    def start_drag(self, event):
        self.drag_data["item"] = self.canvas.find_closest(event.x, event.y)[0]
        self.drag_data["index"] = self.anchors.index(self.drag_data["item"])
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def drag(self, event):
        item_tags = self.canvas.gettags(self.drag_data["item"])
        if 'anchor' in item_tags:
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            self.canvas.move(self.drag_data["item"], dx, dy)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def end_drag(self, event):
        new_rect_coords = []
        for anchor in self.anchors:
            x1, y1, x2, y2 = self.canvas.coords(anchor)
            img_x = ((x1 + x2) / 2) / self.scale_factor
            img_y = ((y1 + y2) / 2) / self.scale_factor
            new_rect_coords.append((img_x, img_y))
        self.rect_coords = np.array(new_rect_coords, dtype=np.float32)
        self.update_rectangle_on_image()

    def update_rectangle_on_image(self):
        updated_image = self.original_image.copy()
        rect_points = []
        for i in range(len(self.rect_coords)):
            x, y = self.rect_coords[i]
            rect_points.append((int(x), int(y)))
            x, y = self.rect_coords[(i + 1) % len(self.rect_coords)]
            rect_points.append((int(x), int(y)))
        for i in range(0, len(rect_points), 2):
            cv2.line(updated_image, rect_points[i], rect_points[i + 1], (0, 255, 0), 2)
        self.image_with_rectangle = updated_image
        self.update_canvas(self.canvas, self.image_with_rectangle)

    def scan_image(self):
        if self.img is None:
            messagebox.showinfo("Information", "No image loaded.")
            return
        anchor_coords = [self.canvas.coords(anchor) for anchor in self.anchors]
        if anchor_coords:
            anchor_points = [(int((coords[0] + coords[2]) / 2), int((coords[1] + coords[3]) / 2)) for coords in anchor_coords]
            unscaled_anchor_points = np.array(anchor_points, dtype='float32') / self.scale_factor
            self.warpedImg = four_point_transform(np.array(self.img), unscaled_anchor_points)
            self.display_scanned_image(self.warpedImg)
        else:
            messagebox.showinfo("Information", "No document corners detected.")

    def save_image(self):
        if self.warpedImg is not None:
            save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")])
            if save_path:
                image_to_save = Image.fromarray(cv2.cvtColor(self.warpedImg, cv2.COLOR_BGR2RGB))
                image_to_save.save(save_path)
               
                messagebox.showinfo("Image Saved", f"Image successfully saved to {save_path}")
        else:
            messagebox.showinfo("No Image", "No image available to save.")



def main():
    window = tk.Tk()
    window.title("Document Scanner")
    window.geometry("615x968")
    app = ImageSelector(window)
    window.mainloop()

if __name__ == "__main__":
    main()
