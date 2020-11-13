# Sorting w/ Python & Tk.Canvas

![](https://i.imgur.com/AbFt8IC.png)

![](https://i.imgur.com/SxbhAcQ.png)

- Inspired by: [15 Sorting Algorithms in 6 Minutes](https://www.youtube.com/watch?v=kPRA0W1kECg).
- More features coming in the future to further imitate the [video](https://www.youtube.com/watch?v=kPRA0W1kECg).

##### Installation:

- *(Probably create a virtual environment)*
- Find the wheel appropriate wheel for pyaudio [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio).
- `pip install wheel.whl`
- `pip install requirements.txt`

##### Dependencies:

- `numpy==1.19.3`
- `synthesizer`
- `colour`
- `PyAudio`
- `enum-compat` (if you plan to compile it with PyInstaller)

##### Usage:

`python main.py`

or

`Visual-Sorts.exe`

---

##### Todo:
- [ ] Implement many, many sorting algorithms.
- [x] Colors
- [ ] Audio artifacts / clipping
- [x] Compile Executable (https://stackoverflow.com/questions/43124775/why-python-3-6-1-throws-attributeerror-module-enum-has-no-attribute-intflag) 