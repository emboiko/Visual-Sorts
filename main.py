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
from synthesizer import Player, Synthesizer, Waveform


class SorterGUI:
    def __init__(self, root):
        self.master = root
        self.master.title("Visual Sorts")
        self.master.geometry("1000x550")
        self.master.update()
        width_offset, height_offset = self.get_offsets()
        self.master.geometry(f"+{width_offset}+{height_offset}")
        self.master.resizable(False, False)

        self.sort_modes = (
            "Bubble",
            "Selection",
            "Insertion",
        )
        self.sort_orders = ("Ascending","Descending")

        # Widgets:
        self.sort_mode = StringVar(self.master)
        self.sort_mode.set(self.sort_modes[0])
        self.sort_order = StringVar(self.master)
        self.sort_order.set(self.sort_orders[0])

        self.frame = Frame(self.master, relief="sunken", borderwidth=2)
        self.delay_label = Label(self.frame, text="Delay (ms):")
        self.delay_scale = Scale(
            self.frame,
            orient="horizontal",
            from_=.001,
            to=0.05,
            resolution=.001
        )
        self.delay_scale.set(0.025)
        self.mode_menu = OptionMenu(self.frame, self.sort_mode, *self.sort_modes)
        self.order_menu = OptionMenu(self.frame, self.sort_order, *self.sort_orders)
        self.sort_button = Button(self.frame, text="Sort", command=self.sort)
        self.reset_button = Button(self.frame, text="Reset", command=self.reset)
        self.canvas = Canvas(self.master, background="black")

        # Layout:
        self.master.rowconfigure(1, weight=1)
        self.master.columnconfigure(0, weight=1)

        self.frame.grid(row=0, column=0)
        self.delay_label.grid(row=0, column=0)
        self.delay_scale.grid(row=0, column=1)
        self.order_menu.grid(row=0, column=2, pady=5, padx=5)
        self.mode_menu.grid(row=0, column=3, pady=5, padx=5)
        self.sort_button.grid(row=0, column=4, pady=5, padx=5)
        self.reset_button.grid(row=0, column=5, pady=5, padx=5)
        self.canvas.grid(row=1, column=0, sticky="nsew")

        # Waveform:
        self.player = Player()
        self.player.open_stream()
        self.synthesizer = Synthesizer(
            osc1_waveform=Waveform.sine,
            osc1_volume=1.0,
            use_osc2=True,
            osc2_waveform=Waveform.sine,
            osc2_volume=1,
            osc2_freq_transpose=5.0,
        )

        self.running = False
        self.reset()
        self.master.protocol("WM_DELETE_WINDOW", self.close)


    def __str__(self):
        """
            Pretty print self w/ address.
        """
        
        return f"SorterGUI @ {hex(id(self))}"


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


    def close(self):
        """
            Callback for main window delete- prevents tkinter from crashing
            when the app is closed mid-sort.
        """

        self.reset()
        self.master.destroy()


    def reset(self):
        """
            Resets the sorting canvas with newly randomized rectangles.
        """

        self.running = False
        self.heights = [randint(0,500) for _ in range(100)]
        self.draw_canvas()


    def draw_canvas(self):
        """
            Clears, then populates the canvas with rectangles using [self.heights]
        """

        self.canvas.delete("all")
        for i, height in enumerate(self.heights):
            self.canvas.create_rectangle(i*10,500,(i*10)+10,height, fill="white")
            if self.running:
                # It would be nice to reduce the attack / artifacting,
                # for now, it sounds the way it sounds.
                self.player.play_wave(
                    self.synthesizer.generate_constant_wave(
                        height * 3,
                        self.delay_scale.get()
                    )
                )
                self.canvas.update()


    def sort(self):
        """
            Controller for sort generators
        """

        # Not everybody loves eval, but this seemed like a nifty use case.
        # User input is limited to preset data.
        code = (f"self.{self.sort_mode.get().lower()}_sort(self.heights, self.sort_order.get())")
        gen = eval(code)

        self.running = True
        while self.running:
            try:
                next(gen)
                self.draw_canvas()
            except StopIteration:
                return
        
        # If we make it out of the loop and end up here, the user
        # reset during the sort, so we re-randomize and draw once.
        self.reset()


    #####################################################################
    # If performance was actually in mind here, we would probably factor
    # the string comparison for sort_order into an ascending_X_sort()
    # and descending_X_sort(), calling accordingly. In this case, I chose
    # to avoid the duplicate code. This is only an excercise after all.
    #####################################################################


    def bubble_sort(self, nums, sort_order):
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


    def selection_sort(self, nums, sort_order):
        """
            Generator for selection sort w/ conditional for sort order
        """

        for i in range(len(nums)):
            lowest_index = i

            for j in range(i+1, len(nums)):
                if sort_order == "Ascending":
                    if nums[j] > nums[lowest_index]:
                        lowest_index = j
                else:
                    if nums[j] < nums[lowest_index]:
                        lowest_index = j
            
            nums[i], nums[lowest_index] = nums[lowest_index], nums[i]

            yield


    def insertion_sort(self, nums, sort_order):
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
