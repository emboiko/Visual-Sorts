from tkinter import (
    Tk,
    Canvas,
    Frame,
    Label,
    Scale,
    OptionMenu,
    Button,
    StringVar
)
from random import randint
from time import sleep


class SorterGUI:
    def __init__(self, root):
        self.master = root
        self.master.title("Visual Sorts")

        #Geometry
        self.master.geometry("1005x550")
        self.master.update()
        width_offset, height_offset = self.get_offsets()
        self.master.geometry(f"+{width_offset}+{height_offset}")
        self.master.resizable(False, False)

        #General Attrs:
        self.sort_modes = (
            "Bubble",
            "Selection",
            "Insertion",
        )

        self.sort_orders = ("Ascending","Descending")

        #Widgets:
        self.sort_mode = StringVar(self.master)
        self.sort_mode.set(self.sort_modes[0])
        self.sort_order = StringVar(self.master)
        self.sort_order.set(self.sort_orders[0])

        self.frame = Frame(self.master, relief="sunken", borderwidth=2)
        self.delay_label = Label(self.frame, text="Delay (ms):")
        self.delay_scale = Scale(self.frame, orient="horizontal", to=100, resolution=10)
        self.mode_menu = OptionMenu(self.frame, self.sort_mode, *self.sort_modes)
        self.order_menu = OptionMenu(self.frame, self.sort_order, *self.sort_orders)
        self.sort_button = Button(self.frame, text="Sort", command=self.sort)
        self.reset_button = Button(self.frame, text="Reset", command=self.reset)

        self.canvas = Canvas(self.master, background="black", width=1000, height=500)

        #Layout:
        self.master.rowconfigure(1, weight=1)
        self.master.columnconfigure(0, weight=1)

        self.frame.grid(row=0, column=0)
        self.delay_label.grid(row=0, column=0)
        self.delay_scale.grid(row=0, column=1)
        self.order_menu.grid(row=0, column=2, pady=5, padx=5)
        self.mode_menu.grid(row=0, column=3, pady=5, padx=5)
        self.sort_button.grid(row=0, column=4, pady=5, padx=5)
        self.reset_button.grid(row=0, column=5, pady=5, padx=5)

        self.canvas.grid(row=1, column=0)

        #Init
        self.reset()


    def get_offsets(self):
        """
            Returns an appropriate offset for a given tkinter toplevel,
            such that it always is created center screen on the primary display.
        """

        width_offset = int(
            (self.master.winfo_screenwidth() / 2) - (self.master.winfo_width() / 2)
        )

        height_offset = int(
            (self.master.winfo_screenheight() / 2) - (self.master.winfo_height() / 2)
        )

        return (width_offset, height_offset)


    def reset(self):
        """
            Resets the sorting canvas with newly randomized rectangles.
        """

        self.heights = [randint(0,500) for _ in range(100)]
        self.draw_gui()


    def draw_gui(self):
        """
            Clears, then populates the canvas with rectangles using [self.heights]
        """

        self.canvas.delete("all")
        for i, height in enumerate(self.heights):
            self.canvas.create_rectangle(i*10,500,(i*10)+10,height, fill="red")
        self.canvas.update()


    def sort(self):
        """
            Controller for sort generators
        """
        
        #Not everybody loves eval, but this seemed like a great use case.
        #User input is limited to preset data.
        code = (f"{self.sort_mode.get().lower()}_sort(self.heights, self.sort_order.get())")
        gen = eval(code)

        while True:
            try:
                next(gen)
                self.draw_gui()
                sleep(self.delay_scale.get() / 1000)
            except StopIteration:
                break


def bubble_sort(nums, sort_order):
    """
        Generator for bubble sort w/ conditional for sort order
    """

    swapped = True
    while swapped:
        swapped = False
        for i in range(len(nums) - 1):
            if sort_order == "Ascending":
                if nums[i] < nums[i +1]:
                    nums[i], nums[i+1] = nums[i+1], nums[i]
                    swapped = True
            else:
                if nums[i] > nums[i +1]:
                    nums[i], nums[i+1] = nums[i+1], nums[i]
                    swapped = True

        yield


def selection_sort(nums, sort_order):
    """
        Generator for selection sort w/ conditional for sort order
    """

    for i in range(len(nums)):
        lowest_index = i

        for j in range(i+1, len(nums)):
            if sort_order == "Ascending":
                if nums[j] < nums[lowest_index]:
                    lowest_index = j
            else:
                if nums[j] > nums[lowest_index]:
                    lowest_index = j
        
        nums[i], nums[lowest_index] = nums[lowest_index], nums[i]

        yield


def insertion_sort(nums, sort_order):
    """
        Generator for insertion sort w/ conditional for sort order
    """

    for i in range(1, len(nums)):
        
        inserted = nums[i]
        j = i-1

        if sort_order == "Ascending":
            while j >= 0 and nums[j] < inserted:
                nums[j+1] = nums[j]
                j -= 1

            nums[j+1] = inserted
        else:
            while j >= 0 and nums[j] > inserted:
                nums[j+1] = nums[j]
                j -= 1

            nums[j+1] = inserted

        yield


def main():
    """
        Sorts visualized with tkinter canvas

        Inspired by https://www.youtube.com/watch?v=kPRA0W1kECg
    """
    
    root = Tk()
    sorter_gui = SorterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
