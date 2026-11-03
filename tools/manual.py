# FREEZE SHIMMER (Studio Wiga) - notice PDF bilingue (anglais puis francais), illustree avec le rendu reel du plugin.
# Usage : python3 tools/manual.py <fichier PDF de sortie>
# Images : tools/manual_assets/ (couverture, facade annotee et ligne d'etat reprises de la notice v1.2.0).
# La capture des menus du clic droit de la v1.2.0 (« Window size », « Reset MIDI to defaults (CC ...) ») a ete retiree :
# elle montrait l'ancien menu et le depot n'a pas d'outil de rendu (tools/render) pour la refaire.
# Polices : assets/fonts (Poppins + DejaVuSans pour les fleches). Code compile : Source/ (les copies a la racine ne servent plus).
# Contenu verifie contre Source/PluginEditor.cpp / Source/PluginProcessor.cpp (v1.3.1). Pas d'historique des versions dans le PDF.
import os, sys
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (BaseDocTemplate, PageTemplate, NextPageTemplate, Frame, Paragraph, Spacer, Image as RLImage,
                                Table, TableStyle, PageBreak, CondPageBreak, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "docs", "FreezeShimmer_Manual_EN-FR_v1.3.1.pdf")
VERSION = "1.3.1"
FONTS = os.path.join(ROOT, "assets", "fonts")
A = os.path.join(ROOT, "tools", "manual_assets")

for n, f in (("Pop", "Poppins-Regular"), ("PopL", "Poppins-Light"), ("PopM", "Poppins-Medium"), ("PopB", "Poppins-Bold"), ("DV", "DejaVuSans")):
    pdfmetrics.registerFont(TTFont(n, os.path.join(FONTS, f + ".ttf")))

ACC = colors.HexColor("#2BA9E6"); ACC_L = colors.HexColor("#8FD3F5")       # bleu glace du visuel
DARK = colors.HexColor("#0E1B2A"); GREY = colors.HexColor("#5E6B7A"); LIGHT = colors.HexColor("#E8F5FC")

st = {
    "h1": ParagraphStyle("h1", fontName="PopB", fontSize=20, leading=24, textColor=ACC, spaceAfter=8, spaceBefore=4, keepWithNext=1),
    "h2": ParagraphStyle("h2", fontName="PopM", fontSize=13, leading=17, textColor=DARK, spaceAfter=4, spaceBefore=10, keepWithNext=1),
    "h3": ParagraphStyle("h3", fontName="PopM", fontSize=10.5, leading=14, textColor=ACC, spaceAfter=2, spaceBefore=7, keepWithNext=1),
    "p": ParagraphStyle("p", fontName="Pop", fontSize=9.6, leading=14, textColor=DARK, spaceAfter=5),
    "small": ParagraphStyle("small", fontName="Pop", fontSize=8.2, leading=11.5, textColor=GREY),
    "cap": ParagraphStyle("cap", fontName="Pop", fontSize=8.2, leading=11, textColor=GREY, alignment=TA_CENTER),
    "cell": ParagraphStyle("cell", fontName="Pop", fontSize=8.4, leading=11, textColor=DARK),
    "cellb": ParagraphStyle("cellb", fontName="PopM", fontSize=8.4, leading=11, textColor=DARK),
    "cover": ParagraphStyle("cover", fontName="PopL", fontSize=34, leading=42, textColor=colors.white, alignment=TA_CENTER),
    "coversub": ParagraphStyle("coversub", fontName="Pop", fontSize=12, leading=17, textColor=colors.HexColor("#B9C6D3"), alignment=TA_CENTER),
    "coverlang": ParagraphStyle("coverlang", fontName="PopM", fontSize=8.5, leading=11, textColor=ACC_L),
}
W = A4[0] - 36 * mm

def P(t, s="p"): return Paragraph(t.replace("→", '<font name="DV">→</font>'), st[s])
def img(name, width):
    path = os.path.join(A, name); im = Image.open(path)
    return RLImage(path, width=width, height=width * im.height / im.width)
def table(rows, widths, header=True):
    data = [[P(c, "cellb" if (header and r == 0) else "cell") for c in row] for r, row in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.3, colors.HexColor("#D3E3EE")),
             ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    if header: style += [("BACKGROUND", (0, 0), (-1, 0), LIGHT), ("LINEBELOW", (0, 0), (-1, 0), 0.8, ACC)]
    t.setStyle(TableStyle(style)); return t

