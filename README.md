# Freeze Shimmer — VST3 (Windows 11 & macOS)

Plugin d'effet **VST3** « Frozen Cosmic Reverb » par **NINE HANDS | DSP**, qui réunit dans une seule interface :

- un **shimmer / cosmic reverb** inspiré de la *Pico Shimmer* (3 scènes, retard, modulation) ;
- un **freeze / sound retainer** inspiré de la *Pico Deep Freeze* (sustain infini, couches, glissando).

L'interface (v1.4.1) est une pédale givrée **plein cadre** : potards à calques animés (flou de mouvement, lumière en haut à gauche), textes et logo en vectoriel, LED MODE (page B) et LED centrale (effet actif / bypass), halo lumineux autour du footswitch quand le freeze est actif, pastille unique « presets / ligne d'état », menus clic droit au design d'Octopus avec réglage **Glow** (25 / 50 / 75 / 100 %). Fenêtre par défaut « 60 % », non réductible en dessous.

> **Précision importante.** Les algorithmes des pédales Electro-Harmonix sont propriétaires, et le schéma fourni
> décrit le câblage matériel (3 potentiomètres, interrupteurs SPDT, footswitch, LED, entrée/sortie), pas l'algorithme audio.
> Les moteurs de ce plugin sont donc **écrits from scratch** pour reproduire le *comportement* décrit dans les manuels
> (fonctions des boutons, modes, interactions), pas une copie bit-à-bit du son. Projet indépendant, non affilié à
> Electro-Harmonix (noms de pédales cités à titre de référence).

---

<p align="center">
  <a href="https://github.com/Nine-Hands-Dsp/Freeze-Shimmer/releases/latest/download/FreezeShimmer-VST3-Windows.zip"><img alt="Télécharger pour Windows" src="https://img.shields.io/badge/%E2%AC%87%20T%C3%A9l%C3%A9charger-Windows-0078D6?style=for-the-badge"></a>
  <a href="https://github.com/Nine-Hands-Dsp/Freeze-Shimmer/releases/latest/download/FreezeShimmer-VST3-macOS.zip"><img alt="Télécharger pour macOS" src="https://img.shields.io/badge/%E2%AC%87%20T%C3%A9l%C3%A9charger-macOS-111111?style=for-the-badge&logo=apple&logoColor=white"></a>
  <br>
  <a href="https://github.com/Nine-Hands-Dsp/Freeze-Shimmer/releases/latest/download/FreezeShimmer-Notice.pdf"><img alt="Télécharger la notice (PDF)" src="https://img.shields.io/badge/%F0%9F%93%96%20Notice-PDF-919496?style=for-the-badge"></a>
  <br>
  <a href="https://github.com/Nine-Hands-Dsp/Freeze-Shimmer/releases/latest"><img alt="Dernière version" src="https://img.shields.io/github/v/release/Nine-Hands-Dsp/Freeze-Shimmer?label=derni%C3%A8re%20version&color=919496"></a>
</p>

## Installation (utilisateur)

1. Récupérez `FreezeShimmer-win64.zip` dans **Actions → dernier build → Artifacts** (ou dans **Releases** si vous avez poussé un tag `vX.Y.Z`).
2. Dézippez, puis clic droit sur `Install-FreezeShimmer.ps1` → *Exécuter avec PowerShell* (droits admin demandés).
   Le script copie `Freeze Shimmer.vst3` dans `C:\Program Files\Common Files\VST3`.
3. Relancez le scan des plugins de votre DAW.

Un exécutable autonome (`Freeze Shimmer.exe`) est aussi fourni pour essayer le plugin sans DAW.

### macOS (Apple Silicon et Intel)

1. Récupérez `FreezeShimmer-macos.zip` dans **Actions → dernier build → Artifacts** (ou **Releases**). Le binaire est **universel** (arm64 + x86_64), macOS 10.13 minimum.
2. Dézippez, puis au choix : double-cliquez sur `FreezeShimmer-VST3.pkg` (installation pour tous les utilisateurs dans `/Library/Audio/Plug-Ins/VST3`), ou sur `install-freezeshimmer-mac.command` : il copie `Freeze Shimmer.vst3` dans `~/Library/Audio/Plug-Ins/VST3`, retire la quarantaine et applique une signature locale.
   (Installation manuelle : copiez le dossier `Freeze Shimmer.vst3` dans `~/Library/Audio/Plug-Ins/VST3` ou `/Library/Audio/Plug-Ins/VST3`.)
