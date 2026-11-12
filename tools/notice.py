# FREEZE SHIMMER (NINE HANDS | DSP) - notice PDF en francais uniquement, illustree avec le rendu reel du plugin.
# Usage : python3 tools/manual.py <fichier PDF de sortie>
# Images : tools/manual_assets/ (couverture, facade annotee et ligne d'etat reprises de la notice v1.2.0).
# La capture des menus du clic droit de la v1.2.0 (« Window size », « Reset MIDI to defaults (CC ...) ») a ete retiree :
# elle montrait l'ancien menu et le depot n'a pas d'outil de rendu (tools/render) pour la refaire.
# Polices : assets/fonts (Poppins + DejaVuSans pour les fleches). Code compile : Source/ (les copies a la racine ne servent plus).
# Contenu verifie contre Source/PluginEditor.cpp / Source/PluginProcessor.cpp (v1.5.2). Pas d'historique des versions dans le PDF.
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
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "docs", "FreezeShimmer_Notice_FR_v1.5.2.pdf")
VERSION = "1.5.2"
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

def P(t, s="p"): return Paragraph(t.replace("→", '<font name="DV">→</font>').replace("◀", '<font name="DV">◀</font>').replace("▶", '<font name="DV">▶</font>'), st[s])
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
"fr": dict(
 lang="FRANÇAIS", sub="Reverb cosmique et freeze", ver="Notice d'utilisation &nbsp;·&nbsp; version " + VERSION,
 foot="Notice d'utilisation",
 intro_t="1. Présentation",
 intro=["<b>Freeze Shimmer</b> est un effet VST3 NINE HANDS | DSP qui réunit deux idées de pédales en un seul instrument : une <b>reverb shimmer / cosmique</b> inspirée de l'Electro-Harmonix Pico Shimmer (3 scènes, retard, modulation) et un <b>freeze / sound retainer</b> inspiré de la Pico Deep Freeze (sustain infini, couches, glissando).",
        "Joue un accord, maintiens le footswitch et le plugin capture ce qu'il entend. Relâche : le son flotte indéfiniment pendant que tu joues par-dessus. Un double-clic sur le footswitch le laisse partir en douceur. Les moteurs sont écrits de zéro pour reproduire le comportement décrit dans les manuels des pédales, pas une copie bit à bit."],
 feat_h="Points forts",
 feat=["Reverb shimmer : FDN à 8 lignes avec l'octave réinjectée dans la boucle, 3 scènes (INTERGALACTIC, OFF-WORLD, ETHERDUST), écho jusqu'à 950 ms, modulation.",
       "Freeze spectral (vocodeur de phase) : un accord figé garde sa hauteur, jusqu'à 4 couches, fondu GLISS, modes LATCH / MOMENT / AUTO.",
       "Sept potards animés sur deux pages (A étiquettes blanches, B bleues), LED MODE, LED centrale (effet actif / bypass), footswitch à halo lumineux (freeze), pastille presets / ligne d'état.",
       "MIDI Learn sur toutes les commandes (clic droit sur la commande) ; aucun CC n'est assigné par défaut. Menus du clic droit au design d'Octopus, réglage Glow (halo des lumières).",
       "10 presets d'usine ; fenêtre 60 %, 75 % ou 100 % (Plugin size), taille par défaut des nouvelles fenêtres au choix, jamais plus petite que 60 %."],
 flow_h="Chemin du signal",
 flow="Entrée → reverb shimmer (BLEND) → freeze (capture après le shimmer, reverb comprise) → DRY × ton signal + EFFECT × son figé → sortie. En bypass, les queues de reverb s'éteignent naturellement.",
 inst_t="2. Installation",
 inst=[("Windows 11", "Dézippe <b>FreezeShimmer-win64.zip</b> (artefact GitHub Actions ou Release) et lance <b>Install-FreezeShimmer.ps1</b> (clic droit &gt; Exécuter avec PowerShell) : il copie <b>Freeze Shimmer.vst3</b> dans <b>C:\\Program Files\\Common Files\\VST3</b>. Une application autonome <b>Freeze Shimmer.exe</b> est aussi fournie."),
       ("macOS", "Dézippe <b>FreezeShimmer-macos.zip</b> (binaire universel, macOS 10.13 ou plus), puis double-clique sur <b>FreezeShimmer-VST3.pkg</b> (tous les utilisateurs) ou sur <b>install-freezeshimmer-mac.command</b> (copie dans ~/Library/Audio/Plug-Ins/VST3, retire la quarantaine). Si macOS bloque : clic droit &gt; Ouvrir. Sous macOS, Ctrl + clic ouvre aussi le menu du clic droit."),
       ("Reaper", "Options &gt; Preferences &gt; Plug-ins &gt; VST &gt; <b>Re-scan</b>. Le plugin apparaît sous le nom <b>Freeze Shimmer</b>, fabricant <b>NINE HANDS | DSP</b>.")],
 ov_t="3. Vue d'ensemble de l'interface",
 ov_hdr=["#", "Élément", "Rôle"],
 ov=[["1", "DRY", "Niveau du son direct."], ["2", "EFFECT", "Niveau du son figé."],
     ["3", "BLEND / RVB MIX", "Dosage du shimmer / quantité de reverb."], ["4", "TIME / DELAY", "Déclin de la reverb / temps d'écho."],
     ["5", "SPEED / LAYER", "Temps de fondu du freeze / nombre de couches."], ["6", "VOICE / DEPTH", "Plate → shimmer → cordes / profondeur de modulation."],
     ["7", "TONE / RATE / GLISS", "Brillance / vitesse de modulation / fondu entre deux freezes."],
     ["8", "LED MODE (bouton)", "Scène, mode de freeze, page, presets ; <b>blanche</b> = page A, <b>bleue</b> = page B."], ["9", "LED centrale (bypass)", "Allumée : effet actif ; éteinte : bypass."],
     ["10", "Footswitch", "Freeze (maintien), relâche (double-clic) ; halo bleu lumineux qui pulse pendant le freeze."],
     ["11", "Pastille presets / état", "Au repos : preset (◀ ▶, clic sur le nom pour la liste). Dès qu'un réglage bouge : valeur lisible, valeur MIDI, messages du MIDI Learn."]],
 ov_note=["Double-clic sur un potard : valeur par défaut. Glisse verticalement ou utilise la molette. Clic droit sur un potard, MODE ou le footswitch : son MIDI Learn.",
          "La LED MODE est toujours allumée : <b>blanche</b> en page A (étiquettes blanches), <b>bleue</b> en page B (étiquettes bleues, potards à liseré bleu). La LED centrale indique l'état de l'effet : allumée quand il est actif, éteinte en bypass. Le freeze est indiqué par le halo bleu qui pulse autour du footswitch. Leur halo se règle par clic droit &gt; <b>Glow (halo of the lights)</b> : 25, 50, 75 ou 100 % (le cœur des lumières reste toujours à pleine intensité)."],
 ctl_t="4. Commandes",
 ctl_intro="Chaque potard a deux fonctions. La page A (étiquettes blanches) est celle par défaut ; la page B (étiquettes bleues) s'obtient en maintenant MODE environ une seconde.",
 kn_hdr=["Potard", "Page A", "Page B"],
 kn=[["1", "<b>DRY</b> : niveau du signal direct, non traité.", "—"], ["2", "<b>EFFECT</b> : niveau du son figé dans le mélange.", "—"],
     ["3", "<b>BLEND</b> : dosage direct / effet de l'étage shimmer (puissance constante).", "<b>RVB MIX</b> : quantité de reverb, 0 = retard seul."],
     ["4", "<b>TIME</b> : déclin d'environ 0,4 s à 18 s ; au maximum ∞, la réverb ne s'éteint plus.", "<b>DELAY</b> : temps d'écho 0-950 ms, 0 = coupé."],
     ["5", "<b>SPEED</b> : fondu d'entrée / de sortie du freeze, 20 ms – 3 s.", "<b>LAYER</b> : nombre de couches figées empilées, 1 – 4 (LATCH)."],
     ["6", "<b>VOICE</b> : plate (0-25 %) → shimmer → cordes (75-100 %).", "<b>DEPTH</b> : profondeur de modulation de la reverb."],
     ["7", "<b>TONE</b> : brillance du signal traité.", "<b>RATE</b> : vitesse de modulation, 0,15 – 5 Hz."]],
 kn_note="<b>GLISS</b> (fondu entre deux freezes, 20 ms – 5 s) peut remplacer TONE / RATE sur le potard 7 : clic droit sur le potard &gt; <b>GLISS (freeze)</b> ; <b>TONE / RATE (follows the page)</b> le rétablit. Astuce SPEED : bas = capture instantanée et percussive ; haut = éclosion lente et longue relâche.",
 sc_h="Scènes shimmer",
 sc=[["INTERGALACTIC (vert)", "Shimmer classique : une voix à l'octave supérieure tourne dans la boucle de reverb. VOICE passe de plate à shimmer puis cordes."],
     ["OFF-WORLD (orange)", "Shimmer plus doux et plus sombre, modulation renforcée ; dans la moitié haute, VOICE ajoute des textures de synthé vintage (octaves désaccordées)."],
     ["ETHERDUST (rouge)", "Shimmer glitch à temps de retard aléatoires, des scintillements granulaires aux échos distincts. RVB MIX bas = plus de bégaiements."]],
 md_h="Bouton MODE", md_hdr=["Geste", "Effet"],
 md=[["Clic", "Scène suivante"], ["Maj + clic", "Mode de freeze suivant (LATCH · MOMENT · AUTO)"], ["Maintien environ 1 s", "Bascule page A / B"],
     ["Molette (sur la LED)", "Preset d'usine précédent / suivant"], ["Clic droit", "MIDI Learn de SCENE et FREEZE MODE, puis le menu complet"]],
 fz_t="5. Freeze et footswitch",
 fz_intro="Le moteur de freeze est un freeze spectral à vocodeur de phase (FFT 4096) : il garde la magnitude et l'avance de phase de chaque bande, donc un accord figé garde sa hauteur.",
 fz_hdr=["Mode", "Comportement"],
 fz=[["LATCH (par défaut)", "Maintiens le footswitch : le plugin capture ce qu'il entend. Relâche : le son est tenu à l'infini, joue par-dessus. Double-clic : le freeze s'éteint en fondu (durée SPEED). Chaque nouvelle capture ajoute une couche (jusqu'à LAYER) ou glisse vers le nouveau son (GLISS)."],
     ["MOMENT", "Le son n'est figé que tant que le footswitch est maintenu."],
     ["AUTO", "Capture automatique à chaque attaque détectée ; GLISS règle le passage d'une note à la suivante. Un clic sur le footswitch arme / désarme l'auto-capture."]],
 fz_note="Change de mode par Maj + clic sur MODE, le menu du clic droit (<b>Mode freeze</b>) ou le MIDI. Bypass : clic droit &gt; <b>Effect on (bypass when unticked)</b> ou MIDI (ENGAGE). Arrêter un freeze : double-clic, clic droit &gt; <b>Stop the freeze</b> ou MIDI (RELEASE FREEZE).",
 midi_t="6. MIDI",
 midi_intro="Freeze Shimmer écoute le canal choisi dans clic droit &gt; <b>MIDI channel</b> (OMNI par défaut, ou 1-16). Dans Reaper, arme la piste avec ton entrée MIDI et active le monitoring. <b>Aucun CC n'est assigné par défaut</b> : chaque commande s'assigne par MIDI Learn. Tous les paramètres sont aussi automatisables depuis le DAW.",
 learn_h="MIDI Learn",
 learn=["<b>Clic droit sur une commande</b> : un potard (le paramètre de la page affichée, ou GLISS sur le potard 7), le bouton MODE (SCENE et FREEZE MODE) ou le footswitch (FOOTSWITCH et RELEASE FREEZE). Le menu commence par <b>MIDI Learn: &lt;commande&gt; (no CC)</b> (ou le CC appris, par ex. <b>(CC 24)</b>). Choisis-le puis bouge une pédale d'expression ou appuie sur un bouton MIDI : le premier CC reçu est affecté. Ce message d'apprentissage ne modifie pas le son.",
        "La ligne d'état affiche <b>MIDI LEARN: move a control for &lt;commande&gt;</b>, puis <b>&lt;commande&gt; = CC n</b> pendant 2 secondes.",
        "<b>Clear MIDI: &lt;commande&gt;</b> retire l'affectation ; <b>Cancel MIDI learn</b> (ou un nouveau choix du même MIDI Learn) annule l'attente.",
        "Un numéro de CC ne pilote qu'une commande : apprendre un CC déjà utilisé le retire de l'autre commande.",
        "Clic droit &gt; sous-menu <b>MIDI Learn</b> : <b>Learn: &lt;commande&gt; (no CC)</b> ou avec son CC appris pour les 18 fonctions, <b>Cancel MIDI learn</b> (pendant l'attente) et <b>Clear all MIDI assignments</b>, qui efface toutes les affectations. <b>MIDI map...</b> affiche les affectations en cours.",
        "Les affectations sont <b>sauvegardées avec le projet</b>. Un projet fait avec une version précédente qui utilisait encore les anciens numéros d'usine (CC 20-32, 102-106) s'ouvre sans aucune affectation : réapprends les commandes voulues. Un projet où tu avais changé une affectation garde ses affectations telles qu'enregistrées. La pédale de sustain n'est plus un footswitch d'office : apprends-la sur FOOTSWITCH pour figer le son avec elle."],
 lt_hdr=["Commande", "Type"],
 lt=[["DRY, EFFECT, BLEND, RVB MIX, TIME, DELAY, SPEED", "Continu 0-127"], ["LAYER, VOICE, DEPTH, TONE, RATE, GLISS", "Continu 0-127"],
     ["SCENE", "Sélecteur 3 positions : 0-42 INTERGALACTIC, 43-85 OFF-WORLD, 86-127 ETHERDUST"],
     ["FREEZE MODE", "Sélecteur 3 positions : LATCH, MOMENT, AUTO"],
     ["FOOTSWITCH", "Footswitch momentané : 64 et plus = enfoncé, moins de 64 = relâché (maintien / relâche comme le vrai footswitch)"],
     ["ENGAGE", "Bascule à accrochage : 64 et plus = effet actif, moins de 64 = bypass"], ["RELEASE FREEZE", "Déclencheur : 64 et plus arrête le freeze"],
     ["Presets d'usine", "Program Change 0-9 = presets 1 à 10 (toujours actif, rien à apprendre)"]],
 st_cap="Ligne d'état pendant le MIDI Learn : attente, puis confirmation.",
 win_t="7. Fenêtre et pastille presets / état",
 win=["La fenêtre s'ouvre à la taille par défaut et ne peut jamais être plus petite que 60 %. Clic droit sur la pédale &gt; <b>Plugin size</b> : <b>60 %</b>, <b>75 %</b> ou <b>100 %</b> redimensionne cette fenêtre, et <b>(default)</b> est indiqué à côté de la taille par défaut choisie ; tu peux aussi tirer le coin jusqu'à 150 %. En bas du même menu, <b>Default size (new windows)</b> choisit la taille d'ouverture de toutes les nouvelles fenêtres de Freeze Shimmer (réglage commun à toutes les instances, enregistré sur l'ordinateur, dans NINE HANDS | DSP/Freeze Shimmer/settings.xml du dossier de données de l'utilisateur) ; la fenêtre ouverte prend aussitôt cette taille.",
      "La taille de chaque fenêtre (choisie dans le menu ou au coin) est enregistrée avec le projet et reste prioritaire pour cette instance à la réouverture du projet ; une nouvelle instance s'ouvre à la taille par défaut.",
      "La pastille noire sous les potards est à la fois la barre de presets et la ligne d'état. Au repos elle montre le preset (clic sur ◀ ▶ pour changer, clic sur le nom pour la liste). Dès qu'un réglage bouge (souris, molette, MIDI, automation), elle affiche le dernier paramètre touché avec sa valeur lisible (%, s, ms, Hz) et, si une commande est assignée, son CC avec la valeur MIDI (ex. <b>CC 12 = 70</b>) ; elle passe en vert quand la valeur vient du MIDI. Environ 2,5 s après le dernier mouvement, la barre de presets revient en fondu. Un clic sur la pastille pendant l'affichage fait revenir la barre. Les messages du MIDI Learn et du Glow s'y affichent aussi.",
      "Tous les menus du clic droit ont le design d'Octopus et s'ouvrent là où l'on clique."],
 rc_hdr=["Menu du clic droit (MODE / footswitch)", "Rôle"],
 rc=[["MIDI Learn / Clear MIDI", "En tête, pour la commande cliquée."], ["Presets", "Les 10 presets d'usine."],
     ["Plugin size", "60 %, 75 %, 100 % (« (default) » à côté de la taille par défaut), puis Default size (new windows)."],
     ["Scene (shimmer) / Mode freeze", "Choix de la scène / du mode de freeze."], ["Knobs: page A / page B", "Page des potards."],
     ["Effect on (bypass when unticked)", "Effet actif / bypass."], ["Stop the freeze", "Arrête le freeze."], ["Glow (halo of the lights)", "Halo des lumières : 25, 50, 75 ou 100 %."], ["MIDI channel", "OMNI ou 1-16."],
     ["MIDI Learn", "Learn pour chaque fonction, Cancel MIDI learn, Clear all MIDI assignments."], ["MIDI map...", "Affectations CC en cours."]],
 rc_note="Clic droit sur un potard (1 à 6) ou sur une zone vide de la pédale : son MIDI Learn (sur un potard), Plugin size et le sous-menu MIDI Learn. Clic droit sur le potard 7 : son MIDI Learn et le choix TONE / RATE / GLISS.",
 pre_t="8. Presets",
 pre="Dix points de départ : flèches ◀ ▶ de la pastille, clic sur son nom, molette sur la LED MODE, clic droit &gt; <b>Presets</b>, liste de programmes de l'hôte ou Program Change MIDI 0-9. Clean Plate est le son par défaut d'une nouvelle instance.",
 pre_hdr=["#", "Preset", "Scène · mode", "TIME", "DELAY", "LAYER", "VOICE", "Caractère"],
 presets=[["1", "Clean Plate", "INTERGALACTIC · LATCH", "1,3 s", "OFF", "1", "PLATE", "Plate courte et propre, sans shimmer : point de départ neutre."],
          ["2", "Glacial Pad", "INTERGALACTIC · LATCH", "10,7 s", "OFF", "2", "PLATE", "Longue nappe cristalline, queue de reverb pure (VOICE plate)."],
          ["3", "Infinite Cosmos", "INTERGALACTIC · LATCH", "6,5 s", "OFF", "3", "PLATE", "Shimmer ample et lumineux, queue de 6,5 s."],
          ["4", "Tape Echo Shimmer", "INTERGALACTIC · LATCH", "2,8 s", "765 ms", "1", "PLATE", "Écho modulé façon bande (765 ms) qui scintille, reverb à 50 %."],
          ["5", "Etherdust Glitch", "ETHERDUST · LATCH", "2,3 s", "522 ms", "1", "PLATE", "Bégaiements aléatoires et scintillements granulaires."],
          ["6", "Frozen Drone", "INTERGALACTIC · LATCH", "4,1 s", "OFF", "4", "PLATE", "Quatre couches figées qui glissent d'une capture à l'autre : un drone sans fin."],
          ["7", "Auto Freeze Swell", "INTERGALACTIC · AUTO", "6,0 s", "OFF", "1", "SHIMMER 25 %", "Capture automatique à chaque attaque, transitions douces."],
          ["8", "Dark Cathedral", "OFF-WORLD · LATCH", "14,0 s", "OFF", "2", "PLATE", "Cathédrale sombre et immense, aigus adoucis."],
          ["9", "True Delay", "INTERGALACTIC · LATCH", "1,3 s", "428 ms", "1", "PLATE", "Vrai delay propre : reverb coupée (RVB MIX 0), environ 430 ms."],
          ["10", "Frozen Plate", "INTERGALACTIC · LATCH", "5,1 s", "OFF", "2", "PLATE", "Plate profonde (environ 5 s) sous un freeze verrouillé."]],
 tips_t="9. Conseils d'utilisation",
 tips=["<b>Chaîne Reaper</b> : piste guitare &gt; accordeur &gt; saturation &gt; simulateur d'ampli &gt; Freeze Shimmer &gt; console. Comme une reverb en boucle d'effets, il sonne mieux après l'ampli ; avant le simulateur, il marche aussi, avec un caractère plus saturé « pedalboard ».",
       "<b>7 cordes accordée grave</b> : fige un accord grave avec SPEED haut et joue des solos par-dessus ; garde TONE sous midi et VOICE sur PLATE pour un grave propre, et utilise OFF-WORLD pour un shimmer plus sombre.",
       "<b>Rien ne se fige ?</b> Vérifie que l'effet est actif (clic droit &gt; <b>Effect on</b>) et EFFECT monté. En MOMENT, garde le footswitch enfoncé.",
       "<b>Trop de reverb ?</b> Baisse BLEND (page A) ou RVB MIX (page B), ou TIME.",
       "<b>Freeze trop brutal ?</b> Monte SPEED, et GLISS pour fondre les captures successives.",
       "<b>Avec un Chocolate Plus</b> : apprends FOOTSWITCH sur un bouton momentané (maintien = freeze), RELEASE FREEZE sur un autre, et BLEND ou TIME sur une pédale d'expression."],
 ts_h="Dépannage", ts_hdr=["Problème", "Solution"],
 ts=[["Le MIDI ne répond pas", "Vérifie MIDI channel (OMNI) et que la piste reçoit le MIDI ; aucun CC n'est assigné par défaut : clic droit sur la commande &gt; MIDI Learn. Certains hôtes n'envoient pas le MIDI aux effets : utilise l'assignation de paramètres."],
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
       ["Interface", "Pédale plein cadre, potards à calques animés (flou de mouvement), textes et logo vectoriels, menus au design d'Octopus, Glow 25 / 50 / 75 / 100 %"],
       ["Stabilité", "Anti-gel v2 de la fenêtre sous Windows : l'interface ne bloque jamais l'hôte"], ["Version", VERSION]],
 legal="Inspiré des Electro-Harmonix Pico Shimmer et Pico Deep Freeze ; projet indépendant, sans lien avec Electro-Harmonix. Construit avec JUCE (GPL-3.0). Visuel © NINE HANDS | DSP.")
}

