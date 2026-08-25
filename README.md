# LiveParameters
**A persistent, real-time palette for managing Fusion User Parameters.**

**Version:** 1.2.2

**Author:** Ed Johnson (Making With An EdJ)

<img src="LiveParamsAppIcon.png" width="300">

## Introduction: The "Why" and "What"

If you design parametrically in Fusion, you know the struggle. It isn't just about changing numbers; it's the tedious cycle of: 

> *Modify > Change Parameters > Edit > OK > Check Model > Realize you need a change > Modify > Change Parameters...*

> **Lather. Rinse. Repeat.**

The native Fusion dialog is **modal**, meaning it **must be dismissed** to continue any real editing.

**LiveParameters** solves this by moving your parameters into a **modeless palette**.

* **Real-Time Updates:** Tweak dimensions and see your model update instantly without closing windows.
* **Workflow Efficiency:** Keep your parameters docked on the side while you design.
* **Enhanced Management:** Search, filter by favorites, rename parameters, and manage comments easier than ever before.

## ✨ What's New in v1.2.2

**Bug fix:** the Edit (✎) button could silently fail to open for a parameter whose comment contained a straight apostrophe (e.g. "what's") or a line break — fixed by properly encoding comments before they reach the edit dialog. A couple of related edge cases (an unescaped `"` in a text parameter's expression, or in an imported theme's ID) were found and fixed at the same time.

## Installation

### Manual Installation Options

This add-in requires a quick manual installation. You can choose to install it in Fusion's default directory or a custom folder of your choice.

#### Option 1: Install in the Default Fusion Directory
1. **Download:** Download the source code as a ZIP file and extract the `LiveParameters-main` folder. Rename the folder to `LiveParameters` (remove the `-main` suffix) — Fusion requires the folder name to match the add-in name exactly, so it won't run correctly if you skip this step.
Download the zip file using the green `Code` button above or simply click this link: [LiveParameters Main Branch](https://github.com/edjohnson100/LiveParameters/archive/refs/heads/main.zip)
*(Alternatively, grab the `LiveParameters-vX.Y.Z.zip` asset from the [latest Release](https://github.com/edjohnson100/LiveParameters/releases/latest) — its folder is already named `LiveParameters`, so you can skip the rename step.)*
2. **Move the Folder:** Move the entire `LiveParameters` folder into your native Fusion Scripts directory:
   * **Windows:** `%appdata%\Autodesk\Autodesk Fusion 360\API\AddIns`
     * *Note: This path is hidden by default in Windows. Copy and paste the entire path above into the File Explorer address bar to navigate there directly, bypassing the need to toggle hidden files/folders on.*
   * **Mac:** `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns`
     * *Note: `~/Library` is hidden by default on macOS as well. In Finder, press `Cmd+Shift+G` (Go to Folder), paste the path above, and press Enter to navigate there directly. (Unverified on an actual Mac as of this writing — please confirm and adjust this note if it's not accurate.)*
3. **Open Fusion:** Press `Shift + S` to open the **Scripts and Add-Ins** dialog.
4. **Run the Script:** Make sure the **Add-ins** filter checkbox is checked. You should see **LiveParameters** in the list of add-ins. You may want to check the 'Run on startup' option so it automatically runs when Fusion starts. Click the **Run** icon to execute the add-in.

#### Option 2: Install in a Custom Directory
1. **Download:** Download the source code as a ZIP file and extract the `LiveParameters-main` folder. Rename the folder to `LiveParameters` (remove the `-main` suffix) — Fusion requires the folder name to match the add-in name exactly, so it won't run correctly if you skip this step.
Download the zip file using the green `Code` button above or simply click this link: [LiveParameters Main Branch](https://github.com/edjohnson100/LiveParameters/archive/refs/heads/main.zip)
*(Alternatively, grab the `LiveParameters-vX.Y.Z.zip` asset from the [latest Release](https://github.com/edjohnson100/LiveParameters/releases/latest) — its folder is already named `LiveParameters`, so you can skip the rename step.)*
2. **Organize:** Create a dedicated folder on your computer for your Fusion tools (e.g., `Documents\Fusion_Tools`) and move the `LiveParameters` folder inside it.
3. **Open Fusion:** Press `Shift + S` to open the **Scripts and Add-Ins** dialog.
4. **Add the Add-in:** Click the grey **"+"** icon next to the search box at the top of the dialog and select **Script or add-in from device**.
5. **Locate:** Navigate to your custom folder, select the `LiveParameters` folder, and click **Select Folder**.
6. **Run the Add-in:** Make sure the **Add-ins** filter checkbox is checked. You should see **LiveParameters** in the list of add-ins. You may want to check the 'Run on startup' option so it automatically runs when Fusion starts. Click the **Run** icon to execute the add-in.

## Using LiveParameters

Once running, to open the **LiveParameters** palette window:
* Select **"Live Param"** via **Solid > Modify** menu (it will be near the bottom) to open the **LiveParameters** palette window. If you close the palette window, you can re-open it in the same way.

### The Interface

* **Search Bar:** Instantly filter your parameter list by name. No more scrolling through hundreds of parameters!
* **★ Favs Only:** Toggle this checkbox to hide everything except your "Favorite" parameters.
* **Themes:** Pick Light/Dark/Sepia from the header dropdown, or open the **Themes** tab to import/export a custom theme (JSON or a full `style.css` bundle) and adjust font family/size.

### Managing Parameters

* **Create:** Expand the **"Add Parameter"** section.
    * Supports Name, Unit (dropdown + custom), Expression, and Comments.
    * *Note: Text parameters must be enclosed in single quotes (e.g., `'MyText'`).*
* **Edit Values:** Type a new value or expression into any input box and press **Enter** (or Tab away) to apply it immediately.
* **Rename & Edit Comments:** Click the **Pencil (✎)** icon next to a parameter to open the edit dialog. You can safely rename parameters or update comments here.
* **Delete:** Click the **X** icon to remove a parameter.
    * *Safety Check:* The add-in will prevent deletion if the parameter is currently in use by the model.
* **Safety Interlock:** To prevent data loss, **LiveParameters** blocks editing while native Fusion commands (like Extrude, Fillet, or Sketch tools) are active.
    * *Tip:* If you get an error saying a command is active, **Click the Fusion Canvas** and press **ESC** to drop the active tool.

## Tech Stack

For the fellow coders and makers out there, here is how **LiveParameters** was built:

* **Language:** Python (Fusion API)
* **Interface:** HTML5 / CSS3 / JavaScript (running inside a Fusion Palette)
* **Communication:** JSON-based bridge between Python (Logic) and JavaScript (UI).

## Acknowledgements & Credits

* **Developer:** Ed Johnson ([Making With An EdJ](https://www.youtube.com/@makingwithanedj))
* **AI Assistance:** Developed with coding assistance from Google's Gemini 3 Pro model.
* **Lucy (The Cavachon):**
    ***Chief Wellness Officer & Director of Mandatory Breaks***
    * Thank you for ensuring I maintained healthy circulation by interrupting my deep coding sessions with urgent requests for play.
* **License:** Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.

---

## ❤️ Support the Maker (and Lucy!)

I develop these tools to improve my own workflows and love sharing them with the community. If you find LiveParameters useful and want to say thanks, feel free to **[buy Lucy a dog treat on Ko-fi](https://ko-fi.com/makingwithanedj)**!

***

*Happy Making!*
*— EdJ*