3. Relancez le scan des plugins de votre DAW.

> Le plugin n'est pas notarisé Apple : si macOS bloque l'ouverture (« développeur non identifié »), clic droit sur le `.pkg` ou le `.command` → *Ouvrir*,
> ou exécutez `xattr -dr com.apple.quarantine "Freeze Shimmer.vst3"` dans le Terminal.
> Sous macOS, le clic droit sur la pédale s'obtient aussi par `Ctrl` + clic.

## Compiler soi-même

Prérequis : Windows 11, Visual Studio 2022 (charge de travail *Développement Desktop C++*), CMake ≥ 3.22, Git.
Sous macOS : Xcode (ou les Command Line Tools), CMake ≥ 3.22, Git.

```powershell
git clone <votre-repo> FreezeShimmer
cd FreezeShimmer
cmake -S . -B build -G "Visual Studio 17 2022" -A x64
cmake --build build --config Release --parallel
# -> build\FreezeShimmer_artefacts\Release\VST3\Freeze Shimmer.vst3
```

JUCE 8.0.12 est téléchargé automatiquement par CMake. Option `-DFS_COPY_AFTER_BUILD=ON` pour copier le VST3 après compilation
(terminal administrateur requis).

```bash
# macOS (binaire universel)
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release --parallel
# -> build/FreezeShimmer_artefacts/Release/VST3/Freeze Shimmer.vst3
```

**Via GitHub** : poussez le dépôt ; le workflow `.github/workflows/build.yml` compile le VST3 sur `windows-2022` et sur `macos-14`, lance les tests DSP
sous Linux et publie les zips (`FreezeShimmer-win64.zip`, `FreezeShimmer-macos.zip`). Un tag `v1.1.0` crée une *Release* avec le zip.

---

## Commandes

| Bouton | Page A (étiquette blanche) | Page B (étiquette bleue) |
|---|---|---|
| haut gauche | **DRY** — niveau du signal direct | idem |
| haut droite | **EFFECT** — niveau du son figé | idem |
| gauche 1 | **BLEND** — dry/wet du shimmer | **RVB MIX** — mix réverb (0 = retard seul) |
| centre | **TIME** — decay, **infini** au maximum | **DELAY** — retard 0–950 ms (0 = off) |
| droite 1 | **SPEED** — attaque/relâchement du freeze | **LAYER** — nombre de couches (1–4, Latch) |
| gauche 2 | **VOICE** — plate → shimmer → strings | **DEPTH** — profondeur de modulation |
| droite 2 | **TONE** — luminosité du wet | **RATE** — vitesse de modulation |
| droite 2 (menu) | **GLISS** — fondu entre deux freezes (clic droit sur le bouton → *GLISS*) | |

- **Bouton MODE** (haut) : clic = scène suivante (**INTERGALACTIC** vert · **OFF-WORLD** orange · **ETHERDUST** rouge) ;
  `Maj`+clic = mode freeze suivant (**LATCH · MOMENT · AUTO**) ; maintien ~1 s = bascule page A/B ;
  **molette** = preset suivant / précédent ; clic droit = menu complet (presets, taille (*Plugin size*), scène, mode, page, bypass, canal MIDI, table MIDI).
- **LED centrale** : éteinte en bypass · allumée effet actif ; le **halo du footswitch** indique le freeze.
- **Footswitch** (bas) : **appui maintenu** = freeze · **double-clic** = arrête le freeze (voir ci-dessous). Bypass : clic droit → menu, ou MIDI (après MIDI Learn).
- **Double-clic** sur un bouton = valeur par défaut. Glisser verticalement, ou molette.

### Scènes (shimmer)

- **INTERGALACTIC** : shimmer classique (octave +12 dans la boucle de réverb), VOICE morphe *plate → shimmer → strings*.
- **OFF-WORLD** : shimmer plus doux/sombre avec modulation renforcée ; VOICE en moitié haute = textures de synthé vintage (octaves désaccordées).
- **ETHERDUST** : shimmer « glitch » à temps de retard aléatoires (de scintillements granulaires à des échos distincts) ; RVB MIX bas = plus de stutter.

