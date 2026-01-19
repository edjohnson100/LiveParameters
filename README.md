# LiveParameters
**A persistent, real-time palette for managing Fusion User Parameters.**

<img src="LiveParamsAppIcon.png" width="300">

## Introduction: The "Why" and "What"

If you design parametrically in Fusion, you know the struggle. It isn't just about changing numbers; it's the tedious cycle of: 

> *Modify > Change Parameters > Edit > OK > Check Model > Realize you need a change > Modify > Change Parameters...*

> **Lather. Rinse. Repeat.**

The native Fusion dialog is **modal**, meaning it **must be dismissed** to continue any real editing.

**LiveParameters** solves this by moving your parameters into a **modeless palette**.

* **Real-Time Updates:** Tweak dimensions and see your model update instantly without closing windows.
* **Workflow Efficiency:** Keep your parameters docked on the side while you design.
* **Enhanced Management:** Search, filter by favorites, and manage comments easier than ever before.

## Installation

### Method: Manual Installation (Scripts & Add-Ins)
Since this is a Python-based add-in, you can install it directly into your Fusion API folder.

1.  **Download:** Download the source code (ZIP) from this repository and unzip it.
2.  **Locate Folder:** You should have a folder named `LiveParameters-main` containing files like `LiveParameters.manifest` and `LiveParameters.py`.
3.  **Rename Folder:** Rename the folder to  `LiveParameters`.
4.  **Move to Fusion:**
    * **Windows:** Copy the folder to:
        `%AppData%\Autodesk\Autodesk Fusion 360\API\AddIns\`
    * **Mac:** Copy the folder to:
        `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/`
5.  **Activate:**
    * Open Fusion.
    * Press `Shift+S` to open **Scripts and Add-Ins**.
    * Click the **Add-Ins** tab.
    * Select **LiveParameters** and click **Run**.
    * *(Optional)* Check **Run on Startup** to have it load automatically next time.

## Using LiveParameters

Once running, the **LiveParameters** palette will appear (defaulting to the right side). You can access it via the **Solid > Modify** panel if you close it.

### The Interface

* **Search Bar:** Instantly filter your parameter list by name. No more scrolling through hundreds of parameters!
* **★ Favs Only:** Toggle this checkbox to hide everything except your "Favorite" parameters.
* **Dark/Light Mode:** Use the toggle in the header to switch themes.

### Managing Parameters

* **Create:** Expand the **"Add Parameter"** section.
    * Supports Name, Unit (dropdown + custom), Expression, and Comments.
    * *Note: Text parameters must be enclosed in single quotes (e.g., `'MyText'`).*
* **Edit Values:** Type a new value or expression into any input box and press **Enter** (or Tab away) to apply it immediately.
* **Edit Comments:** Click the **Pencil (✎)** icon next to a parameter to update its comment.
* **Delete:** Click the **X** icon to remove a parameter.
    * *Safety Check:* The add-in will prevent deletion if the parameter is currently in use by the model.

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

***

*Happy Making!*
*— EdJ*