def bl(items): return [P("&bull;&nbsp;&nbsp;" + i) for i in items]
def section():
    t = T["fr"]; f = []
    f.append(NextPageTemplate("p")); f.append(PageBreak())          # la couverture est dessinee par cover_bg
    f.append(P(t["intro_t"], "h1")); f += [P(x) for x in t["intro"]]
    f.append(P(t["feat_h"], "h2")); f += bl(t["feat"])
    f.append(P(t["flow_h"], "h2")); f.append(P(t["flow"]))
    f.append(P(t["inst_t"], "h1"))
    for h, x in t["inst"]: f.append(P(h, "h3")); f.append(P(x))
    f.append(PageBreak())
    f.append(P(t["ov_t"], "h1")); f.append(img("overview_annotated.png", W * 0.50)); f.append(Spacer(1, 4 * mm))
    f.append(table([t["ov_hdr"]] + t["ov"], [10 * mm, 44 * mm, W - 54 * mm])); f.append(Spacer(1, 3 * mm))
    f += [P(x) for x in t["ov_note"]]
    f.append(PageBreak())
    f.append(P(t["ctl_t"], "h1")); f.append(P(t["ctl_intro"]))
    f.append(table([t["kn_hdr"]] + t["kn"], [18 * mm, (W - 18 * mm) * 0.55, (W - 18 * mm) * 0.45])); f.append(Spacer(1, 2 * mm))
    f.append(P(t["kn_note"], "small"))
    f.append(P(t["sc_h"], "h2")); f.append(table(t["sc"], [44 * mm, W - 44 * mm], header=False))
    f.append(KeepTogether([P(t["md_h"], "h2"), table([t["md_hdr"]] + t["md"], [44 * mm, W - 44 * mm])]))
    f.append(PageBreak())
    f.append(P(t["fz_t"], "h1")); f.append(P(t["fz_intro"]))
    f.append(table([t["fz_hdr"]] + t["fz"], [34 * mm, W - 34 * mm])); f.append(Spacer(1, 2 * mm)); f.append(P(t["fz_note"]))
    f.append(P(t["midi_t"], "h1")); f.append(P(t["midi_intro"]))
    f.append(P(t["learn_h"], "h2")); f += bl(t["learn"])
    f.append(Spacer(1, 2 * mm)); f.append(table([t["lt_hdr"]] + t["lt"], [62 * mm, W - 62 * mm]))
    f.append(CondPageBreak(70 * mm))
    f.append(P(t["win_t"], "h1")); f += [P(x) for x in t["win"]]
    f.append(KeepTogether([Spacer(1, 2 * mm), table([t["rc_hdr"]] + t["rc"], [62 * mm, W - 62 * mm]), Spacer(1, 2 * mm), P(t["rc_note"], "small")]))
    f.append(CondPageBreak(150 * mm))
    f.append(P(t["pre_t"], "h1")); f.append(P(t["pre"]))
    f.append(table([t["pre_hdr"]] + t["presets"], [8 * mm, 28 * mm, 30 * mm, 13 * mm, 15 * mm, 14 * mm, 19 * mm, W - 127 * mm]))
    f.append(P(t["tips_t"], "h1")); f += bl(t["tips"])
    f.append(KeepTogether([P(t["ts_h"], "h2"), table([t["ts_hdr"]] + t["ts"], [48 * mm, W - 48 * mm])]))
    f.append(KeepTogether([P(t["tech_t"], "h1"), table(t["tech"], [26 * mm, W - 26 * mm], header=False), Spacer(1, 3 * mm), P(t["legal"], "small")]))
    return f   # pas d'historique des versions (regle de l'utilisateur)