T = {
"en": dict(
 lang="ENGLISH", sub="Frozen Cosmic Reverb &nbsp;·&nbsp; VST3 &nbsp;·&nbsp; Windows &amp; macOS", ver="User manual &nbsp;·&nbsp; version " + VERSION,
 foot="User manual",
 intro_t="1. Presentation",
 intro=["<b>Freeze Shimmer</b> is a VST3 effect by Studio Wiga that merges two pedal ideas into one instrument: a <b>shimmer / cosmic reverb</b> inspired by the Electro-Harmonix Pico Shimmer (3 scenes, delay, modulation) and a <b>freeze / sound retainer</b> inspired by the Pico Deep Freeze (infinite sustain, layers, glissando).",
        "Play a chord, hold the footswitch and the plugin captures what it hears. Release: the sound keeps floating indefinitely while you play over it. A double-click on the footswitch gently lets it go. The engines are written from scratch to reproduce the behaviour described in the pedal manuals, not a bit-for-bit copy."],
 feat_h="Main features",
 feat=["Shimmer reverb: 8-line FDN with the octave fed back into the loop, 3 scenes (INTERGALACTIC, OFF-WORLD, ETHERDUST), echo up to 950 ms, modulation.",
       "Spectral freeze (phase vocoder): a frozen chord keeps its pitch, up to 4 layers, GLISS crossfade, LATCH / MOMENT / AUTO modes.",
       "Seven knobs with two pages (A white, B blue), MODE button with LED, footswitch, status line.",
       "MIDI Learn on every control (right-click the control); no CC is assigned by default.",
       "10 factory presets; window 60 %, 75 % or 100 % (Plugin size), default size of new windows to choose, never smaller than 60 %."],
 flow_h="Signal flow",
 flow="Input → shimmer reverb (BLEND) → freeze (captures after the shimmer, reverb included) → DRY × your signal + EFFECT × frozen sound → output. When bypassed, reverb tails fade out naturally.",
 inst_t="2. Installation",
 inst=[("Windows 11", "Unzip <b>FreezeShimmer-win64.zip</b> (GitHub Actions artifact or Release) and run <b>Install-FreezeShimmer.ps1</b> (right-click &gt; Run with PowerShell): it copies <b>Freeze Shimmer.vst3</b> into <b>C:\\Program Files\\Common Files\\VST3</b>. A standalone <b>Freeze Shimmer.exe</b> is also included."),
       ("macOS", "Unzip <b>FreezeShimmer-macos.zip</b> (universal binary, macOS 10.13 or later), then double-click <b>FreezeShimmer-VST3.pkg</b> (all users) or <b>install-freezeshimmer-mac.command</b> (copies to ~/Library/Audio/Plug-Ins/VST3, removes the quarantine). If macOS blocks it: right-click &gt; Open. On macOS, Ctrl + click also opens the right-click menu."),
       ("Reaper", "Options &gt; Preferences &gt; Plug-ins &gt; VST &gt; <b>Re-scan</b>. The plugin appears as <b>Freeze Shimmer</b> by <b>Studio Wiga</b>.")],
 ov_t="3. Interface overview",
 ov_hdr=["#", "Element", "Role"],
 ov=[["1", "DRY", "Level of your direct signal."], ["2", "EFFECT", "Level of the frozen sound."],
     ["3", "BLEND / RVB MIX", "Shimmer balance / reverb amount."], ["4", "TIME / DELAY", "Reverb decay / echo time."],
     ["5", "SPEED / LAYER", "Freeze fade time / number of layers."], ["6", "VOICE / DEPTH", "Plate → shimmer → strings / modulation depth."],
     ["7", "TONE / RATE / GLISS", "Brightness / modulation speed / crossfade between freezes."],
     ["8", "MODE button + LED", "Scene, freeze mode, page, presets; LED state."], ["9", "Footswitch", "Freeze (hold), release (double-click)."],
     ["10", "Status line", "Last value touched, scene · mode · page · FROZEN, MIDI value, MIDI Learn messages."]],
 ov_note=["Double-click a knob to reset it. Drag vertically or use the mouse wheel. Right-click a knob, MODE or the footswitch for its MIDI Learn.",
          "The LED above MODE is off when bypassed, steady blue when active and blinks blue while a freeze is running."],
 ctl_t="4. Controls",
 ctl_intro="Each knob has two functions. Page A (white labels) is the default; page B (blue labels) is reached by holding MODE for about one second.",
 kn_hdr=["Knob", "Page A", "Page B"],
 kn=[["1", "<b>DRY</b>: level of the direct, unprocessed signal.", "—"], ["2", "<b>EFFECT</b>: level of the frozen sound in the mix.", "—"],
     ["3", "<b>BLEND</b>: dry / wet balance of the shimmer stage (equal power).", "<b>RVB MIX</b>: reverb amount, 0 = delay only."],
     ["4", "<b>TIME</b>: decay from about 0.4 s to 18 s; at maximum ∞, the tank never decays.", "<b>DELAY</b>: echo time 0-950 ms, 0 = off."],
     ["5", "<b>SPEED</b>: fade-in / fade-out of the freeze, 20 ms – 3 s.", "<b>LAYER</b>: number of stacked frozen layers, 1 – 4 (LATCH)."],
     ["6", "<b>VOICE</b>: plate (0-25 %) → shimmer → strings (75-100 %).", "<b>DEPTH</b>: modulation depth of the reverb."],
     ["7", "<b>TONE</b>: brightness of the wet signal.", "<b>RATE</b>: modulation speed, 0.15 – 5 Hz."]],
 kn_note="<b>GLISS</b> (crossfade between two freezes, 20 ms – 5 s) can replace TONE / RATE on knob 7: right-click the knob &gt; <b>GLISS (freeze)</b>; <b>TONE / RATE (suit la page)</b> brings it back. SPEED tip: low = instant, percussive capture; high = slow bloom and long release.",
 sc_h="Shimmer scenes",
 sc=[["INTERGALACTIC (green)", "Classic shimmer: an octave-up voice recirculates inside the reverb loop. VOICE morphs plate → shimmer → strings."],
     ["OFF-WORLD (orange)", "Softer, darker shimmer with stronger modulation; in the upper half, VOICE adds vintage synth textures from detuned octaves."],
     ["ETHERDUST (red)", "Glitchy shimmer with random delay times, from granular sparkles to distinct echoes. Lower RVB MIX = more stutter."]],
 md_h="MODE button", md_hdr=["Gesture", "Effect"],
 md=[["Click", "Next scene"], ["Shift + click", "Next freeze mode (LATCH · MOMENT · AUTO)"], ["Hold about 1 s", "Toggle page A / B"],
     ["Mouse wheel", "Previous / next factory preset"], ["Right-click", "MIDI Learn of SCENE and FREEZE MODE, then the full menu"]],
 fz_t="5. Freeze and footswitch",
 fz_intro="The freeze engine is a phase-vocoder spectral freeze (FFT 4096): it keeps both magnitude and phase advance of every bin, so a frozen chord holds its pitch.",
 fz_hdr=["Mode", "Behaviour"],
 fz=[["LATCH (default)", "Hold the footswitch: the plugin captures what it hears. Release: the sound is sustained forever, play over it. Double-click: the freeze fades out over the SPEED time. Each new capture adds a layer (up to LAYER) or glides to the new sound (GLISS)."],
     ["MOMENT", "Frozen only while the footswitch is held."],
     ["AUTO", "Captures automatically at every detected attack; GLISS sets the morph from one note to the next. A click on the footswitch arms / disarms auto-capture."]],
 fz_note="Change the mode with Shift + click on MODE, the right-click menu (<b>Mode freeze</b>) or MIDI. Bypass: right-click &gt; <b>Effet actif (bypass si decoche)</b> or MIDI (ENGAGE). Stop a freeze: double-click, right-click &gt; <b>Arreter le freeze</b> or MIDI (RELEASE FREEZE).",
 midi_t="6. MIDI",
 midi_intro="Freeze Shimmer listens on the channel chosen in right-click &gt; <b>Canal MIDI</b> (OMNI by default, or 1-16). In Reaper, arm the track with your MIDI input and monitoring on. <b>No CC is assigned by default</b>: every control is assigned with MIDI Learn. All parameters are also automatable from the DAW.",
 learn_h="MIDI Learn",
 learn=["<b>Right-click a control</b>: a knob (the parameter of the page shown, or GLISS on knob 7), the MODE button (SCENE and FREEZE MODE) or the footswitch (FOOTSWITCH and RELEASE FREEZE). The menu starts with <b>MIDI Learn: &lt;control&gt; (no CC)</b> (or the learnt CC, e.g. <b>(CC 24)</b>). Choose it, then move an expression pedal or press a MIDI button: the first CC received is assigned. The learning message itself does not change the sound.",
        "The status line shows <b>MIDI LEARN: move a control for &lt;control&gt;</b>, then <b>&lt;control&gt; = CC n</b> for 2 seconds.",
        "<b>Clear MIDI: &lt;control&gt;</b> removes the assignment; <b>Cancel MIDI learn</b> (or choosing the same MIDI Learn again) stops waiting.",
        "A CC number drives only one control: learning a CC already used elsewhere removes it from the other control.",
        "Right-click &gt; <b>MIDI Learn</b> submenu: <b>Learn: &lt;control&gt; (no CC)</b> or with its learnt CC for all 18 functions, <b>Cancel MIDI learn</b> (while waiting) and <b>Clear all MIDI assignments</b>, which removes every assignment. <b>Table MIDI...</b> shows the current assignments.",
        "Assignments are <b>saved with your project</b>. A project made with an earlier version that still used the former factory numbers (CC 20-32, 102-106) opens with no assignment: learn the controls you need again. A project in which you had changed an assignment keeps its assignments as saved. The sustain pedal is no longer a footswitch by itself: learn it on FOOTSWITCH if you want to freeze with it."],
 lt_hdr=["Control", "Type"],
 lt=[["DRY, EFFECT, BLEND, RVB MIX, TIME, DELAY, SPEED", "Continuous 0-127"], ["LAYER, VOICE, DEPTH, TONE, RATE, GLISS", "Continuous 0-127"],
     ["SCENE", "Selector, 3 positions: 0-42 INTERGALACTIC, 43-85 OFF-WORLD, 86-127 ETHERDUST"],
     ["FREEZE MODE", "Selector, 3 positions: LATCH, MOMENT, AUTO"],
     ["FOOTSWITCH", "Footswitch, momentary: 64 and above = pressed, below 64 = released (hold / release like the real footswitch)"],
     ["ENGAGE", "Switch, latching: 64 and above = effect on, below 64 = bypass"], ["RELEASE FREEZE", "Trigger: 64 and above stops the freeze"],
     ["Factory presets", "Program Change 0-9 = presets 1 to 10 (always active, nothing to learn)"]],
 st_cap="Status line during MIDI Learn: waiting, then confirmation.",
 win_t="7. Window and status line",
 win=["The window opens at the default size and can never be made smaller than 60 %. Right-click the pedal &gt; <b>Plugin size</b>: <b>60 %</b>, <b>75 %</b> or <b>100 %</b> resizes this window, with <b>(default)</b> shown next to the default size you chose; you can also drag the corner up to 150 %. At the bottom of the same menu, <b>Default size (new windows)</b> chooses the size at which every new Freeze Shimmer window opens (a setting shared by all instances and saved on the computer, in Studio Wiga/Freeze Shimmer/settings.xml of your user data folder); the open window takes that size at once.",
      "The size of each window (chosen in the menu or with the corner) is saved with your project and stays the priority for that instance when the project is reopened; a new instance opens at the default size.",
      "The status line under the FREEZE SHIMMER plate shows the last parameter touched with its readable value (%, s, ms, Hz), the state scene · mode · page · FROZEN, and on the right the learnt CC with the matching MIDI value (e.g. <b>CC12 = 70</b>; <b>noCC</b> while the control is not assigned). It turns green when the value came from MIDI; the value on the left is white for page A and blue for page B. MIDI Learn messages appear there in green."],
 rc_hdr=["Right-click menu (MODE / footswitch)", "Use"],
 rc=[["MIDI Learn / Clear MIDI", "At the top, for the control you clicked."], ["Presets d'usine", "The 10 factory presets."],
     ["Plugin size", "60 %, 75 %, 100 % (“(default)” next to the default size), then Default size (new windows)."],
     ["Scene (shimmer) / Mode freeze", "Choose the scene / freeze mode."], ["Boutons : page A / page B", "Knob page."],
     ["Effet actif (bypass si decoche)", "Effect on / bypass."], ["Arreter le freeze", "Stops the freeze."], ["Canal MIDI", "OMNI or 1-16."],
     ["MIDI Learn", "Learn for every function, Cancel MIDI learn, Clear all MIDI assignments."], ["Table MIDI...", "Current CC assignments."]],
 rc_note="Right-click a knob (1 to 6) or an empty area of the pedal: its MIDI Learn (on a knob), Plugin size and the MIDI Learn submenu. Right-click knob 7: its MIDI Learn and the TONE / RATE / GLISS choice.",
 pre_t="8. Presets",
 pre="Ten starting points: mouse wheel over MODE, right-click &gt; <b>Presets d'usine</b>, the host program list or MIDI Program Change 0-9. CLEAN PLATE is the default sound of a new instance.",
 pre_hdr=["#", "Preset", "Scene · mode", "TIME", "DELAY", "LAYER", "VOICE", "Character"],
 presets=[["1", "CLEAN PLATE", "INTERGALACTIC · LATCH", "1.3 s", "OFF", "1", "PLATE", "Short, clean plate, no shimmer: neutral starting point."],
          ["2", "GLACIAL PAD", "INTERGALACTIC · LATCH", "10.7 s", "OFF", "2", "PLATE", "Long crystalline pad, pure reverb tail (VOICE plate)."],
          ["3", "INFINITE COSMOS", "INTERGALACTIC · LATCH", "6.5 s", "OFF", "3", "PLATE", "Wide luminous shimmer, 6.5 s tail."],
          ["4", "TAPE ECHO SHIMMER", "INTERGALACTIC · LATCH", "2.8 s", "765 ms", "1", "PLATE", "Modulated tape-style echo (765 ms) that shimmers, 50 % reverb."],
          ["5", "ETHERDUST GLITCH", "ETHERDUST · LATCH", "2.3 s", "522 ms", "1", "PLATE", "Random stutters and glittering granular sparkle."],
          ["6", "FROZEN DRONE", "INTERGALACTIC · LATCH", "4.1 s", "OFF", "4", "PLATE", "Four frozen layers gliding between captures: an endless drone."],
          ["7", "AUTO FREEZE SWELL", "INTERGALACTIC · AUTO", "6.0 s", "OFF", "1", "SHIMMER 25 %", "Auto-capture on every attack with soft morphing."],
          ["8", "DARK CATHEDRAL", "OFF-WORLD · LATCH", "14.0 s", "OFF", "2", "PLATE", "Dark, enormous cathedral, rolled-off top."],
          ["9", "TRUE DELAY", "INTERGALACTIC · LATCH", "1.3 s", "428 ms", "1", "PLATE", "Clean true delay: reverb off (RVB MIX 0), about 430 ms."],
          ["10", "FROZEN PLATE", "INTERGALACTIC · LATCH", "5.1 s", "OFF", "2", "PLATE", "Deep plate (about 5 s) under a latched freeze."]],
 tips_t="9. Tips",
 tips=["<b>Reaper chain</b>: guitar track &gt; tuner &gt; drive &gt; amp sim &gt; Freeze Shimmer &gt; mixer. Like a reverb pedal in an effects loop, it sounds best after the amp; before the amp sim it works too, with a more saturated, “pedalboard” character.",
       "<b>Low-tuned 7-string</b>: freeze a low chord with SPEED high and play leads over it; keep TONE below noon and VOICE on PLATE so the low end stays clean, and use OFF-WORLD for darker shimmer.",
       "<b>Nothing freezes?</b> Check that the LED is lit and EFFECT is up. In MOMENT, keep the footswitch held.",
       "<b>Too much reverb?</b> Lower BLEND (page A) or RVB MIX (page B), or TIME.",
       "<b>Freeze too abrupt?</b> Raise SPEED, and GLISS to blend successive captures.",
       "<b>With a Chocolate Plus</b>: learn FOOTSWITCH on a momentary button (hold to freeze), RELEASE FREEZE on another, and BLEND or TIME on an expression pedal."],
 ts_h="Troubleshooting", ts_hdr=["Problem", "Solution"],
 ts=[["MIDI not responding", "Check Canal MIDI (OMNI) and that the track receives MIDI; no CC is assigned by default: right-click the control &gt; MIDI Learn. Some hosts do not send MIDI to effects: use parameter mapping."],
     ["A control reacts to the wrong pedal", "Right-click the control &gt; Clear MIDI, or MIDI Learn &gt; Clear all MIDI assignments."],
     ["The sustain pedal does not freeze", "No CC is assigned by default: right-click the footswitch &gt; MIDI Learn: FOOTSWITCH, then press the sustain pedal."],
     ["Window too big or small", "Right-click the pedal &gt; Plugin size, or drag the corner; Default size (new windows) sets the size of new windows."]],
 tech_t="10. Specifications",
 tech=[["Format", "VST3 64-bit · Windows 11 · macOS 10.13+ universal (Apple Silicon + Intel); standalone app on Windows"],
       ["Shimmer", "8-line FDN (Householder), input diffusion, damping, modulation, octave in the loop; TIME max = frozen tank"],
       ["Freeze", "Phase-vocoder spectral freeze, FFT 4096, 75 % overlap, up to 4 layers"],
       ["Latency", "None reported (the freeze needs 1-3 frames of 21 ms to reach full level)"],
       ["Presets", "10 factory presets, Program Change 0-9"],
       ["MIDI", "MIDI Learn on 18 functions, no CC assigned by default, channel OMNI / 1-16; assignments saved with the project"],
       ["Window", "60 % / 75 % / 100 % (Plugin size), default size of new windows to choose, resizable by the corner up to 150 %, never smaller than 60 %"],
       ["Stability", "Windows anti-freeze v2: the interface never blocks the host"], ["Version", VERSION]],
 legal="Inspired by the Electro-Harmonix Pico Shimmer and Pico Deep Freeze; independent project, not affiliated with Electro-Harmonix. Built with JUCE (GPL-3.0). Artwork © Studio Wiga."),
"fr": dict(
 lang="FRANÇAIS", sub="Frozen Cosmic Reverb &nbsp;·&nbsp; VST3 &nbsp;·&nbsp; Windows &amp; macOS", ver="Notice d'utilisation &nbsp;·&nbsp; version " + VERSION,
 foot="Notice d'utilisation",
 intro_t="1. Présentation",
 intro=["<b>Freeze Shimmer</b> est un effet VST3 Studio Wiga qui réunit deux idées de pédales en un seul instrument : une <b>reverb shimmer / cosmique</b> inspirée de l'Electro-Harmonix Pico Shimmer (3 scènes, retard, modulation) et un <b>freeze / sound retainer</b> inspiré de la Pico Deep Freeze (sustain infini, couches, glissando).",
        "Joue un accord, maintiens le footswitch et le plugin capture ce qu'il entend. Relâche : le son flotte indéfiniment pendant que tu joues par-dessus. Un double-clic sur le footswitch le laisse partir en douceur. Les moteurs sont écrits de zéro pour reproduire le comportement décrit dans les manuels des pédales, pas une copie bit à bit."],
 feat_h="Points forts",
 feat=["Reverb shimmer : FDN à 8 lignes avec l'octave réinjectée dans la boucle, 3 scènes (INTERGALACTIC, OFF-WORLD, ETHERDUST), écho jusqu'à 950 ms, modulation.",
       "Freeze spectral (vocodeur de phase) : un accord figé garde sa hauteur, jusqu'à 4 couches, fondu GLISS, modes LATCH / MOMENT / AUTO.",
       "Sept potards sur deux pages (A blanche, B bleue), bouton MODE avec LED, footswitch, ligne d'état.",
       "MIDI Learn sur toutes les commandes (clic droit sur la commande) ; aucun CC n'est assigné par défaut.",
       "10 presets d'usine ; fenêtre 60 %, 75 % ou 100 % (Plugin size), taille par défaut des nouvelles fenêtres au choix, jamais plus petite que 60 %."],
 flow_h="Chemin du signal",
 flow="Entrée → reverb shimmer (BLEND) → freeze (capture après le shimmer, reverb comprise) → DRY × ton signal + EFFECT × son figé → sortie. En bypass, les queues de reverb s'éteignent naturellement.",
 inst_t="2. Installation",
 inst=[("Windows 11", "Dézippe <b>FreezeShimmer-win64.zip</b> (artefact GitHub Actions ou Release) et lance <b>Install-FreezeShimmer.ps1</b> (clic droit &gt; Exécuter avec PowerShell) : il copie <b>Freeze Shimmer.vst3</b> dans <b>C:\\Program Files\\Common Files\\VST3</b>. Une application autonome <b>Freeze Shimmer.exe</b> est aussi fournie."),
       ("macOS", "Dézippe <b>FreezeShimmer-macos.zip</b> (binaire universel, macOS 10.13 ou plus), puis double-clique sur <b>FreezeShimmer-VST3.pkg</b> (tous les utilisateurs) ou sur <b>install-freezeshimmer-mac.command</b> (copie dans ~/Library/Audio/Plug-Ins/VST3, retire la quarantaine). Si macOS bloque : clic droit &gt; Ouvrir. Sous macOS, Ctrl + clic ouvre aussi le menu du clic droit."),
       ("Reaper", "Options &gt; Preferences &gt; Plug-ins &gt; VST &gt; <b>Re-scan</b>. Le plugin apparaît sous le nom <b>Freeze Shimmer</b>, fabricant <b>Studio Wiga</b>.")],
 ov_t="3. Vue d'ensemble de l'interface",
 ov_hdr=["#", "Élément", "Rôle"],
 ov=[["1", "DRY", "Niveau du son direct."], ["2", "EFFECT", "Niveau du son figé."],
     ["3", "BLEND / RVB MIX", "Dosage du shimmer / quantité de reverb."], ["4", "TIME / DELAY", "Déclin de la reverb / temps d'écho."],
     ["5", "SPEED / LAYER", "Temps de fondu du freeze / nombre de couches."], ["6", "VOICE / DEPTH", "Plate → shimmer → cordes / profondeur de modulation."],
     ["7", "TONE / RATE / GLISS", "Brillance / vitesse de modulation / fondu entre deux freezes."],
     ["8", "Bouton MODE + LED", "Scène, mode de freeze, page, presets ; état de la LED."], ["9", "Footswitch", "Freeze (maintien), relâche (double-clic)."],
     ["10", "Ligne d'état", "Dernière valeur touchée, scène · mode · page · FROZEN, valeur MIDI, messages du MIDI Learn."]],
 ov_note=["Double-clic sur un potard : valeur par défaut. Glisse verticalement ou utilise la molette. Clic droit sur un potard, MODE ou le footswitch : son MIDI Learn.",
          "La LED au-dessus de MODE est éteinte en bypass, bleu fixe quand l'effet est actif et clignote en bleu pendant un freeze."],
 ctl_t="4. Commandes",
 ctl_intro="Chaque potard a deux fonctions. La page A (étiquettes blanches) est celle par défaut ; la page B (étiquettes bleues) s'obtient en maintenant MODE environ une seconde.",
 kn_hdr=["Potard", "Page A", "Page B"],
 kn=[["1", "<b>DRY</b> : niveau du signal direct, non traité.", "—"], ["2", "<b>EFFECT</b> : niveau du son figé dans le mélange.", "—"],
     ["3", "<b>BLEND</b> : dosage direct / effet de l'étage shimmer (puissance constante).", "<b>RVB MIX</b> : quantité de reverb, 0 = retard seul."],
     ["4", "<b>TIME</b> : déclin d'environ 0,4 s à 18 s ; au maximum ∞, la réverb ne s'éteint plus.", "<b>DELAY</b> : temps d'écho 0-950 ms, 0 = coupé."],
     ["5", "<b>SPEED</b> : fondu d'entrée / de sortie du freeze, 20 ms – 3 s.", "<b>LAYER</b> : nombre de couches figées empilées, 1 – 4 (LATCH)."],
     ["6", "<b>VOICE</b> : plate (0-25 %) → shimmer → cordes (75-100 %).", "<b>DEPTH</b> : profondeur de modulation de la reverb."],
     ["7", "<b>TONE</b> : brillance du signal traité.", "<b>RATE</b> : vitesse de modulation, 0,15 – 5 Hz."]],
 kn_note="<b>GLISS</b> (fondu entre deux freezes, 20 ms – 5 s) peut remplacer TONE / RATE sur le potard 7 : clic droit sur le potard &gt; <b>GLISS (freeze)</b> ; <b>TONE / RATE (suit la page)</b> le rétablit. Astuce SPEED : bas = capture instantanée et percussive ; haut = éclosion lente et longue relâche.",
 sc_h="Scènes shimmer",
 sc=[["INTERGALACTIC (vert)", "Shimmer classique : une voix à l'octave supérieure tourne dans la boucle de reverb. VOICE passe de plate à shimmer puis cordes."],
     ["OFF-WORLD (orange)", "Shimmer plus doux et plus sombre, modulation renforcée ; dans la moitié haute, VOICE ajoute des textures de synthé vintage (octaves désaccordées)."],
     ["ETHERDUST (rouge)", "Shimmer glitch à temps de retard aléatoires, des scintillements granulaires aux échos distincts. RVB MIX bas = plus de bégaiements."]],
 md_h="Bouton MODE", md_hdr=["Geste", "Effet"],
 md=[["Clic", "Scène suivante"], ["Maj + clic", "Mode de freeze suivant (LATCH · MOMENT · AUTO)"], ["Maintien environ 1 s", "Bascule page A / B"],
     ["Molette", "Preset d'usine précédent / suivant"], ["Clic droit", "MIDI Learn de SCENE et FREEZE MODE, puis le menu complet"]],
 fz_t="5. Freeze et footswitch",
 fz_intro="Le moteur de freeze est un freeze spectral à vocodeur de phase (FFT 4096) : il garde la magnitude et l'avance de phase de chaque bande, donc un accord figé garde sa hauteur.",
 fz_hdr=["Mode", "Comportement"],
 fz=[["LATCH (par défaut)", "Maintiens le footswitch : le plugin capture ce qu'il entend. Relâche : le son est tenu à l'infini, joue par-dessus. Double-clic : le freeze s'éteint en fondu (durée SPEED). Chaque nouvelle capture ajoute une couche (jusqu'à LAYER) ou glisse vers le nouveau son (GLISS)."],
     ["MOMENT", "Le son n'est figé que tant que le footswitch est maintenu."],
     ["AUTO", "Capture automatique à chaque attaque détectée ; GLISS règle le passage d'une note à la suivante. Un clic sur le footswitch arme / désarme l'auto-capture."]],
 fz_note="Change de mode par Maj + clic sur MODE, le menu du clic droit (<b>Mode freeze</b>) ou le MIDI. Bypass : clic droit &gt; <b>Effet actif (bypass si decoche)</b> ou MIDI (ENGAGE). Arrêter un freeze : double-clic, clic droit &gt; <b>Arreter le freeze</b> ou MIDI (RELEASE FREEZE).",
 midi_t="6. MIDI",
 midi_intro="Freeze Shimmer écoute le canal choisi dans clic droit &gt; <b>Canal MIDI</b> (OMNI par défaut, ou 1-16). Dans Reaper, arme la piste avec ton entrée MIDI et active le monitoring. <b>Aucun CC n'est assigné par défaut</b> : chaque commande s'assigne par MIDI Learn. Tous les paramètres sont aussi automatisables depuis le DAW.",
 learn_h="MIDI Learn",
 learn=["<b>Clic droit sur une commande</b> : un potard (le paramètre de la page affichée, ou GLISS sur le potard 7), le bouton MODE (SCENE et FREEZE MODE) ou le footswitch (FOOTSWITCH et RELEASE FREEZE). Le menu commence par <b>MIDI Learn: &lt;commande&gt; (no CC)</b> (ou le CC appris, par ex. <b>(CC 24)</b>). Choisis-le puis bouge une pédale d'expression ou appuie sur un bouton MIDI : le premier CC reçu est affecté. Ce message d'apprentissage ne modifie pas le son.",
        "La ligne d'état affiche <b>MIDI LEARN: move a control for &lt;commande&gt;</b>, puis <b>&lt;commande&gt; = CC n</b> pendant 2 secondes.",
        "<b>Clear MIDI: &lt;commande&gt;</b> retire l'affectation ; <b>Cancel MIDI learn</b> (ou un nouveau choix du même MIDI Learn) annule l'attente.",
        "Un numéro de CC ne pilote qu'une commande : apprendre un CC déjà utilisé le retire de l'autre commande.",
        "Clic droit &gt; sous-menu <b>MIDI Learn</b> : <b>Learn: &lt;commande&gt; (no CC)</b> ou avec son CC appris pour les 18 fonctions, <b>Cancel MIDI learn</b> (pendant l'attente) et <b>Clear all MIDI assignments</b>, qui efface toutes les affectations. <b>Table MIDI...</b> affiche les affectations en cours.",
        "Les affectations sont <b>sauvegardées avec le projet</b>. Un projet fait avec une version précédente qui utilisait encore les anciens numéros d'usine (CC 20-32, 102-106) s'ouvre sans aucune affectation : réapprends les commandes voulues. Un projet où tu avais changé une affectation garde ses affectations telles qu'enregistrées. La pédale de sustain n'est plus un footswitch d'office : apprends-la sur FOOTSWITCH pour figer le son avec elle."],
 lt_hdr=["Commande", "Type"],
 lt=[["DRY, EFFECT, BLEND, RVB MIX, TIME, DELAY, SPEED", "Continu 0-127"], ["LAYER, VOICE, DEPTH, TONE, RATE, GLISS", "Continu 0-127"],
     ["SCENE", "Sélecteur 3 positions : 0-42 INTERGALACTIC, 43-85 OFF-WORLD, 86-127 ETHERDUST"],
     ["FREEZE MODE", "Sélecteur 3 positions : LATCH, MOMENT, AUTO"],
     ["FOOTSWITCH", "Footswitch momentané : 64 et plus = enfoncé, moins de 64 = relâché (maintien / relâche comme le vrai footswitch)"],
     ["ENGAGE", "Bascule à accrochage : 64 et plus = effet actif, moins de 64 = bypass"], ["RELEASE FREEZE", "Déclencheur : 64 et plus arrête le freeze"],
     ["Presets d'usine", "Program Change 0-9 = presets 1 à 10 (toujours actif, rien à apprendre)"]],
 st_cap="Ligne d'état pendant le MIDI Learn : attente, puis confirmation.",
 win_t="7. Fenêtre et ligne d'état",
 win=["La fenêtre s'ouvre à la taille par défaut et ne peut jamais être plus petite que 60 %. Clic droit sur la pédale &gt; <b>Plugin size</b> : <b>60 %</b>, <b>75 %</b> ou <b>100 %</b> redimensionne cette fenêtre, et <b>(default)</b> est indiqué à côté de la taille par défaut choisie ; tu peux aussi tirer le coin jusqu'à 150 %. En bas du même menu, <b>Default size (new windows)</b> choisit la taille d'ouverture de toutes les nouvelles fenêtres de Freeze Shimmer (réglage commun à toutes les instances, enregistré sur l'ordinateur, dans Studio Wiga/Freeze Shimmer/settings.xml du dossier de données de l'utilisateur) ; la fenêtre ouverte prend aussitôt cette taille.",
      "La taille de chaque fenêtre (choisie dans le menu ou au coin) est enregistrée avec le projet et reste prioritaire pour cette instance à la réouverture du projet ; une nouvelle instance s'ouvre à la taille par défaut.",
      "La ligne d'état sous l'encadré FREEZE SHIMMER affiche le dernier paramètre touché avec sa valeur lisible (%, s, ms, Hz), l'état scène · mode · page · FROZEN, et à droite le CC appris avec la valeur MIDI correspondante (ex. <b>CC12 = 70</b> ; <b>noCC</b> tant que la commande n'est pas assignée). Elle passe en vert quand la valeur vient du MIDI ; la valeur de gauche est blanche pour la page A et bleue pour la page B. Les messages du MIDI Learn s'y affichent en vert."],
 rc_hdr=["Menu du clic droit (MODE / footswitch)", "Rôle"],
 rc=[["MIDI Learn / Clear MIDI", "En tête, pour la commande cliquée."], ["Presets d'usine", "Les 10 presets d'usine."],
     ["Plugin size", "60 %, 75 %, 100 % (« (default) » à côté de la taille par défaut), puis Default size (new windows)."],
     ["Scene (shimmer) / Mode freeze", "Choix de la scène / du mode de freeze."], ["Boutons : page A / page B", "Page des potards."],
     ["Effet actif (bypass si decoche)", "Effet actif / bypass."], ["Arreter le freeze", "Arrête le freeze."], ["Canal MIDI", "OMNI ou 1-16."],
     ["MIDI Learn", "Learn pour chaque fonction, Cancel MIDI learn, Clear all MIDI assignments."], ["Table MIDI...", "Affectations CC en cours."]],
 rc_note="Clic droit sur un potard (1 à 6) ou sur une zone vide de la pédale : son MIDI Learn (sur un potard), Plugin size et le sous-menu MIDI Learn. Clic droit sur le potard 7 : son MIDI Learn et le choix TONE / RATE / GLISS.",
 pre_t="8. Presets",
 pre="Dix points de départ : molette sur MODE, clic droit &gt; <b>Presets d'usine</b>, liste de programmes de l'hôte ou Program Change MIDI 0-9. CLEAN PLATE est le son par défaut d'une nouvelle instance.",
 pre_hdr=["#", "Preset", "Scène · mode", "TIME", "DELAY", "LAYER", "VOICE", "Caractère"],
 presets=[["1", "CLEAN PLATE", "INTERGALACTIC · LATCH", "1,3 s", "OFF", "1", "PLATE", "Plate courte et propre, sans shimmer : point de départ neutre."],
          ["2", "GLACIAL PAD", "INTERGALACTIC · LATCH", "10,7 s", "OFF", "2", "PLATE", "Longue nappe cristalline, queue de reverb pure (VOICE plate)."],
          ["3", "INFINITE COSMOS", "INTERGALACTIC · LATCH", "6,5 s", "OFF", "3", "PLATE", "Shimmer ample et lumineux, queue de 6,5 s."],
          ["4", "TAPE ECHO SHIMMER", "INTERGALACTIC · LATCH", "2,8 s", "765 ms", "1", "PLATE", "Écho modulé façon bande (765 ms) qui scintille, reverb à 50 %."],
          ["5", "ETHERDUST GLITCH", "ETHERDUST · LATCH", "2,3 s", "522 ms", "1", "PLATE", "Bégaiements aléatoires et scintillements granulaires."],
          ["6", "FROZEN DRONE", "INTERGALACTIC · LATCH", "4,1 s", "OFF", "4", "PLATE", "Quatre couches figées qui glissent d'une capture à l'autre : un drone sans fin."],
          ["7", "AUTO FREEZE SWELL", "INTERGALACTIC · AUTO", "6,0 s", "OFF", "1", "SHIMMER 25 %", "Capture automatique à chaque attaque, transitions douces."],
          ["8", "DARK CATHEDRAL", "OFF-WORLD · LATCH", "14,0 s", "OFF", "2", "PLATE", "Cathédrale sombre et immense, aigus adoucis."],
          ["9", "TRUE DELAY", "INTERGALACTIC · LATCH", "1,3 s", "428 ms", "1", "PLATE", "Vrai delay propre : reverb coupée (RVB MIX 0), environ 430 ms."],
          ["10", "FROZEN PLATE", "INTERGALACTIC · LATCH", "5,1 s", "OFF", "2", "PLATE", "Plate profonde (environ 5 s) sous un freeze verrouillé."]],
 tips_t="9. Conseils d'utilisation",
 tips=["<b>Chaîne Reaper</b> : piste guitare &gt; accordeur &gt; saturation &gt; simulateur d'ampli &gt; Freeze Shimmer &gt; console. Comme une reverb en boucle d'effets, il sonne mieux après l'ampli ; avant le simulateur, il marche aussi, avec un caractère plus saturé « pedalboard ».",
       "<b>7 cordes accordée grave</b> : fige un accord grave avec SPEED haut et joue des solos par-dessus ; garde TONE sous midi et VOICE sur PLATE pour un grave propre, et utilise OFF-WORLD pour un shimmer plus sombre.",
       "<b>Rien ne se fige ?</b> Vérifie que la LED est allumée et EFFECT monté. En MOMENT, garde le footswitch enfoncé.",
       "<b>Trop de reverb ?</b> Baisse BLEND (page A) ou RVB MIX (page B), ou TIME.",
       "<b>Freeze trop brutal ?</b> Monte SPEED, et GLISS pour fondre les captures successives.",
       "<b>Avec un Chocolate Plus</b> : apprends FOOTSWITCH sur un bouton momentané (maintien = freeze), RELEASE FREEZE sur un autre, et BLEND ou TIME sur une pédale d'expression."],
 ts_h="Dépannage", ts_hdr=["Problème", "Solution"],
 ts=[["Le MIDI ne répond pas", "Vérifie Canal MIDI (OMNI) et que la piste reçoit le MIDI ; aucun CC n'est assigné par défaut : clic droit sur la commande &gt; MIDI Learn. Certains hôtes n'envoient pas le MIDI aux effets : utilise l'assignation de paramètres."],
     ["Une commande réagit à la mauvaise pédale", "Clic droit sur la commande &gt; Clear MIDI, ou MIDI Learn &gt; Clear all MIDI assignments."],
     ["La pédale de sustain ne fige pas", "Aucun CC n'est assigné par défaut : clic droit sur le footswitch &gt; MIDI Learn: FOOTSWITCH, puis appuie sur la pédale de sustain."],
     ["Fenêtre trop grande ou trop petite", "Clic droit sur la pédale &gt; Plugin size, ou tire le coin ; Default size (new windows) règle la taille des nouvelles fenêtres."]],
 tech_t="10. Caractéristiques techniques",
 tech=[["Format", "VST3 64 bits · Windows 11 · macOS 10.13+ universel (Apple Silicon + Intel) ; application autonome sous Windows"],
       ["Shimmer", "FDN 8 lignes (Householder), diffusion d'entrée, amortissement, modulation, octave dans la boucle ; TIME max = réverb figée"],
       ["Freeze", "Freeze spectral à vocodeur de phase, FFT 4096, recouvrement 75 %, jusqu'à 4 couches"],
       ["Latence", "Aucune déclarée (le freeze met 1 à 3 trames de 21 ms à atteindre son plein niveau)"],
       ["Presets", "10 presets d'usine, Program Change 0-9"],
       ["MIDI", "MIDI Learn sur 18 fonctions, aucun CC assigné par défaut, canal OMNI / 1-16 ; affectations sauvegardées avec le projet"],
       ["Fenêtre", "60 % / 75 % / 100 % (Plugin size), taille par défaut des nouvelles fenêtres au choix, redimensionnable par le coin jusqu'à 150 %, jamais sous 60 %"],
       ["Stabilité", "Anti-gel v2 de la fenêtre sous Windows : l'interface ne bloque jamais l'hôte"], ["Version", VERSION]],
 legal="Inspiré des Electro-Harmonix Pico Shimmer et Pico Deep Freeze ; projet indépendant, sans lien avec Electro-Harmonix. Construit avec JUCE (GPL-3.0). Visuel © Studio Wiga."),
}

