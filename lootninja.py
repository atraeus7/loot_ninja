from tkinter import *
from tkinter import filedialog
import queue
import os
import threading
import logging
import re
import time

logging.basicConfig(level=logging.ERROR)

class GuiPart:
    def __init__(self, master: Frame, q):
        self.queue = q

        self.raw_loot_frame = Frame(master, name="raw_loot")
        self.raw_loot_frame.grid(column=0, row=0, sticky=(N, W, E, S))
        self.raw_loot_frame.columnconfigure(0, weight=1)

        self.loot_bid_frame = Frame(master, name="loot_bid")
        self.loot_bid_frame.grid(column=1, row=0, sticky=(N, W, E, S))
        self.loot_bid_frame.columnconfigure(0, weight=1)

        self.items_open_frame = Frame(master, name="items_open")
        self.items_open_frame.grid(column=2, row=0, sticky=(N, W, E, S))
        self.items_open_frame.columnconfigure(0, weight=1)

        self.items_closed_frame = Frame(master, name="items_closed")
        self.items_closed_frame.grid(column=3, row=0, sticky=(N, W, E, S))
        self.items_closed_frame.columnconfigure(0, weight=1)

        self.master_looters_frame = Frame(master, borderwidth=2, relief="ridge", name="masterloot")
        self.master_looters_frame.grid(column=0, row=1, sticky=(N, W, E, S))

        self.eq_log_frame = Frame(master, name="eq_log", borderwidth=2, relief="ridge")
        self.eq_log_frame.grid(column=1, row=1, columnspan=3, sticky=(N, W, E, S))

        # Raw Loot
        self.raw_loot_label = Label(master=self.raw_loot_frame, text="Raw Loot")
        self.raw_loot_label.grid(column=0, row=0, sticky=(N, W, E, S))
        self.raw_loot_list = Listbox(master=self.raw_loot_frame, selectmode=MULTIPLE, width=30)
        self.raw_loot_list.grid(column=0, row=1, sticky=(N, W, E, S))

        self.transition_one_frame = Frame(self.raw_loot_frame, name="trans1")
        self.transition_one_frame.grid(column=1, row=1, sticky=(N, W, E, S))
        self.transition_one_frame.columnconfigure(0, weight=1)
        self.transition_one_frame.rowconfigure(0, weight=1)
        self.transition_one_frame.rowconfigure(1, weight=1)
        self.transition_one_frame.rowconfigure(2, weight=1)
        self.transition_one_f_button = Button(master=self.transition_one_frame, text=">>", command=self.raw_to_bid)
        self.transition_one_f_button.grid(column=0, row=0, sticky=(N, W, E, S))
        self.transition_one_b_button = Button(master=self.transition_one_frame, text="<<", command=self.bid_to_raw)
        self.transition_one_b_button.grid(column=0, row=1, sticky=(N, W, E, S))
        self.transition_one_x_button = Button(master=self.transition_one_frame, text="x", command=self.remove_raw)
        self.transition_one_x_button.grid(column=0, row=2, sticky=(N, W, E, S))

        # Loot to Bid
        self.loot_to_bid_label = Label(master=self.loot_bid_frame, text="Loot to Bid")
        self.loot_to_bid_label.grid(column=0, row=0, sticky=(N, W, E, S))
        self.loot_to_bid_list = Listbox(master=self.loot_bid_frame, selectmode=MULTIPLE, width=30)
        self.loot_to_bid_list.grid(column=0, row=1, sticky=(N, W, E, S))

        self.transition_two_frame = Frame(self.loot_bid_frame, name="trans2")
        self.transition_two_frame.grid(column=1, row=1, sticky=(N, W, E, S))
        self.transition_two_frame.columnconfigure(0, weight=1)
        self.transition_two_frame.rowconfigure(0, weight=1)
        self.transition_two_button = Button(master=self.transition_two_frame, text=">>", command=self.bid_to_open)
        self.transition_two_button.grid(column=0, row=0, sticky=(N, W, E, S))

        # Items Currently Open
        self.loot_bidding_label = Label(master=self.items_open_frame, text="Bids open on")
        self.loot_bidding_label.grid(column=0, row=0, sticky=(N, W, E, S))
        self.loot_open_list = Listbox(master=self.items_open_frame, selectmode=MULTIPLE, width=30)
        self.loot_open_list.grid(column=0, row=1, sticky=(N, W, E, S))

        self.transition_two_frame = Frame(self.items_open_frame, name="trans3")
        self.transition_two_frame.grid(column=1, row=1, sticky=(N, W, E, S))
        self.transition_two_frame.columnconfigure(0, weight=1)
        self.transition_two_frame.rowconfigure(0, weight=1)
        self.transition_two_button = Button(master=self.transition_two_frame, text=">>", command=self.open_to_closed)
        self.transition_two_button.grid(column=0, row=0, sticky=(N, W, E, S))

        # Items Currently Closed
        self.loot_closed_label = Label(master=self.items_closed_frame, text="Bids closed on")
        self.loot_closed_label.grid(column=0, row=0, sticky=(N, W, E, S))
        self.loot_closed_list = Listbox(master=self.items_closed_frame, selectmode=MULTIPLE, width=30)
        self.loot_closed_list.grid(column=0, row=1, sticky=(N, W, E, S))

        # Master Looters
        self.master_looters = ['You']
        self.master_looters_label = Label(master=self.master_looters_frame, text="Master Looters")
        self.master_looters_label.grid(column=0, row=0, sticky=(N, W, E, S))
        self.master_looters_list = Listbox(master=self.master_looters_frame, height=6)
        self.master_looters_list.bind('<Delete>', self.remove_looter)
        self.master_looters_list.grid(column=0, row=2, sticky=(N, W, E, S))

        self.master_looters_text = Entry(master=self.master_looters_frame, width=30)
        self.master_looters_text.bind('<Return>', self.add_looter)
        self.master_looters_text.grid(column=0, row=1, sticky=(N, W, E, S))

        # EQ Log
        self.eq_browse_frame = Frame(master=self.eq_log_frame, name="eqbrowse")
        self.eq_browse_frame.grid(column=0, row=0, sticky=(N, W, E, S))
        self.eq_log_label = Label(master=self.eq_browse_frame, text="Everquest Log File")
        self.eq_log_label.grid(column=0, row=0, padx=3, sticky=(N, W, S))
        self.eq_file_dialog_button = Button(master=self.eq_browse_frame, text="Browse", command=self.get_eq_log_file_name)
        self.eq_file_dialog_button.grid(column=1, row=0, sticky=(N, W, S))

        self.eq_file_path = StringVar(self.eq_log_frame, "None")
        self.eq_file_label = Label(self.eq_log_frame, textvariable=self.eq_file_path)
        self.eq_file_label.grid(column=0, row=1, padx=3, sticky=(N, W, S))

    def raw_to_bid(self):
        for item in self.raw_loot_list.curselection():
            self.loot_to_bid_list.insert('end', self.raw_loot_list.get(item))

        for item in reversed(self.raw_loot_list.curselection()):
            self.raw_loot_list.delete(item)

    def bid_to_raw(self):
        for item in self.loot_to_bid_list.curselection():
            self.raw_loot_list.insert('end', self.loot_to_bid_list.get(item))

        for item in reversed(self.loot_to_bid_list.curselection()):
            self.loot_to_bid_list.delete(item)

    def remove_raw(self):
        self.raw_loot_list.delete(0, 'end')

    def bid_to_open(self):
        for item in self.loot_to_bid_list.curselection():
            self.loot_open_list.insert('end', self.loot_to_bid_list.get(item))

        for item in reversed(self.loot_to_bid_list.curselection()):
            self.loot_to_bid_list.delete(item)

    def open_to_closed(self):
        for item in self.loot_open_list.curselection():
            self.loot_closed_list.insert('end', self.loot_open_list.get(item))

        for item in reversed(self.loot_open_list.curselection()):
            self.loot_open_list.delete(item)

    def add_looter(self, event):
        self.master_looters.append(self.master_looters_text.get())
        self.master_looters_list.insert('end', self.master_looters_text.get())
        self.master_looters_text.delete(0, 'end')

    def remove_looter(self, event):
        self.master_looters.remove(self.master_looters_list.get(self.master_looters_list.curselection()))
        for looter in reversed(self.master_looters_list.curselection()):
            self.master_looters_list.delete(looter)

    def get_eq_log_file_name(self):
        self.eq_file_path.set(filedialog.askopenfilename())

    def processIncoming(self):
        """Handle all messages currently in the queue, if any."""
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                # Check contents of message and do whatever is needed. As a
                # simple test, print it (in real life, you would
                # suitably update the GUI's display in a richer fashion).
                if msg[0] == 'Add Raw':
                    self.raw_loot_list.insert('end', '[' + msg[1] + '] ' + msg[2])

            except queue.Empty:
                # just on general principles, although we don't
                # expect this branch to be taken in this case
                pass