def deco(c, doc):
    c.saveState()
    c.setFillColor(ACC); c.rect(0, A4[1] - 4.5 * mm, A4[0], 4.5 * mm, stroke=0, fill=1)
    c.setFont("Pop", 7.5); c.setFillColor(GREY)
    c.drawString(18 * mm, 10 * mm, "Freeze Shimmer (NINE HANDS | DSP) · Notice d'utilisation · v" + VERSION)
    c.drawRightString(A4[0] - 18 * mm, 10 * mm, str(doc.page))
    c.restoreState()

# ---- couverture « minimale » (gabarit fixe de toutes les notices NINE HANDS | DSP) ; mesures en mm depuis le haut
PEDAL_H, PEDAL_TOP, NAME_TOP, SUB_TOP = 82, 84, 194, 208
pdfmetrics.registerFont(TTFont("Barlow", os.path.join(FONTS, "BarlowCondensed-ExtraBold.ttf")))
def cover_bg(c, doc):
    Wp, Hp = A4
    c.saveState(); c.setFillColor(colors.black); c.rect(0, 0, Wp, Hp, stroke=0, fill=1)
    c.setFillColor(ACC); c.rect(0, 0, Wp, 3 * mm, stroke=0, fill=1)                       # bandeau d'accent en bas
    c.setFont("PopM", 8.5); c.setFillColor(ACC_L)
    c.drawCentredString(Wp / 2, Hp - 18 * mm - 8.5 * 0.72, "FRANÇAIS")
    # pedale detouree (boitier + jacks = 82 mm de haut) avec reflet et halo
    im = Image.open(os.path.join(A, "cover_pedale.png")); k = (PEDAL_H * mm) / 1800.0     # points par pixel (rendu 1316 x 1800)
    pad = 300; w, h = im.width * k, im.height * k
    x = (Wp - 1316 * k) / 2 - pad * k; ytop = Hp - PEDAL_TOP * mm + pad * k
    c.drawImage(os.path.join(A, "cover_pedale.png"), x, ytop - h, width=w, height=h, mask="auto")
    c.setFont("Barlow", 30); c.setFillColor(colors.white)
    c.drawCentredString(Wp / 2, Hp - NAME_TOP * mm - 30 * 0.72, "FREEZE SHIMMER", charSpace=15 * 0.5) if False else None
    t = c.beginText(); t.setFont("Barlow", 30); t.setCharSpace(7.5); name = "FREEZE SHIMMER"
    wname = pdfmetrics.stringWidth(name, "Barlow", 30) + 7.5 * (len(name) - 1)
    t.setTextOrigin((Wp - wname) / 2, Hp - NAME_TOP * mm - 30 * 0.72); t.textOut(name); c.drawText(t)
    t = c.beginText(); t.setFont("Pop", 10); t.setFillColor(colors.HexColor("#BDC4B8")); t.setCharSpace(1.5)
    sub = "Reverb cosmique et freeze"; ws = pdfmetrics.stringWidth(sub, "Pop", 10) + 1.5 * (len(sub) - 1)
    t.setTextOrigin((Wp - ws) / 2, Hp - SUB_TOP * mm - 10 * 0.72); t.textOut(sub); c.drawText(t)
    # logo NINE HANDS | DSP blanc (SVG officiel v003, rendu 4x), 38 mm de large, bas a 22 mm du bas
    lg = Image.open(os.path.join(A, "logo_blanc.png")); lw = 38 * mm; lh = lw * lg.height / lg.width
    c.drawImage(os.path.join(A, "logo_blanc.png"), (Wp - lw) / 2, 22 * mm, width=lw, height=lh, mask="auto")
    c.restoreState()

def render_logo():
    import re
    from playwright.sync_api import sync_playwright
    svg = open(os.path.join(A, "NineHandsLogoWhite.svg")).read(); vb = re.search(r'viewBox="([^"]+)"', svg).group(1).split()
    wpx = 1800; hpx = int(wpx * float(vb[3]) / float(vb[2])) + 4
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": wpx, "height": hpx})
        pg.set_content('<html><body style="margin:0;background:transparent">' + svg.replace("<svg ", f'<svg width="{wpx}" ', 1) + "</body></html>")
        pg.screenshot(path=os.path.join(A, "logo_blanc_raw.png"), omit_background=True); b.close()
    im = Image.open(os.path.join(A, "logo_blanc_raw.png")).convert("RGBA"); im = im.crop(im.getbbox()); im.save(os.path.join(A, "logo_blanc.png"))
render_logo()

doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=18 * mm,
                      title="Freeze Shimmer - Notice d'utilisation v" + VERSION, author="NINE HANDS | DSP")
doc.addPageTemplates([PageTemplate(id="cover", frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="fc")], onPage=cover_bg),
                      PageTemplate(id="p", frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")], onPage=deco)])
doc.build(section())
print(OUT)
