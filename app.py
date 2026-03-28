import threading
import tkinter as tk
from tkinter import ttk, messagebox

import requests

API_BASE = "https://api.opendota.com/api"
TIMEOUT_SECONDS = 12


class DotaRankingGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Dota 2 Ranking Viewer")
        self.geometry("560x420")
        self.resizable(True, True)

        self.account_id_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Enter a Dota 2 account ID to begin.")

        self._build_layout()

    def _build_layout(self) -> None:
        container = ttk.Frame(self, padding=16)
        container.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(
            container,
            text="Dota 2 Player Rank Lookup",
            font=("Segoe UI", 14, "bold"),
        )
        title.pack(anchor=tk.W)

        subtitle = ttk.Label(
            container,
            text="Uses OpenDota API to display profile and rank details.",
        )
        subtitle.pack(anchor=tk.W, pady=(2, 12))

        input_row = ttk.Frame(container)
        input_row.pack(fill=tk.X)

        ttk.Label(input_row, text="Account ID:").pack(side=tk.LEFT)
        entry = ttk.Entry(input_row, textvariable=self.account_id_var)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 8))
        entry.bind("<Return>", lambda _event: self.fetch_player_data())

        self.lookup_button = ttk.Button(
            input_row,
            text="Lookup",
            command=self.fetch_player_data,
        )
        self.lookup_button.pack(side=tk.LEFT)

        status = ttk.Label(container, textvariable=self.status_var)
        status.pack(anchor=tk.W, pady=(10, 8))

        self.result_box = tk.Text(
            container,
            height=16,
            wrap=tk.WORD,
            state=tk.DISABLED,
            padx=10,
            pady=8,
        )
        self.result_box.pack(fill=tk.BOTH, expand=True)

    def _set_result_text(self, text: str) -> None:
        self.result_box.configure(state=tk.NORMAL)
        self.result_box.delete("1.0", tk.END)
        self.result_box.insert(tk.END, text)
        self.result_box.configure(state=tk.DISABLED)

    def fetch_player_data(self) -> None:
        raw_id = self.account_id_var.get().strip()
        if not raw_id.isdigit():
            messagebox.showerror("Invalid Account ID", "Please enter a numeric account ID.")
            return

        account_id = int(raw_id)
        self.lookup_button.configure(state=tk.DISABLED)
        self.status_var.set("Loading player data...")
        self._set_result_text("")

        thread = threading.Thread(
            target=self._load_player_data,
            args=(account_id,),
            daemon=True,
        )
        thread.start()

    def _load_player_data(self, account_id: int) -> None:
        try:
            profile_resp = requests.get(
                f"{API_BASE}/players/{account_id}", timeout=TIMEOUT_SECONDS
            )
            profile_resp.raise_for_status()

            wl_resp = requests.get(
                f"{API_BASE}/players/{account_id}/wl", timeout=TIMEOUT_SECONDS
            )
            wl_resp.raise_for_status()

            profile_data = profile_resp.json()
            wl_data = wl_resp.json()

            text = self._format_player_data(profile_data, wl_data)
            self.after(0, lambda: self._finish_success(text))
        except requests.RequestException as exc:
            self.after(0, lambda: self._finish_error(f"Network/API error: {exc}"))
        except ValueError as exc:
            self.after(0, lambda: self._finish_error(f"Invalid response format: {exc}"))

    def _finish_success(self, text: str) -> None:
        self.lookup_button.configure(state=tk.NORMAL)
        self.status_var.set("Player data loaded.")
        self._set_result_text(text)

    def _finish_error(self, err_msg: str) -> None:
        self.lookup_button.configure(state=tk.NORMAL)
        self.status_var.set("Failed to load player data.")
        self._set_result_text(err_msg)

    @staticmethod
    def _format_player_data(profile_data: dict, wl_data: dict) -> str:
        profile = profile_data.get("profile", {})
        mmr_estimate = profile_data.get("mmr_estimate", {})

        wins = wl_data.get("win", 0)
        losses = wl_data.get("lose", 0)
        total_games = wins + losses
        win_rate = (wins / total_games * 100) if total_games else 0.0

        rows = [
            f"Player Name: {profile.get('personaname', 'Unknown')}",
            f"Steam Profile: {profile.get('profileurl', 'N/A')}",
            f"Country: {profile.get('loccountrycode', 'N/A')}",
            f"Rank Tier: {profile_data.get('rank_tier', 'N/A')}",
            f"Leaderboard Rank: {profile_data.get('leaderboard_rank', 'N/A')}",
            f"Estimated MMR: {mmr_estimate.get('estimate', 'N/A')}",
            "",
            f"Wins: {wins}",
            f"Losses: {losses}",
            f"Total Games: {total_games}",
            f"Win Rate: {win_rate:.2f}%",
        ]

        return "\n".join(rows)


if __name__ == "__main__":
    app = DotaRankingGUI()
    app.mainloop()