class ThreadedClient:
    """
    Launch the main part of the GUI and the worker thread. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """

    def __init__(self, master: Tk):
        """
        Start the GUI and the asynchronous threads. We are in the main
        (original) thread of the application, which will later be used by
        the GUI as well. We spawn a new thread for the worker (I/O).
        """
        self.master = master

        # Create the queue
        self.queue = queue.Queue()

        # Set up the GUI part
        self.gui = GuiPart(master, self.queue)

        self.eq_log_file_name = None
        self.eq_log_file = None

        self.master_looters = None
        self.loot_regex_list = list()

        # Set up the thread to do asynchronous I/O
        # More threads can also be created and used, if necessary
        self.running = 1
        self.thread1 = threading.Thread(target=self.lootWorker)
        self.thread1.start()

        # Start the periodic call in the GUI to check if the queue contains
        # anything
        self.periodicCall()

    def lootWorker(self):
        while self.running:
            if self.master_looters != self.gui.master_looters:
                self.master_looters = self.gui.master_looters.copy()
                self.loot_regex_list = list()
                for looter in self.master_looters:
                    self.loot_regex_list.append(re.compile(rf'({looter})(.*looted.?)(\w+.?)(\w.*)(\sfrom.*)'))

            if self.eq_log_file is None:
                if os.path.exists(self.gui.eq_file_path.get()):
                    self.eq_log_file_name = self.gui.eq_file_path.get()
                    self.eq_log_file = open(self.eq_log_file_name, 'r')
                    logging.info("Path set to: " + self.gui.eq_file_path.get())

            elif self.eq_log_file_name != self.gui.eq_file_path.get():
                self.eq_log_file.close()
                self.eq_log_file_name = self.gui.eq_file_path.get()
                self.eq_log_file = open(self.eq_log_file_name, 'r')
                logging.info("Path changed to: " + self.gui.eq_file_path.get())

            if self.eq_log_file is not None:
                line = self.eq_log_file.readline()
                if line:
                    for regex in self.loot_regex_list:
                        match = re.search(regex, line)
                        if match:
                            logging.debug("Item matched to: ", match.group(4))
                            self.queue.put(('Add Raw', match.group(1), match.group(4)))

            time.sleep(0.00001)

    def periodicCall(self):
        """
        Check every 200 ms if there is something new in the queue.
        """
        self.gui.processIncoming()
        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            import sys
            sys.exit(1)
        self.master.after(200, self.periodicCall)

    def endApplication(self):
        self.running = 0

        # # Make sure all threads have stopped execution
        self.thread1.join()

        if self.eq_log_file is not None:
            self.eq_log_file.close()


if __name__ == "__main__":
    window = Tk()
    window.title("Loot Ninja")
    mainframe = Frame(window)
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

    client = ThreadedClient(mainframe)
    window.protocol("WM_DELETE_WINDOW", client.endApplication)
    window.mainloop()