### Freeze (footswitch)

Mode **LATCH** (par défaut) :
1. **Maintenez** le footswitch : le plugin fige en continu ce qu'il entend (accord, note, nappe…).
2. **Relâchez** : le son figé est maintenu à l'infini, vous jouez par-dessus (le signal direct passe normalement, niveau DRY).
3. **Double-clic** sur le footswitch : le freeze s'arrête (fondu réglé par SPEED).
Un nouvel appui ajoute une couche (jusqu'à LAYER = 4) ou glisse vers le nouveau son (GLISS).

Autres modes (`Maj`+clic sur MODE) :
- **MOMENT** : le son est figé seulement tant que l'on maintient le footswitch.
- **AUTO** : capture automatique à chaque nouvelle attaque détectée ; GLISS règle le morphing d'une note à la suivante. Un clic sur le footswitch arme / désarme l'auto-capture.

SPEED = attaque / relâchement du freeze · LAYER = nombre de couches · GLISS = durée du fondu entre deux freezes.

Chaîne audio : `entrée → Shimmer (BLEND) → Freeze (capture post-shimmer) → DRY × signal + EFFECT × son figé → sortie`.
En bypass, les queues de réverb s'éteignent naturellement.

### Ligne d'état

Sous l'encadré : dernier paramètre touché et sa valeur lisible (%, s, ms, Hz…), état *scène · mode · page · FROZEN*,
et à droite la valeur **MIDI** correspondante (`CC24 = 70` si un CC est appris). Elle passe en vert quand la valeur vient d'un message MIDI entrant. La valeur affichée à gauche prend la couleur de l'étiquette du potard : blanc (page A), bleu (page B : RVB MIX, DELAY, LAYER, DEPTH, RATE).

---

## MIDI

Tous les paramètres sont aussi **automatisables** depuis le DAW (utile car certains hôtes n'envoient pas le MIDI aux effets —
voir *MIDI learn* / mapping de paramètres de votre DAW). Canal réglable (menu clic droit, **OMNI** par défaut).

Aucun CC assigné par défaut : clic droit > MIDI > Learn.

**MIDI Learn** (v1.2) : clic droit sur un potard (paramètre de la page affichée), le bouton MODE (scène, mode freeze) ou le footswitch (freeze, relâche) -> « MIDI Learn », puis bouger la pédale d'expression / appuyer sur le bouton MIDI ; « Clear MIDI » retire l'assignation. Le sous-menu *MIDI Learn* liste toutes les commandes (potards, scène 0-42 / 43-85 / 86-127, mode freeze LATCH / MOMENT / AUTO, footswitch ≥ 64 enfoncé, effet actif ≥ 64 / bypass, relâche du freeze) et « Clear all MIDI assignments » efface toutes les assignations. Les assignations sont sauvegardées avec le projet.

*Program Change* 0 à 9 = preset d'usine.

---

## Presets d'usine (10)

Molette sur le bouton MODE, ou clic droit → *Presets d'usine*, ou *Program Change* MIDI 0–9 / liste de programmes de l'hôte.
**CLEAN PLATE** est le premier preset et le son par défaut d'une nouvelle instance.

| # | Nom | Caractère |
|---|---|---|
| 1 | CLEAN PLATE | plate courte et propre, sans shimmer |
| 2 | GLACIAL PAD | shimmer long, nappe cristalline (VOICE 0 %) |
| 3 | INFINITE COSMOS | shimmer ample, TIME 6,5 s |
| 4 | TAPE ECHO SHIMMER | écho modulé 765 ms + shimmer, RVB MIX 50 % |
| 5 | ETHERDUST GLITCH | stutters aléatoires scintillants |
| 6 | FROZEN DRONE | freeze 4 couches, drone qui glisse |
| 7 | AUTO FREEZE SWELL | freeze automatique, enchaînement doux |
| 8 | DARK CATHEDRAL | cathédrale sombre et très longue |
| 9 | TRUE DELAY | vrai delay propre (RVB MIX 0 : retard seul, 430 ms) |
| 10 | FROZEN PLATE | freeze sur une plate simple mais profonde (TIME ≈ 5 s, VOICE 0 %) |


---

## Fenêtre

- Ouverture à **50 % = 390 × 495 px** (taille minimale, jamais en dessous). Visuel net : image 1× à la taille par défaut, image 2× au-delà. **Clic droit sur la pédale** (ou sur un potard, ou menu MODE / footswitch) → *Plugin size* : 60 % / 75 % / 100 % pour cette fenêtre (« (default) » marque la taille par défaut choisie), et *Default size (new windows)* pour choisir la taille d'ouverture de toutes les nouvelles fenêtres de Freeze Shimmer (réglage enregistré dans `NINE HANDS | DSP/Freeze Shimmer/settings.xml` du dossier de données de l'utilisateur, comme Octopus).
- Redimensionnable à la souris par le coin, de 50 % (taille minimale = taille par défaut) à 150 % ; la taille est **mémorisée dans le projet** : une instance déjà ouverte rouvre à sa taille, une nouvelle instance s'ouvre à la taille par défaut choisie.