CUR = {"foot": ""}
def section(lang):
    t = T[lang]; f = []
    def bl(items): return [P("&bull;&nbsp;&nbsp;" + i) for i in items]
    f.append(NextPageTemplate("p"))
    f.append(Spacer(1, 2 * mm)); f.append(P(t["lang"], "coverlang")); f.append(Spacer(1, 2 * mm))
    f.append(img("cover.png", W * 0.46)); f.append(Spacer(1, 6 * mm))
    f.append(P("F R E E Z E &nbsp; S H I M M E R", "cover")); f.append(Spacer(1, 2 * mm))
    f.append(P(t["sub"], "coversub")); f.append(P(t["ver"], "coversub")); f.append(Spacer(1, 8 * mm))
    f.append(img("logo_studio_wiga_blanc.png", 52 * mm)); f.append(PageBreak())
    f.append(P(t["intro_t"], "h1")); f += [P(x) for x in t["intro"]]
    f.append(P(t["feat_h"], "h2")); f += bl(t["feat"])
    f.append(P(t["flow_h"], "h2")); f.append(P(t["flow"]))
    f.append(P(t["inst_t"], "h1"))
    for h, x in t["inst"]: f.append(P(h, "h3")); f.append(P(x))
    f.append(PageBreak())
    f.append(P(t["ov_t"], "h1")); f.append(img("overview_annotated.png", W * 0.50)); f.append(Spacer(1, 4 * mm))
    f.append(table([t["ov_hdr"]] + t["ov"], [10 * mm, 42 * mm, W - 52 * mm])); f.append(Spacer(1, 3 * mm))
    f += [P(x) for x in t["ov_note"]]
    f.append(PageBreak())
    f.append(P(t["ctl_t"], "h1")); f.append(P(t["ctl_intro"]))
    f.append(table([t["kn_hdr"]] + t["kn"], [14 * mm, (W - 14 * mm) * 0.55, (W - 14 * mm) * 0.45])); f.append(Spacer(1, 2 * mm))
    f.append(P(t["kn_note"], "small"))
    f.append(P(t["sc_h"], "h2")); f.append(table(t["sc"], [44 * mm, W - 44 * mm], header=False))
    f.append(KeepTogether([P(t["md_h"], "h2"), table([t["md_hdr"]] + t["md"], [44 * mm, W - 44 * mm])]))
    f.append(PageBreak())
    f.append(P(t["fz_t"], "h1")); f.append(P(t["fz_intro"]))
    f.append(table([t["fz_hdr"]] + t["fz"], [34 * mm, W - 34 * mm])); f.append(Spacer(1, 2 * mm)); f.append(P(t["fz_note"]))
    f.append(P(t["midi_t"], "h1")); f.append(P(t["midi_intro"]))
    f.append(P(t["learn_h"], "h2")); f += bl(t["learn"])
    f.append(KeepTogether([Spacer(1, 2 * mm), img("status_learn.png", W * 0.55), P(t["st_cap"], "cap")]))
    f.append(Spacer(1, 2 * mm)); f.append(table([t["lt_hdr"]] + t["lt"], [62 * mm, W - 62 * mm]))
    f.append(CondPageBreak(70 * mm))
    f.append(P(t["win_t"], "h1")); f += [P(x) for x in t["win"]]
    f.append(KeepTogether([Spacer(1, 2 * mm), table([t["rc_hdr"]] + t["rc"], [62 * mm, W - 62 * mm]), Spacer(1, 2 * mm), P(t["rc_note"], "small")]))
    f.append(CondPageBreak(150 * mm))
    f.append(P(t["pre_t"], "h1")); f.append(P(t["pre"]))
    f.append(table([t["pre_hdr"]] + t["presets"], [8 * mm, 26 * mm, 30 * mm, 13 * mm, 15 * mm, 14 * mm, 19 * mm, W - 125 * mm]))
    f.append(P(t["tips_t"], "h1")); f += bl(t["tips"])
    f.append(KeepTogether([P(t["ts_h"], "h2"), table([t["ts_hdr"]] + t["ts"], [48 * mm, W - 48 * mm])]))
    f.append(KeepTogether([P(t["tech_t"], "h1"), table(t["tech"], [26 * mm, W - 26 * mm], header=False), Spacer(1, 3 * mm), P(t["legal"], "small")]))
    # pas d'historique des versions dans la notice (demande de l'utilisateur)
    f.append(PageBreak())
    return f

