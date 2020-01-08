from tkinter import (
    Tk,
    Canvas,
    Frame,
    Label,
    Scale,
    OptionMenu,
    Button,
    Checkbutton,
    StringVar,
    BooleanVar
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
            "Cocktail",
            "Selection",
            "Insertion",
            "Shell",
        )
        self.sort_orders = ("Ascending","Descending")

        # Widgets:
        self.sort_mode = StringVar(self.master)
        self.sort_mode.set(self.sort_modes[2])
        self.sort_order = StringVar(self.master)
        self.sort_order.set(self.sort_orders[0])
        self.muted = BooleanVar(self.master)
        self.muted.set(1)

        self.frame = Frame(self.master, relief="sunken", borderwidth=2)
        
        self.freq_offset_label = Label(self.frame, text="Frequency Offset (hz):")
        self.freq_offset_scale = Scale(
            self.frame,
            orient="horizontal",
            from_=0,
            to=1000,
            resolution=10,
            length=200
        )
        self.freq_offset_scale.set(250)

        self.delay_label = Label(self.frame, text="Delay (sec):")
        self.delay_scale = Scale(
            self.frame,
            orient="horizontal",
            from_=.005,
            to=0.1,
            resolution=.005,
            length=200

        )
        self.delay_scale.set(0.085)
        
        self.mode_menu = OptionMenu(self.frame, self.sort_mode, *self.sort_modes)
        self.order_menu = OptionMenu(self.frame, self.sort_order, *self.sort_orders)
        self.sort_button = Button(self.frame, text="Sort", command=self.sort)
        self.reset_button = Button(self.frame, text="Reset", command=self.reset)
        self.mute_check = Checkbutton(self.frame, variable=self.muted, text="Mute")
        self.canvas = Canvas(self.master, background="black")

        # Layout:
        self.master.rowconfigure(1, weight=1)
        self.master.columnconfigure(0, weight=1)

        self.frame.grid(row=0, column=0, sticky="ew")
        self.freq_offset_label.grid(row=0, column=1)
        self.freq_offset_scale.grid(row=0, column=2)
        self.delay_label.grid(row=0, column=3)
        self.delay_scale.grid(row=0, column=4)
        self.order_menu.grid(row=0, column=5, pady=5, padx=5)
        self.mode_menu.grid(row=0, column=6, pady=5, padx=5)
        self.sort_button.grid(row=0, column=7, pady=5, padx=5)
        self.reset_button.grid(row=0, column=8, pady=5, padx=5)
        self.mute_check.grid(row=0, column=9, padx=10)
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
            
            This might not be necessary if the user isn't running the app in 
            the console, but there's still an ugly traceback going to stdout.
        """

        self.reset()
        raise SystemExit


    def reset(self):
        """
            Resets the sorting canvas with newly randomized rectangles.
        """

        self.running = False
        self.heights = [randint(0,500) for _ in range(200)]
        self.draw_canvas()


    def draw_canvas(self, tone_1=0, tone_2=0):
        """
            Clears, then populates the canvas with rectangles using [self.heights]
        """

        self.canvas.delete("all")
        for i, height in enumerate(self.heights):
            self.canvas.create_rectangle(i*5,500,(i*5)+5,height, fill="white")

        if self.running:
            # If we're muted, synthesizer still does a much better job than
            # sleep() for achieving the delay, so freq=0.
            if self.muted.get():
                self.player.play_wave(
                    self.synthesizer.generate_constant_wave(
                        0,
                        self.delay_scale.get()
                    )
                )
            else:
                # Otherwise, we'll cut the duration in half and play both tones 
                # so we hear the comparisons taking place. Heights are in range
                # 0-500 inclusive, which is at max a somewhat low frequency,
                # so we include an offset which the user can modulate.
                self.player.play_wave(
                    self.synthesizer.generate_constant_wave(
                        tone_1 + self.freq_offset_scale.get(),
                        self.delay_scale.get() / 2
                    )
                )
                self.player.play_wave(
                    self.synthesizer.generate_constant_wave(
                        tone_2 + self.freq_offset_scale.get(),
                        self.delay_scale.get() / 2
                    )
                )

        self.canvas.update()


    def sort(self):
        """
            Controller for sort generators
        """

        if not self.running:
            # Not everybody loves eval, but this seemed like a nifty use case.
            # User input is limited to preset data.
            code = (f"self.{self.sort_mode.get().lower()}_sort(self.heights, self.sort_order.get())")
            gen = eval(code)

            self.running = True
            while self.running:
                try:
                    tone_1, tone_2 = next(gen)
                    self.draw_canvas(tone_1, tone_2)
                except StopIteration:
                    self.running = False
                    return
            
            # If we make it out of the loop and end up here, the user
            # reset during the sort, so we re-randomize and draw once.
            self.reset()


    #####################################################################
    # If performance was actually in mind here, we would probably factor
    # the string comparison for sort_order into an ascending_X_sort()
    # and descending_X_sort(), calling accordingly. In this case, I chose
    # to avoid the duplicate code. This is only an excercise after all.
    # (Not to mention we're making even more assignments to yield tone values)
    #####################################################################


    def bubble_sort(self, nums, sort_order):
        """
            Generator for inplace bubble sort w/ conditional for sort order
        """

        tone_1, tone_2 = 0, 0
        swapped = True
        while swapped:
            swapped = False
            for i in range(len(nums) - 1):
                if sort_order == "Ascending":
                    if nums[i] < nums[i +1]:
                        tone_1, tone_2 = nums[i], nums[i+1]
                        nums[i], nums[i+1] = nums[i+1], nums[i]
                        swapped = True
                else:
                    if nums[i] > nums[i +1]:
                        tone_1, tone_2 = nums[i], nums[i+1]
                        nums[i], nums[i+1] = nums[i+1], nums[i]
                        swapped = True

            yield tone_1, tone_2


    def selection_sort(self, nums, sort_order):
        """
            Generator for inplace selection sort w/ conditional for sort order
        """

        tone_1, tone_2 = 0, 0

        for i in range(len(nums)):
            lowest_index = i

            for j in range(i+1, len(nums)):
                if sort_order == "Ascending":
                    if nums[j] > nums[lowest_index]:
                        lowest_index = j
                else:
                    if nums[j] < nums[lowest_index]:
                        lowest_index = j
            
            tone_1, tone_2 = nums[i], nums[lowest_index]
            nums[i], nums[lowest_index] = nums[lowest_index], nums[i]

            yield tone_1, tone_2


    def insertion_sort(self, nums, sort_order):
        """
            Generator for inplace insertion sort w/ conditional for sort order
        """

        tone_1, tone_2 = 0, 0

        for i in range(1, len(nums)):
            inserted = nums[i]
            j = i-1

            if sort_order == "Ascending":
                while j >= 0 and nums[j] < inserted:
                    nums[j+1] = nums[j]
                    j -= 1

                tone_1, tone_2 = nums[j], nums[j+1]
                nums[j+1] = inserted
            else:
                while j >= 0 and nums[j] > inserted:
                    nums[j+1] = nums[j]
                    j -= 1

                tone_1, tone_2 = nums[j], nums[j+1]
                nums[j+1] = inserted

            yield tone_1, tone_2


    def shell_sort(self, nums, sort_order):
        """
            Generator for inplace shell sort w/ conditional for sort order
        """
        
        tone_1, tone_2 = 0, 0

        n = len(nums)
        gap = n // 2
        while gap > 0:
            for i in range(gap, n):
                temp = nums[i]
                j = i
                if sort_order == "Ascending":
                    while j >= gap and nums[j - gap] < temp:
                        tone_1, tone_2 = nums[j], nums[j-gap]
                        nums[j] = nums[j - gap]
                        j -= gap
                else:
                    while j >= gap and nums[j - gap] > temp:
                        tone_1, tone_2 = nums[j], nums[j-gap]
                        nums[j] = nums[j - gap]
                        j -= gap

                nums[j] = temp
                yield tone_1, tone_2

            gap //= 2


    def cocktail_sort(self, nums, sort_order): 
        """
            Generator for inplace cocktail sort w/ conditional for sort order

            Yields twice => Longer / more thorough visualization
        """

        tone_1, tone_2 = 0, 0
        
        n = len(nums) 
        swapped = True
        start = 0
        end = n-1
        while (swapped == True): 
            swapped = False
    
            for i in range (start, end): 
                if sort_order == "Ascending":
                    if (nums[i] < nums[i + 1]) : 
                        tone_1, tone_2 = nums[i], nums[i + 1]
                        yield tone_1, tone_2
                        nums[i], nums[i + 1] = nums[i + 1], nums[i] 
                        swapped = True
                else:
                    if (nums[i] > nums[i + 1]) : 
                        tone_1, tone_2 = nums[i], nums[i + 1]
                        yield tone_1, tone_2
                        nums[i], nums[i + 1] = nums[i + 1], nums[i] 
                        swapped = True
            
            if (swapped == False): 
                break

            swapped = False    
            end = end-1
    
            for i in range(end-1, start-1, -1): 
                if sort_order == "Ascending":
                    if (nums[i] < nums[i + 1]): 
                        tone_1, tone_2 = nums[i], nums[i + 1]
                        yield tone_1, tone_2
                        nums[i], nums[i + 1] = nums[i + 1], nums[i] 
                        swapped = True
                else:
                    if (nums[i] > nums[i + 1]): 
                        tone_1, tone_2 = nums[i], nums[i + 1]
                        yield tone_1, tone_2
                        nums[i], nums[i + 1] = nums[i + 1], nums[i] 
                        swapped = True
    
            start = start + 1

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
