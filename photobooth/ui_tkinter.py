"""Tkinter interface styled after the procedure document's GUI mockups.

The UI owns widgets and visual state. Camera, session, and file operations are
handled by PhotoBoothApp and the workflow/storage modules.
"""

from pathlib import Path
from typing import Callable, Sequence
import tkinter as tk
from tkinter import messagebox

from PIL import Image, ImageTk

from photobooth.catalog import BoothTemplate, create_template_preview


APP_BG = "#f3f5f9"
WHITE = "#ffffff"
NAVY = "#1b3a60"
NAVY_DARK = "#143252"
TEXT = "#202936"
MUTED = "#637184"
BORDER = "#d7dee8"
PALE_BLUE = "#e9f0f7"
YELLOW = "#ffbd00"
PALE_YELLOW = "#fff3c7"
GREEN = "#23834f"
PALE_GREEN = "#e7f4eb"
RED = "#a13d37"
PALE_RED = "#fde8e6"


class PhotoBoothUI:
    """Build the single-window customer flow and forward actions to the app."""

    def __init__(
        self,
        root: tk.Tk,
        templates: Sequence[BoothTemplate],
        on_home_start: Callable[[], None],
        on_start: Callable[[dict[str, int]], None],
        on_capture: Callable[[], None],
        on_select_photo: Callable[[int], None],
        on_retake: Callable[[], None],
        on_accept_session: Callable[[], None],
        on_next_session: Callable[[], None],
        on_finish: Callable[[], None],
        on_close: Callable[[], None],
    ) -> None:
        self.root = root
        self.templates = tuple(templates)
        self._on_home_start = on_home_start
        self._on_start = on_start
        self._on_capture = on_capture
        self._on_select_photo = on_select_photo
        self._on_retake = on_retake
        self._on_accept_session = on_accept_session
        self._on_next_session = on_next_session
        self._on_finish = on_finish
        self._on_close = on_close

        self.current_screen = "welcome"
        self._image_refs: list[ImageTk.PhotoImage] = []
        self._camera_ready = False
        self._configure_window()
        self._build_shell()
        self.root.bind("<Escape>", lambda _event: self._on_close())
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _configure_window(self) -> None:
        self.root.title("Meongs Photobooth")
        self.root.geometry("1280x800")
        self.root.minsize(1024, 680)
        self.root.configure(bg=APP_BG)

    def _build_shell(self) -> None:
        """Keep the navigation bar fixed while screens change below it."""
        self.header = tk.Frame(self.root, bg=WHITE, height=82)
        self.header.pack(fill=tk.X)
        self.header.pack_propagate(False)

        logo = tk.Canvas(
            self.header,
            width=42,
            height=42,
            bg=WHITE,
            highlightthickness=0,
        )
        logo.create_oval(2, 2, 40, 40, fill=YELLOW, outline=YELLOW)
        logo.create_text(21, 21, text="M", fill=NAVY, font=("Arial", 17, "bold"))
        logo.pack(side=tk.LEFT, padx=(34, 10), pady=18)

        tk.Label(
            self.header,
            text="Meongs Photobooth",
            font=("Arial", 20, "bold"),
            fg=NAVY,
            bg=WHITE,
        ).pack(side=tk.LEFT)

        self.nav_frame = tk.Frame(self.header, bg=WHITE)
        self.nav_frame.pack(side=tk.LEFT, expand=True, padx=22)
        self.nav_labels: dict[str, tk.Label] = {}
        for key, label in (
            ("templates", "Pilih template"),
            ("photo", "Foto"),
            ("result", "Hasil"),
        ):
            nav = tk.Label(
                self.nav_frame,
                text=label,
                font=("Arial", 11),
                fg=MUTED,
                bg=WHITE,
                padx=18,
                pady=10,
            )
            nav.pack(side=tk.LEFT, padx=5)
            self.nav_labels[key] = nav

        self.camera_badge = tk.Label(
            self.header,
            text="MEMERIKSA KAMERA",
            font=("Arial", 10, "bold"),
            fg=NAVY,
            bg=PALE_BLUE,
            padx=18,
            pady=10,
        )
        self.camera_badge.pack(side=tk.RIGHT, padx=34)

        self.content = tk.Frame(self.root, bg=APP_BG)
        self.content.pack(fill=tk.BOTH, expand=True)

    def _set_active_nav(self, screen_name: str) -> None:
        active = {
            "welcome": "templates",
            "templates": "templates",
            "capture": "photo",
            "review": "photo",
            "result": "result",
        }.get(screen_name)
        for key, label in self.nav_labels.items():
            selected = key == active
            label.config(
                fg=NAVY if selected else MUTED,
                bg=PALE_BLUE if selected else WHITE,
                font=("Arial", 11, "bold" if selected else "normal"),
            )

    def set_camera_status(self, ready: bool) -> None:
        self._camera_ready = ready
        self.camera_badge.config(
            text="KAMERA SIAP" if ready else "KAMERA BELUM SIAP",
            fg=GREEN if ready else RED,
            bg=PALE_GREEN if ready else PALE_RED,
        )

    def _reset(
        self,
        screen_name: str,
        title: str,
        subtitle: str = "",
    ) -> tk.Frame:
        self.current_screen = screen_name
        self._image_refs = []
        self._set_active_nav(screen_name)
        for child in self.content.winfo_children():
            child.destroy()

        page = tk.Frame(self.content, bg=APP_BG)
        page.pack(fill=tk.BOTH, expand=True, padx=52, pady=(24, 10))
        if title:
            tk.Label(
                page,
                text=title,
                font=("Arial", 25, "bold"),
                fg=NAVY,
                bg=APP_BG,
            ).pack(anchor="w")
        if subtitle:
            tk.Label(
                page,
                text=subtitle,
                font=("Arial", 12),
                fg=MUTED,
                bg=APP_BG,
            ).pack(anchor="w", pady=(4, 14))
        self.status_label = tk.Label(
            page,
            text="",
            font=("Arial", 10),
            fg=MUTED,
            bg=APP_BG,
        )
        self.status_label.pack(side=tk.BOTTOM, anchor="w", pady=(10, 0))
        return page

    def set_status(self, message: str) -> None:
        if hasattr(self, "status_label") and self.status_label.winfo_exists():
            self.status_label.config(text=message)

    def show_welcome(self, camera_ready: bool, status_message: str) -> None:
        self.set_camera_status(camera_ready)
        page = self._reset("welcome", "")
        columns = tk.Frame(page, bg=APP_BG)
        columns.pack(fill=tk.BOTH, expand=True, pady=(18, 20))
        columns.grid_columnconfigure(0, weight=2)
        columns.grid_columnconfigure(1, weight=1)
        columns.grid_rowconfigure(0, weight=1)

        hero = tk.Frame(
            columns,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        hero.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        tk.Label(
            hero,
            text="Bikin foto seru\nbareng teman",
            font=("Arial", 36, "bold"),
            fg=NAVY,
            bg=WHITE,
            justify=tk.LEFT,
        ).pack(anchor="w", padx=42, pady=(42, 14))
        tk.Label(
            hero,
            text="Pilih template, ambil foto, lalu simpan hasil digitalnya.",
            font=("Arial", 16),
            fg=MUTED,
            bg=WHITE,
            justify=tk.LEFT,
            wraplength=580,
        ).pack(anchor="w", padx=44, pady=(0, 34))

        start_button = tk.Button(
            hero,
            text="Mulai foto",
            command=self._on_home_start,
            font=("Arial", 16, "bold"),
            fg=WHITE,
            bg=NAVY,
            activebackground=NAVY_DARK,
            relief=tk.FLAT,
            padx=34,
            pady=16,
            cursor="hand2",
            state=tk.NORMAL if camera_ready else tk.DISABLED,
            disabledforeground="#8c98a8",
        )
        start_button.pack(anchor="w", padx=42, pady=(0, 24))

        info = tk.Frame(
            columns,
            bg=PALE_YELLOW if not camera_ready else PALE_BLUE,
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        info.grid(row=0, column=1, sticky="nsew")
        tk.Label(
            info,
            text="Kamera siap" if camera_ready else "Kamera belum siap",
            font=("Arial", 21, "bold"),
            fg=NAVY if camera_ready else RED,
            bg=PALE_YELLOW if not camera_ready else PALE_BLUE,
        ).pack(anchor="w", padx=28, pady=(30, 15))
        tk.Label(
            info,
            text=(
                "Hasil foto disimpan di perangkat ini."
                if camera_ready
                else status_message
            ),
            font=("Arial", 13),
            fg=TEXT,
            bg=PALE_YELLOW if not camera_ready else PALE_BLUE,
            wraplength=280,
            justify=tk.LEFT,
        ).pack(anchor="w", padx=28, pady=(0, 20))
        tk.Label(
            info,
            text=status_message,
            font=("Arial", 10, "bold"),
            fg=GREEN if camera_ready else RED,
            bg=PALE_YELLOW if not camera_ready else PALE_BLUE,
            wraplength=280,
            justify=tk.LEFT,
        ).pack(anchor="w", padx=28, pady=(0, 28))
        self.status_label.config(text="Pilih Mulai foto untuk memilih template.")

    def show_template_selection(
        self,
        camera_ready: bool,
        status_message: str,
    ) -> None:
        self.set_camera_status(camera_ready)
        page = self._reset(
            "templates",
            "Pilih template foto kamu",
            "Qty menentukan jumlah sesi foto untuk template ini.",
        )
        layout = tk.Frame(page, bg=APP_BG)
        layout.pack(fill=tk.BOTH, expand=True)
        layout.grid_columnconfigure(0, weight=3)
        layout.grid_columnconfigure(1, weight=2)
        layout.grid_rowconfigure(0, weight=1)

        grid = tk.Frame(layout, bg=APP_BG)
        grid.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        for column in (0, 1):
            grid.grid_columnconfigure(column, weight=1, uniform="template-col")
        for row in (0, 1):
            grid.grid_rowconfigure(row, weight=1, uniform="template-row")

        self._quantity_vars: dict[str, tk.IntVar] = {}
        self._card_frames: dict[str, tk.Frame] = {}
        self._summary_items: dict[str, tk.Label] = {}

        for index, template in enumerate(self.templates):
            row, column = divmod(index, 2)
            card = tk.Frame(
                grid,
                bg=WHITE,
                highlightbackground=BORDER,
                highlightthickness=1,
            )
            card.grid(row=row, column=column, sticky="nsew", padx=7, pady=7)
            self._card_frames[template.template_id] = card
            card.bind("<Button-1>", lambda _event, t=template: self._change_quantity(t.template_id, 1))

            preview_width = max(
                220,
                min(440, int((self.root.winfo_width() - 104) * 0.6 / 2 - 40)),
            )
            preview = create_template_preview(
                template,
                (preview_width, int(preview_width * 0.41)),
            )
            preview_photo = ImageTk.PhotoImage(preview)
            self._image_refs.append(preview_photo)
            preview_label = tk.Label(card, image=preview_photo, bg=WHITE)
            preview_label.pack(fill=tk.X, padx=10, pady=(10, 6))
            preview_label.bind("<Button-1>", lambda _event, t=template: self._change_quantity(t.template_id, 1))

            card_info = tk.Frame(card, bg=WHITE)
            card_info.pack(fill=tk.X, padx=14, pady=(0, 10))
            name = tk.Label(
                card_info,
                text=template.name,
                font=("Arial", 13, "bold"),
                fg=TEXT,
                bg=WHITE,
            )
            name.pack(side=tk.LEFT, anchor="w")

            quantity = tk.IntVar(value=0)
            self._quantity_vars[template.template_id] = quantity
            quantity_controls = tk.Frame(card_info, bg=PALE_BLUE)
            quantity_controls.pack(side=tk.RIGHT)
            tk.Button(
                quantity_controls,
                text="−",
                command=lambda t=template: self._change_quantity(t.template_id, -1),
                font=("Arial", 13, "bold"),
                fg=NAVY,
                bg=PALE_BLUE,
                activebackground="#dbe6f1",
                relief=tk.FLAT,
                width=3,
                cursor="hand2",
            ).pack(side=tk.LEFT)
            tk.Label(
                quantity_controls,
                textvariable=quantity,
                font=("Arial", 12, "bold"),
                fg=NAVY,
                bg=PALE_BLUE,
                width=3,
            ).pack(side=tk.LEFT)
            tk.Button(
                quantity_controls,
                text="+",
                command=lambda t=template: self._change_quantity(t.template_id, 1),
                font=("Arial", 13, "bold"),
                fg=NAVY,
                bg=PALE_BLUE,
                activebackground="#dbe6f1",
                relief=tk.FLAT,
                width=3,
                cursor="hand2",
            ).pack(side=tk.LEFT)

        cart = tk.Frame(
            layout,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        cart.grid(row=0, column=1, sticky="nsew", padx=(4, 0), pady=7)
        tk.Label(
            cart,
            text="Keranjang",
            font=("Arial", 21, "bold"),
            fg=NAVY,
            bg=WHITE,
        ).pack(anchor="w", padx=24, pady=(22, 12))
        tk.Frame(cart, bg=BORDER, height=1).pack(fill=tk.X, padx=24)

        item_list = tk.Frame(cart, bg=WHITE)
        item_list.pack(fill=tk.X, padx=24, pady=(12, 6))
        for template in self.templates:
            line = tk.Label(
                item_list,
                text="",
                font=("Arial", 12, "bold"),
                fg=TEXT,
                bg=WHITE,
                anchor="w",
            )
            line.pack(fill=tk.X, pady=5)
            self._summary_items[template.template_id] = line

        tk.Frame(cart, bg=BORDER, height=1).pack(fill=tk.X, padx=24, pady=(6, 14))
        totals = tk.Frame(cart, bg=WHITE)
        totals.pack(fill=tk.X, padx=24)
        tk.Label(
            totals,
            text="Jumlah sesi",
            font=("Arial", 12),
            fg=MUTED,
            bg=WHITE,
        ).pack(side=tk.LEFT)
        self.session_total = tk.Label(
            totals,
            text="0 sesi",
            font=("Arial", 13, "bold"),
            fg=NAVY,
            bg=WHITE,
        )
        self.session_total.pack(side=tk.RIGHT)

        note = tk.Frame(cart, bg=PALE_BLUE)
        note.pack(fill=tk.X, padx=24, pady=(18, 14))
        tk.Label(
            note,
            text="Setiap qty = 1 sesi baru",
            font=("Arial", 12, "bold"),
            fg=NAVY,
            bg=PALE_BLUE,
        ).pack(anchor="w", padx=14, pady=(12, 4))
        tk.Label(
            note,
            text="3 foto baru + maksimal 1 retake per sesi",
            font=("Arial", 10),
            fg=MUTED,
            bg=PALE_BLUE,
        ).pack(anchor="w", padx=14, pady=(0, 12))

        self.start_button = tk.Button(
            cart,
            text="MULAI SESI FOTO",
            command=self._start_selected,
            font=("Arial", 13, "bold"),
            fg=WHITE,
            bg=NAVY,
            activebackground=NAVY_DARK,
            disabledforeground="#8c98a8",
            relief=tk.FLAT,
            padx=18,
            pady=14,
            cursor="hand2",
            state=tk.DISABLED,
        )
        self.start_button.pack(fill=tk.X, padx=24, pady=(0, 22))
        self._camera_ready = camera_ready
        self._on_order_change()
        self.status_label.config(text=status_message)

    def _change_quantity(self, template_id: str, delta: int) -> None:
        if template_id not in getattr(self, "_quantity_vars", {}):
            return
        var = self._quantity_vars[template_id]
        var.set(max(0, var.get() + delta))
        self._on_order_change()

    def _on_order_change(self) -> None:
        if not hasattr(self, "_quantity_vars"):
            return
        quantities = {
            template_id: var.get()
            for template_id, var in self._quantity_vars.items()
        }
        session_count = sum(quantities.values())
        for template in self.templates:
            quantity = quantities[template.template_id]
            summary_item = self._summary_items.get(template.template_id)
            if summary_item is not None:
                summary_item.config(
                    text=(
                        f"{template.name}  × {quantity}"
                        if quantity > 0
                        else ""
                    )
                )
            card = self._card_frames.get(template.template_id)
            if card is not None:
                card.config(
                    highlightbackground=YELLOW if quantity > 0 else BORDER,
                    highlightthickness=3 if quantity > 0 else 1,
                )
        self.session_total.config(text=f"{session_count} sesi")
        enabled = self._camera_ready and session_count > 0
        self.start_button.config(state=tk.NORMAL if enabled else tk.DISABLED)

    def _start_selected(self) -> None:
        quantities = {
            template_id: var.get()
            for template_id, var in self._quantity_vars.items()
            if var.get() > 0
        }
        self._on_start(quantities)

    def show_capture(
        self,
        session_label: str,
        capture_count: int,
        preview_image: Image.Image | None,
        action_label: str = "AMBIL FOTO",
        countdown_text: str = "",
        can_capture: bool = True,
        is_retake: bool = False,
    ) -> None:
        page = self._reset(
            "capture",
            session_label,
            "Ambil satu foto pengganti untuk sesi ini." if is_retake else "Ambil tiga foto baru untuk sesi ini.",
        )
        layout = tk.Frame(page, bg=APP_BG)
        layout.pack(fill=tk.BOTH, expand=True)
        layout.grid_columnconfigure(0, weight=3)
        layout.grid_columnconfigure(1, weight=1)
        layout.grid_rowconfigure(0, weight=1)

        preview_panel = tk.Frame(
            layout,
            bg="#202a3a",
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        preview_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 18), pady=6)
        self.preview_label = tk.Label(
            preview_panel,
            text="PRATINJAU KAMERA",
            font=("Arial", 15, "bold"),
            fg=WHITE,
            bg="#344154",
        )
        self.preview_label.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        if preview_image is not None:
            self.update_live_preview(preview_image)

        progress = tk.Frame(
            layout,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        progress.grid(row=0, column=1, sticky="nsew", pady=6)
        current_photo = min(capture_count + 1, 3)
        tk.Label(
            progress,
            text="Retake sesi ini" if is_retake else f"Foto {current_photo} dari 3",
            font=("Arial", 19, "bold"),
            fg=NAVY,
            bg=WHITE,
        ).pack(pady=(24, 20))
        self.countdown_label = tk.Label(
            progress,
            text=countdown_text or str(current_photo),
            font=("Arial", 58, "bold"),
            fg=NAVY,
            bg=WHITE,
        )
        self.countdown_label.pack(pady=(0, 6))
        self.capture_hint = tk.Label(
            progress,
            text="Bersiap mengambil retake" if is_retake else "Bersiap mengambil foto",
            font=("Arial", 12),
            fg=MUTED,
            bg=WHITE,
        )
        self.capture_hint.pack(pady=(0, 20))
        tk.Frame(progress, bg=BORDER, height=1).pack(fill=tk.X, padx=24, pady=8)
        for index in range(3):
            done = index < capture_count
            label = tk.Label(
                progress,
                text=f"{index + 1:02d}  " + ("tersimpan" if done else "menunggu"),
                font=("Arial", 11, "bold" if index == capture_count else "normal"),
                fg=GREEN if done else (NAVY if index == capture_count else MUTED),
                bg=WHITE,
            )
            label.pack(anchor="w", padx=26, pady=7)

        self.capture_button = tk.Button(
            progress,
            text=action_label,
            command=self._on_capture,
            font=("Arial", 11, "bold"),
            fg=WHITE,
            bg=NAVY,
            activebackground=NAVY_DARK,
            disabledforeground="#8c98a8",
            relief=tk.FLAT,
            padx=15,
            pady=13,
            cursor="hand2",
            state=tk.NORMAL if can_capture else tk.DISABLED,
        )
        self.capture_button.pack(fill=tk.X, padx=24, pady=(18, 18))

    def update_live_preview(self, image: Image.Image) -> None:
        if self.current_screen != "capture":
            return
        if not hasattr(self, "preview_label") or not self.preview_label.winfo_exists():
            return
        display = image.copy()
        preview_width = min(
            850,
            max(480, int((self.root.winfo_width() - 140) * 0.72)),
        )
        display.thumbnail((preview_width, 500))
        photo = ImageTk.PhotoImage(display)
        self._image_refs.append(photo)
        self.preview_label.config(image=photo, text="")
        if len(self._image_refs) > 3:
            self._image_refs = self._image_refs[-3:]

    def set_countdown(self, seconds: int, is_retake: bool = False) -> None:
        if hasattr(self, "countdown_label") and self.countdown_label.winfo_exists():
            self.countdown_label.config(text=str(seconds))
        if hasattr(self, "capture_hint") and self.capture_hint.winfo_exists():
            self.capture_hint.config(
                text="Bersiap mengambil retake" if is_retake else "Bersiap mengambil foto"
            )
        self.set_capture_enabled(False)

    def set_capture_enabled(self, enabled: bool) -> None:
        if hasattr(self, "capture_button") and self.capture_button.winfo_exists():
            self.capture_button.config(state=tk.NORMAL if enabled else tk.DISABLED)

    def show_review(
        self,
        photo_paths: Sequence[Path],
        session_label: str,
        selected_index: int | None,
        retake_available: bool,
        status_message: str = "",
    ) -> None:
        page = self._reset(
            "review",
            "Pilih foto yang ingin diganti",
            f"{session_label}  ·  Retake tersedia 1 kali",
        )
        photo_row = tk.Frame(page, bg=APP_BG)
        photo_row.pack(fill=tk.BOTH, expand=True)
        for column in (0, 1, 2):
            photo_row.grid_columnconfigure(column, weight=1, uniform="photo-col")

        for index, path in enumerate(photo_paths):
            card = tk.Frame(
                photo_row,
                bg=WHITE,
                highlightbackground=YELLOW if selected_index == index else BORDER,
                highlightthickness=3 if selected_index == index else 1,
            )
            card.grid(row=0, column=index, sticky="nsew", padx=10, pady=8)
            with Image.open(path) as source:
                image = source.convert("RGB")
                photo_width = max(
                    220,
                    min(500, (self.root.winfo_width() - 170) // 3 - 20),
                )
                image.thumbnail((photo_width, int(photo_width * 0.78)))
                photo = ImageTk.PhotoImage(image)
            self._image_refs.append(photo)
            button = tk.Button(
                card,
                image=photo,
                text=f"Foto {index + 1}" + (" · dipilih" if selected_index == index else ""),
                compound=tk.BOTTOM,
                command=lambda photo_index=index: self._on_select_photo(photo_index),
                font=("Arial", 12, "bold"),
                fg=NAVY,
                bg=WHITE,
                activebackground=WHITE,
                relief=tk.FLAT,
                cursor="hand2",
                padx=8,
                pady=8,
            )
            button.pack(fill=tk.BOTH, expand=True, padx=7, pady=7)

        actions = tk.Frame(page, bg=APP_BG)
        actions.pack(fill=tk.X, pady=(10, 2))
        instruction = tk.Frame(actions, bg=PALE_BLUE)
        instruction.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 12))
        tk.Label(
            instruction,
            text=(
                "Pilih satu foto untuk mengaktifkan Retake."
                if selected_index is None
                else ("Retake sudah digunakan untuk sesi ini." if not retake_available else "Retake akan mengganti foto yang dipilih.")
            ),
            font=("Arial", 12, "bold"),
            fg=NAVY,
            bg=PALE_BLUE,
        ).pack(anchor="w", padx=18, pady=(12, 3))
        tk.Label(
            instruction,
            text=status_message or "Tiga foto awal tetap tersimpan sebagai foto mentah.",
            font=("Arial", 10),
            fg=MUTED,
            bg=PALE_BLUE,
        ).pack(anchor="w", padx=18, pady=(0, 12))

        self.retake_button = tk.Button(
            actions,
            text="RETAKE FOTO TERPILIH",
            command=self._on_retake,
            font=("Arial", 11, "bold"),
            fg=WHITE,
            bg=NAVY,
            activebackground=NAVY_DARK,
            disabledforeground="#8c98a8",
            relief=tk.FLAT,
            padx=18,
            pady=15,
            cursor="hand2",
            state=(
                tk.NORMAL
                if selected_index is not None and retake_available
                else tk.DISABLED
            ),
        )
        self.retake_button.pack(side=tk.LEFT, padx=(0, 12))
        tk.Button(
            actions,
            text="GUNAKAN FOTO INI",
            command=self._on_accept_session,
            font=("Arial", 11, "bold"),
            fg=NAVY,
            bg=WHITE,
            activebackground=PALE_BLUE,
            highlightbackground=BORDER,
            highlightthickness=1,
            relief=tk.FLAT,
            padx=18,
            pady=15,
            cursor="hand2",
        ).pack(side=tk.RIGHT)

    def show_result(
        self,
        image_path: Path,
        session_label: str,
        transaction_id: str,
        has_next_session: bool,
        seconds_remaining: int | None = None,
    ) -> None:
        title = "Sesi selesai" if has_next_session else "Sesi terakhir selesai"
        page = self._reset("result", title, session_label)
        layout = tk.Frame(page, bg=APP_BG)
        layout.pack(fill=tk.BOTH, expand=True, pady=(4, 8))
        layout.grid_columnconfigure(0, weight=1)
        layout.grid_columnconfigure(1, weight=1)
        layout.grid_rowconfigure(0, weight=1)

        preview_panel = tk.Frame(
            layout,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        preview_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 18))
        with Image.open(image_path) as source:
            image = source.convert("RGB")
            preview_width = max(
                300,
                min(600, int((self.root.winfo_width() - 200) * 0.45)),
            )
            image.thumbnail((preview_width, 390))
            photo = ImageTk.PhotoImage(image)
        self._image_refs.append(photo)
        tk.Label(preview_panel, image=photo, bg=WHITE).pack(
            expand=True,
            padx=18,
            pady=(18, 6),
        )
        tk.Label(
            preview_panel,
            text="Hasil digital sesi",
            font=("Arial", 12, "bold"),
            fg=NAVY,
            bg=WHITE,
        ).pack(pady=(4, 18))

        details = tk.Frame(
            layout,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        details.grid(row=0, column=1, sticky="nsew")
        tk.Label(
            details,
            text="Terima kasih sudah berfoto!",
            font=("Arial", 21, "bold"),
            fg=NAVY,
            bg=WHITE,
        ).pack(anchor="w", padx=30, pady=(30, 12))
        tk.Label(
            details,
            text=(
                "Hasil sesi sudah disimpan di perangkat."
                if has_next_session
                else "Semua sesi pesanan sudah selesai dan hasilnya tersimpan di perangkat."
            ),
            font=("Arial", 13),
            fg=TEXT,
            bg=WHITE,
            wraplength=520,
            justify=tk.LEFT,
        ).pack(anchor="w", padx=30, pady=(0, 16))
        tk.Label(
            details,
            text=f"ID transaksi: {transaction_id}",
            font=("Arial", 11, "bold"),
            fg=MUTED,
            bg=WHITE,
        ).pack(anchor="w", padx=30, pady=(0, 20))

        button_row = tk.Frame(details, bg=WHITE)
        button_row.pack(fill=tk.X, side=tk.BOTTOM, padx=30, pady=30)
        if has_next_session:
            tk.Button(
                button_row,
                text="SESI BERIKUTNYA",
                command=self._on_next_session,
                font=("Arial", 13, "bold"),
                fg=WHITE,
                bg=NAVY,
                activebackground=NAVY_DARK,
                relief=tk.FLAT,
                padx=22,
                pady=16,
                cursor="hand2",
            ).pack(fill=tk.X)
        else:
            countdown = tk.Frame(button_row, bg=PALE_BLUE)
            countdown.pack(side=tk.LEFT, padx=(0, 12))
            tk.Label(
                countdown,
                text="Kembali ke awal dalam",
                font=("Arial", 10),
                fg=MUTED,
                bg=PALE_BLUE,
                padx=14,
                pady=8,
            ).pack()
            self.completion_label = tk.Label(
                countdown,
                text=f"01:00" if seconds_remaining is not None else "",
                font=("Arial", 18, "bold"),
                fg=NAVY,
                bg=PALE_BLUE,
            )
            self.completion_label.pack(pady=(0, 8))
            tk.Button(
                button_row,
                text="SELESAI",
                command=self._on_finish,
                font=("Arial", 13, "bold"),
                fg=WHITE,
                bg=NAVY,
                activebackground=NAVY_DARK,
                relief=tk.FLAT,
                padx=22,
                pady=16,
                cursor="hand2",
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)

    def set_completion_countdown(self, seconds_remaining: int) -> None:
        if hasattr(self, "completion_label") and self.completion_label.winfo_exists():
            minutes, seconds = divmod(max(0, seconds_remaining), 60)
            self.completion_label.config(text=f"{minutes:02d}:{seconds:02d}")

    def show_error(self, title: str, message: str) -> None:
        messagebox.showerror(title, message, parent=self.root)