def deco(c, doc):
    c.saveState()
    c.setFillColor(ACC); c.rect(0, A4[1] - 4.5 * mm, A4[0], 4.5 * mm, stroke=0, fill=1)
    c.setFont("Pop", 7.5); c.setFillColor(GREY)
    foot = T["fr"]["foot"] if doc.page > HALF[0] else T["en"]["foot"]
    c.drawString(18 * mm, 10 * mm, "Freeze Shimmer (Studio Wiga) · " + foot + " · v" + VERSION)
    c.drawRightString(A4[0] - 18 * mm, 10 * mm, str(doc.page))
    c.restoreState()

def cover_bg(c, doc):
    HALF[0] = doc.page if doc.page > 1 else HALF[0]
    c.saveState(); c.setFillColor(colors.black); c.rect(0, 0, A4[0], A4[1], stroke=0, fill=1)
    c.setFillColor(ACC); c.rect(0, A4[1] - 3 * mm, A4[0], 3 * mm, stroke=0, fill=1); c.restoreState()

HALF = [10 ** 6]   # numero de la couverture francaise (fixe quand elle est dessinee)
doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=18 * mm,
                      title="Freeze Shimmer - User manual / Notice v" + VERSION, author="Studio Wiga")
doc.addPageTemplates([PageTemplate(id="cover", frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="fc")], onPage=cover_bg),
                      PageTemplate(id="p", frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")], onPage=deco)])
en = section("en"); fr = section("fr")
en[-1:] = [NextPageTemplate("cover"), PageBreak()]
doc.build(en + fr[:-1])
print(OUT)
