## 📄 Technical Documentation — `lnkforge.py`

![Lnkforge Banner](https://repository-images.githubusercontent.com/963398358/850600df-af13-4d69-8c81-0d4312082eed)

### 📌 Overview

This script allows the generation of `.lnk` (Windows shortcut) files that embed PowerShell commands. The payload is Base64-encoded using UTF-16BE and inserted into a modified base file (`modular_lnk.b64`). It supports a "minimal" mode where the PowerShell window executes in minimized state.

> 💡 This tool is especially useful for users who want to generate Windows `.lnk` files from Linux or Termux environments without needing access to a Windows GUI.

It also supports variants with or without icons and visible/minimized execution, using dynamic LNK templates:

- `normal` → Visible PowerShell
- `minimal` → Minimized PowerShell
- `normal-icon` → Visible PowerShell with icon
- `minimal-icon` → Minimized PowerShell with icon

---

### ⚙️ Requirements

- Python 3.x
- A `modular_lnk.b64` file containing Base64-encoded `.lnk` templates with four lines:
  - Line 0: Normal LNK (visible window)
  - Line 1: Minimal LNK (minimized window)
  - Line 2: Normal LNK with icon
  - Line 3: Minimal LNK with icon

---

### 🔧 Key Variables

| Variable           | Type   | Description |
|-------------------|--------|-------------|
| `b64_extra_bytes` | `str`  | Base64 filler string that is replaced by the embedded code. Increases memory space in the `.lnk`. |
| `max_bytes`       | `int`  | Maximum payload length, derived from `b64_extra_bytes`. |
| `buffer_`         | `str`  | Accumulates the user's input commands. |
| `minimal_`        | `bool` | Flag to determine whether to use the minimized `.lnk` template. |
| `json_lines`      | `dict` | Maps execution modes (`normal`, `minimal`, `normal-icon`, `minimal-icon`) to template lines. |

---

### 🧠 Internal Logic

#### 1. **Command Input**

- The script starts an interactive loop (`while True`) where the user types commands.
- Typing `minimal`, `normal-icon`, or `minimal-icon` changes the execution mode.
- Commands are concatenated into `buffer_` and checked to ensure the Base64 encoding stays within `max_bytes`.

#### 2. **Length Validation**

- The `check_len_or_save()` function is used to:
  - Return Base64 length (`check_ = True`)
  - Return the actual encoded payload (`check_ = False`)

#### 3. **LNK Construction**

- The script reads `modular_lnk.b64`, selects the correct template line.
- It replaces `b64_extra_bytes` with the encoded payload (`code_`).
- Padding (`=`) is adjusted to ensure Base64 validity.
- The final `.lnk` file is saved as `lnkforge_date.lnk`.

---

### 🧪 Example Usage

```bash
$ python cmd_to_lnk.py
:: CMD TO LNK :: =>> [INFO]
:: Everything you write below will be stored as a shortcut ::
...

cmd_lnk_executor >> systeminfo
cmd_lnk_executor >> ipconfig
cmd_lnk_executor >> minimal-icon
cmd_lnk_executor >> whoami
cmd_lnk_executor >> exit
```

> Output: A `.lnk` file named `lnkforge_date.lnk` will be saved. It will run `systeminfo; ipconfig; whoami;` in a minimized PowerShell window with a custom icon.

---

### ⚠️ Security Considerations

- This script can be used for offensive purposes (e.g., Windows persistence techniques). It is intended for educational or ethical hacking use only, in controlled environments.
- The generated `.lnk` files are structurally "corrupted" but remain fully functional.

---

### 🧼 Additional Tips

- It is recommended to clean line breaks from the Base64 output using: [https://pinetools.com/remove-line-breaks](https://pinetools.com/remove-line-breaks)
- You can experiment with longer payloads by replacing `b64_extra_bytes` to increase allowed size.