---

## Structure du dépôt

```
CMakeLists.txt
Assets/background.jpg            visuel NINE HANDS | DSP (recadré, fond sombre, couleurs rehaussées, INPUT/OUTPUT)
Source/
  PluginProcessor.*              audio, MIDI, paramètres
  PluginEditor.*                 interface : boutons vectoriels, MODE, footswitch, ligne d'état
  Params.h  Presets.h            paramètres, table MIDI, 10 presets d'usine
  dsp/                           moteurs DSP sans dépendance JUCE
    ShimmerEngine.h  Reverb.h  PitchShifter.h   (shimmer, FDN 8 lignes, octaves)
    FreezeEngine.h   FFT.h                      (freeze spectral à conservation de hauteur)
tests/dsp_test.cpp               tests automatiques du DSP (génère des WAV d'écoute)
scripts/Install-FreezeShimmer.ps1           installateur Windows
scripts/install-freezeshimmer-mac.command   installateur macOS
.github/workflows/build.yml      CI : tests + build VST3 Windows et macOS + release
```

Tests DSP en local (Linux/macOS/WSL) : `g++ -O2 -std=c++17 -ISource/dsp tests/dsp_test.cpp -o dsp_test && ./dsp_test .`

## Notes techniques

- **Freeze** : vocodeur de phase figé (FFT 4096, recouvrement 75 %). À la capture on mesure magnitude **et** avance de phase de chaque bin,
  donc la hauteur est conservée (testé : accord La/Do♯/Mi figé sans dérive). Sustain stable, resynthèse en boucle, fondus pilotés par SPEED/GLISS.
- **Shimmer** : réverb FDN 8 lignes (matrice de Householder) avec diffusion d'entrée, amortissement, modulation ; l'octave supérieure est
  réinjectée dans la boucle (pitch shifter granulaire). Gain de boucle automatiquement réduit quand TIME augmente (pas d'auto-oscillation) ; TIME max = tank figé.
- Latence : aucune déclarée (le freeze met 1-3 trames de 21 ms à atteindre son plein niveau).
- Interface redimensionnable à ratio fixe (≈ 0,89).

## Versions

- v1.1.0 : anti-gel v2 (JUCE 8.0.15, caches refaits par le timer, chien de garde, aucun appel à l'hôte depuis le thread audio)

## Licence

JUCE est utilisé sous licence **AGPLv3/GPLv3** : ce projet est distribué sous **GPL-3.0** (voir `LICENSE`).
Le visuel « Freeze Shimmer / NINE HANDS | DSP » reste la propriété de son auteur.

- v1.1.1 : menu de taille de fenêtre : « 60 % (default) », 75 %, 100 % (plus de taille en pixels)
- v1.2.0 : MIDI Learn au clic droit sur chaque commande (Clear MIDI, assignations sauvegardées avec le projet)
- v1.3.0 : clic droit > *Plugin size* > *Default size (new windows)* : taille par défaut des nouvelles fenêtres au choix (60 / 75 / 100 %), comme dans Octopus
- v1.3.1 : plus aucun CC MIDI assigné par défaut (tout passe par le MIDI Learn)
