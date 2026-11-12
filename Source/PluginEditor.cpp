#include "PluginEditor.h"
#include "BinaryData.h"
#include "WigaWindowSize.h"
#include "NineHandsUserPresets.h"

using namespace juce;

namespace
{
const char* const kPrimary[7]   = { "dry", "effect", "blend",  "time",  "speed", "voice", "tone" };
const char* const kSecondary[7] = { "dry", "effect", "rvbmix", "delay", "layer", "depth", "rate" };
const Colour kBlue (0xff38bdf8);
const Colour kAccent (0xff7fd4ff);                  // accent du plugin (givre)
const Colour kInk (0xffeef2f7);

// « CLEAN PLATE » -> « Clean Plate »
String niceName (const char* raw)
{
    String s (String (raw).toLowerCase()), out;
    bool up = true;
    for (auto c : s) { out << (up ? String::charToString (CharacterFunctions::toUpperCase (c)) : String::charToString (c)); up = (c == ' '); }
    return out;
}

// chemin d'un texte avec espacement des lettres, centré en (x, y), tourné de rot degrés
Path textPath (const Typeface::Ptr& face, float em, float track, float x, float y, float rot, const String& s)
{
    const Font font (FontOptions (face).withPointHeight (em));
    float total = 0.0f;
    for (int i = 0; i < s.length(); ++i)
        total += GlyphArrangement::getStringWidth (font, String::charToString (s[i])) + (i > 0 ? track : 0.0f);
    const float base = (font.getAscent() - font.getDescent()) * 0.5f;
    GlyphArrangement ga;
    float px = -total * 0.5f;
    for (int i = 0; i < s.length(); ++i)
    {
        const String ch = String::charToString (s[i]);
        ga.addLineOfText (font, ch, px, base);
        px += GlyphArrangement::getStringWidth (font, ch) + track;
    }
    Path p; ga.createPath (p);
    p.applyTransform (AffineTransform::rotation (rot * MathConstants<float>::pi / 180.0f).translated (x, y));
    return p;
}
}

//==============================================================================
// Lampe
bool Lamp::hitTest (int x, int y)
{
    if (! clickable) return false;
    const auto c = getLocalBounds().getCentre().toFloat();
    const float R = (float) getWidth() / kPad * 0.40f;
    return c.getDistanceFrom (Point<float> ((float) x, (float) y)) <= R;
}

// lentille blanche : la lentille bleue désaturée (même relief, même lumière)
void Lamp::makeWhiteLens()
{
    if (lensOn.isNull()) return;
    lensWhite = lensOn.createCopy();
    Image::BitmapData bd (lensWhite, Image::BitmapData::readWrite);
    for (int y = 0; y < bd.height; ++y)
        for (int x = 0; x < bd.width; ++x)
        {
            auto c = bd.getPixelColour (x, y);
            const float a = c.getFloatAlpha();
            if (a <= 0.0f) continue;
            const float l = jmin (1.0f, (0.2126f * c.getFloatRed() + 0.7152f * c.getFloatGreen() + 0.0722f * c.getFloatBlue()) * 1.25f);
            bd.setPixelColour (x, y, Colour::fromFloatRGBA (l, l, l * 0.985f, a));
        }
}

bool Lamp::step (float target, float colourMix)
{
    level += (target - level) * (target > level ? 0.45f : 0.28f);
    if (level < 0.003f) level = 0.0f;
    if (level > 0.997f) level = 1.0f;
    colMix += (colourMix - colMix) * 0.35f;
    if (std::abs (colMix - colourMix) < 0.01f) colMix = colourMix;
    if (std::abs (level - drawnLevel) > 0.004f || std::abs (colMix - drawnMix) > 0.004f) { drawnLevel = level; drawnMix = colMix; return true; }
    return false;
}

void Lamp::paint (Graphics& g)
{
    if (level <= 0.003f) return;
    const auto c = getLocalBounds().toFloat().getCentre();
    const float u = (float) getWidth() / (layout::ledS * kPad);        // pixels par unité
    const float R = (float) getWidth() * 0.5f;
    // halo sur la façade (dosé par Glow) : la lentille elle-même reste à pleine intensité
    const float peak = 0.55f * level * owner.glowK();
    const Colour col = Colour (235, 242, 250).interpolatedWith (Colour (60, 170, 255), colMix);
    ColourGradient gr (col.withAlpha (peak), c.x, c.y, col.withAlpha (0.0f), c.x + R, c.y, true);
    gr.addColour (0.133, col.withAlpha (peak * 0.88f));
    gr.addColour (0.267, col.withAlpha (peak * 0.64f));
    gr.addColour (0.453, col.withAlpha (peak * 0.35f));
    gr.addColour (0.667, col.withAlpha (peak * 0.18f));
    gr.addColour (0.85,  col.withAlpha (peak * 0.06f));
    g.setGradientFill (gr);
    g.fillEllipse (Rectangle<float> (R * 2.0f, R * 2.0f).withCentre (c));
    if (lensOn.isValid())
    {
        const auto r = Rectangle<float> (layout::ledS * u, layout::ledS * u).withCentre (c);
        g.setImageResamplingQuality (Graphics::highResamplingQuality);
        if (lensWhite.isValid() && colMix < 0.999f) { g.setOpacity (level * (1.0f - colMix)); g.drawImage (lensWhite, r); }
        g.setOpacity (level * colMix); g.drawImage (lensOn, r);
        g.setOpacity (1.0f);
    }
}

void Lamp::mouseDown (const MouseEvent& e)
{
    longFired = false;
    if (e.mods.isPopupMenu())
    {
        owner.showMainMenu (FreezeShimmerProcessor::kLearnScene, FreezeShimmerProcessor::kLearnFMode, "MODE button");
        longFired = true;
        return;
    }
    startTimer (800);
}

void Lamp::owner_togglePage() { owner.togglePage(); }   // maintien ~1 s : page secondaire (comme la pédale)

void Lamp::mouseWheelMove (const MouseEvent&, const MouseWheelDetails& w)
{
    if (w.deltaY > 0.0f)      owner.stepPreset (1);
    else if (w.deltaY < 0.0f) owner.stepPreset (-1);
}

void Lamp::mouseUp (const MouseEvent& e)
{
    stopTimer();
    if (longFired || e.mods.isPopupMenu()) return;
    if (e.mods.isShiftDown()) owner.cycleMode();
    else                      owner.cycleScene();
}

//==============================================================================
// Footswitch
bool FootSwitch::hitTest (int x, int y)
{
    const auto c = getLocalBounds().getCentre().toFloat();
    return c.getDistanceFrom (Point<float> ((float) x, (float) y)) <= (float) getWidth() * (layout::footR * 1.35f / layout::fsS);
}

bool FootSwitch::step (float target)
{
    level += (target - level) * (target > level ? 0.45f : 0.28f);
    if (level < 0.003f) level = 0.0f;
    if (level > 0.997f) level = 1.0f;
    if (std::abs (level - drawnLevel) > 0.004f) { drawnLevel = level; return true; }
    return false;
}

void FootSwitch::paint (Graphics& g)
{
    const auto c = getLocalBounds().toFloat().getCentre();
    const float u = (float) getWidth() / layout::fsS;                 // pixels par unité
    if (level > 0.003f)
    {
        // anneau et halo d'Octopus : traits de halo (largeur 20 -> 3, pas 1,5) à 0,075 x Glow, puis anneau plein et filet clair
        const float ringR = layout::footR * 1.0775f * u, ringW = layout::footR * 0.0674f * u * 0.5f;
        const Colour col (88, 200, 255);
        const float k = ringR / (layout::footR * 1.0775f * u) * 0.639f * u;     // unités de largeur -> pixels
        for (float t = 20.0f; t >= 3.0f; t -= 1.5f)
        {
            g.setColour (col.withAlpha (0.075f * owner.glowK() * level));
            g.drawEllipse (Rectangle<float> (ringR * 2.0f, ringR * 2.0f).withCentre (c), t * k);
        }
        g.setColour (col.withAlpha (0.85f * level));
        g.drawEllipse (Rectangle<float> (ringR * 2.0f, ringR * 2.0f).withCentre (c), ringW * 2.0f);
        g.setColour (Colour (215, 240, 255).withAlpha (0.90f * level));
        g.drawEllipse (Rectangle<float> (ringR * 2.0f, ringR * 2.0f).withCentre (c), ringW * 0.84f);
    }
    if (pressed)
    {
        // bouton assombri tant qu'on appuie (disque noir à 25 %)
        const float r = layout::footR * u * 0.98f;
        g.setColour (Colours::black.withAlpha (0.25f));
        g.fillEllipse (Rectangle<float> (r * 2.0f, r * 2.0f).withCentre (c));
    }
}

void FootSwitch::mouseDown (const MouseEvent& e)
{
    if (e.mods.isPopupMenu()) { owner.showMainMenu (FreezeShimmerProcessor::kLearnFreeze, FreezeShimmerProcessor::kLearnRelease, "Footswitch"); return; }
    pressed = true;
    ignoreUp = false;
    const auto now = Time::getMillisecondCounter();
    const bool doubleClick = (now - lastDownMs) < 380;
    lastDownMs = now;

    if (doubleClick)
    {
        // double-clic : arrête le freeze
        owner.proc.postCommand (FreezeShimmerProcessor::cmdRelease);
        ignoreUp = true;
        lastDownMs = 0;
    }
    else if (owner.choice ("fmode") != 2)
    {
        // maintenu : fige ce qui est entendu (LATCH : la capture reste après le relâchement ; MOMENT : seulement tant que l'on appuie)
        owner.proc.postCommand (FreezeShimmerProcessor::cmdHoldOn);
    }
    repaint();
}

void FootSwitch::mouseUp (const MouseEvent& e)
{
    if (! pressed) return;
    pressed = false;
    if (! e.mods.isPopupMenu() && ! ignoreUp)
    {
        if (owner.choice ("fmode") == 2) owner.proc.postCommand (FreezeShimmerProcessor::cmdToggleAuto);   // AUTO : arme / désarme
        else                             owner.proc.postCommand (FreezeShimmerProcessor::cmdHoldOff);
    }
    repaint();
}

//==============================================================================
FreezeShimmerEditor::FreezeShimmerEditor (FreezeShimmerProcessor& p)
    : AudioProcessorEditor (&p), proc (p),
      modeLamp (*this, ImageCache::getFromMemory (BinaryData::led_on_png, BinaryData::led_on_pngSize), true),
      freezeLamp (*this, ImageCache::getFromMemory (BinaryData::led_on_png, BinaryData::led_on_pngSize), false)
{
    background = ImageCache::getFromMemory (BinaryData::background_png, BinaryData::background_pngSize);       // 1316 x 1800
    regFace  = Typeface::createSystemTypefaceFor (BinaryData::PoppinsRegular_ttf, BinaryData::PoppinsRegular_ttfSize);
    medFace  = Typeface::createSystemTypefaceFor (BinaryData::PoppinsMedium_ttf, BinaryData::PoppinsMedium_ttfSize);
    boldFace = Typeface::createSystemTypefaceFor (BinaryData::PoppinsBold_ttf, BinaryData::PoppinsBold_ttfSize);
    if (auto xml = XmlDocument::parse (String::fromUTF8 (BinaryData::NineHandsLogoWhite_svg, BinaryData::NineHandsLogoWhite_svgSize)))
        logo = Drawable::createFromSVG (*xml);
    menuLnf.f = { regFace, medFace, boldFace };
    glowPct = NineHandsGlow::percent (JucePlugin_Name);

    nh::Knob::Layers L;
    L.shadow    = ImageCache::getFromMemory (BinaryData::knob_shadow_png,    BinaryData::knob_shadow_pngSize);
    L.crown     = ImageCache::getFromMemory (BinaryData::knob_crown_png,     BinaryData::knob_crown_pngSize);
    L.cap       = ImageCache::getFromMemory (BinaryData::knob_cap_png,       BinaryData::knob_cap_pngSize);
    L.marker    = ImageCache::getFromMemory (BinaryData::knob_marker_png,    BinaryData::knob_marker_pngSize);
    L.highlight = ImageCache::getFromMemory (BinaryData::knob_highlight_png, BinaryData::knob_highlight_pngSize);
    for (int i = 0; i < 7; ++i)
    {
        knob[(size_t) i] = std::make_unique<nh::Knob> (L);
        knob[(size_t) i]->setMouseCursor (MouseCursor::PointingHandCursor);
        addAndMakeVisible (*knob[(size_t) i]);
    }
    for (int i = 0; i < 6; ++i) knob[(size_t) i]->onRightClick = [this, i] (const MouseEvent&) { showKnobMenu (i); };
    knob[6]->onRightClick = [this] (const MouseEvent&) { showKnob7Menu(); };
    addAndMakeVisible (modeLamp);
    addAndMakeVisible (freezeLamp);
    addAndMakeVisible (footSwitch);
    modeLamp.setMouseCursor (MouseCursor::PointingHandCursor);
    footSwitch.setMouseCursor (MouseCursor::PointingHandCursor);

    for (int i = 0; i < fsp::kNumKnobs; ++i) proc.apvts.addParameterListener (fsp::kKnobs[i].id, this);
    for (auto id : { "scene", "fmode", "engage" }) proc.apvts.addParameterListener (id, this);

    bindKnobs();

    const double aspect = (double) baseW / (double) baseH;
    setResizable (true, true);
    setResizeLimits (roundToInt ((double) defaultH * aspect), defaultH, roundToInt ((double) maxH * aspect), maxH);
    getConstrainer()->setFixedAspectRatio (aspect);
    hostLock.setLimits (roundToInt ((double) defaultH * aspect), defaultH, roundToInt ((double) maxH * aspect), maxH);
    setOpaque (true);                      // anti-gel : l'hôte ne redessine jamais ce qui est derrière la fenêtre
    // taille mémorisée dans le projet pour cette instance si elle existe (>= taille par défaut), sinon celle choisie dans
    // le menu « Default size (new windows) »
    const int h0 = sizeHeight (NineHandsWindow::openIndex (JucePlugin_Name, proc.uiSizeIdx.load(), numSizes));   // taille du projet, sinon taille par defaut
    setSize (roundToInt ((double) h0 * aspect), h0);
    rebuildCaches();
    lastPresetSeen = proc.presetIndex.load();
    startTimerHz (30);
}

FreezeShimmerEditor::~FreezeShimmerEditor()
{
    stopTimer();
    PopupMenu::dismissAllActiveMenus();
    for (int i = 0; i < fsp::kNumKnobs; ++i) proc.apvts.removeParameterListener (fsp::kKnobs[i].id, this);
    for (auto id : { "scene", "fmode", "engage" }) proc.apvts.removeParameterListener (id, this);
}

int FreezeShimmerEditor::choice (const char* id) const { return (int) proc.apvts.getRawParameterValue (id)->load(); }
bool FreezeShimmerEditor::getBool (const char* id) const { return proc.apvts.getRawParameterValue (id)->load() > 0.5f; }

void FreezeShimmerEditor::setChoice (const char* id, int index)
{
    if (auto* p = proc.apvts.getParameter (id))
    {
        p->beginChangeGesture();
        p->setValueNotifyingHost (p->convertTo0to1 ((float) index));
        p->endChangeGesture();
    }
}

void FreezeShimmerEditor::setBool (const char* id, bool v)
{
    if (auto* p = proc.apvts.getParameter (id))
    {
        p->beginChangeGesture();
        p->setValueNotifyingHost (v ? 1.0f : 0.0f);
        p->endChangeGesture();
    }
}

void FreezeShimmerEditor::loadPreset (int index)
{
    suppressUntil = Time::getMillisecondCounterHiRes() + 400.0;
    statusUntil = 0.0;
    proc.applyPreset (index);
    lastPresetSeen = proc.presetIndex.load();
    lastIndex.store (104);
    lastValue.store ((float) lastPresetSeen);
    lastFromMidi.store (false);
}

void FreezeShimmerEditor::stepPreset (int delta)
{
    loadPreset ((proc.presetIndex.load() + delta + fsp::kNumPresets) % fsp::kNumPresets);
}

int FreezeShimmerEditor::sizeHeight (int idx)
{
    const int h[numSizes] = { defaultH, roundToInt ((float) refH * 0.75f), refH };
    return h[jlimit (0, numSizes - 1, idx)];
}

void FreezeShimmerEditor::setWindowHeight (int h)
{
    h = jlimit (defaultH, maxH, h);
    setSize (roundToInt ((double) h * (double) baseW / (double) baseH), h);
    hostLock.enforce();
}

void FreezeShimmerEditor::cycleScene() { setChoice ("scene", (choice ("scene") + 1) % 3); }
void FreezeShimmerEditor::cycleMode()  { setChoice ("fmode", (choice ("fmode") + 1) % 3); }

Colour FreezeShimmerEditor::sceneColour() const
{
    switch (choice ("scene"))
    {
        case 0:  return Colour (0xff4ade80);   // intergalactic : vert
        case 1:  return Colour (0xfffb923c);   // off-world : orange
        default: return Colour (0xfff43f5e);   // etherdust : rouge
    }
}

void FreezeShimmerEditor::setPage (int p)
{
    proc.uiPage.store (p);
    bindKnobs();
    repaint();
}

int FreezeShimmerEditor::knobParamIndex (int k) const
{
    const char* id = (k == 6 && knob7Gliss) ? "gliss" : (page() == 0 ? kPrimary[k] : kSecondary[k]);
    return fsp::findKnob (id);
}

void FreezeShimmerEditor::bindKnobs()
{
    for (int i = 0; i < 7; ++i)
    {
        const int pi = knobParamIndex (i);
        const bool sec = (i >= 2 && page() == 1) || (i == 6 && knob7Gliss);
        knob[(size_t) i]->setRing (sec);                   // liseré bleu = bouton de la page secondaire
        knob[(size_t) i]->bind (*proc.apvts.getParameter (fsp::kKnobs[pi].id));
    }
    lastIndex.store (-1);
}

void FreezeShimmerEditor::flash (const String& s)
{
    flashText = s;
    flashUntil = Time::getMillisecondCounterHiRes() + 1800.0;
    statusUntil = jmax (statusUntil, flashUntil);
}

//==============================================================================
// Menus (design d'Octopus, ouverts là où on clique)
void FreezeShimmerEditor::addSizeItems (PopupMenu& sizes)
{
    const char* names[numSizes] = { "60 %", "75 %", "100 %" };
    const int def = WigaWindowSize::defaultIndex (JucePlugin_Name, numSizes);
    const int curH = getHeight();
    PopupMenu defSizes;
    for (int i = 0; i < numSizes; ++i)
    {
        sizes.addItem (301 + i, String (names[i]) + (i == def ? "  (default)" : ""), true, std::abs (curH - sizeHeight (i)) <= 8);
        defSizes.addItem (320 + i, names[i], true, i == def);
    }
    sizes.addSeparator();
    sizes.addSubMenu ("Default size (new windows)", defSizes);
}

bool FreezeShimmerEditor::handleSizeResult (int r)
{
    int inst = proc.uiSizeIdx.load();
    const int sz = NineHandsWindow::handleSize (r, JucePlugin_Name, numSizes, inst);
    if (sz < 0) return false;
    proc.uiSizeIdx = inst;
    setWindowHeight (sizeHeight (sz));
    return true;
}

// Glow : intensité du halo des lumières (25 / 50 / 75 / 100 %), commune à toutes les fenêtres du plugin
void FreezeShimmerEditor::addGlowItems (PopupMenu& m)
{
    PopupMenu glow;
    for (int v : { 25, 50, 75, 100 })
        glow.addItem (600 + v, "Glow " + String (v) + " %" + (v == 100 ? "  (default)" : ""), true, glowPct == v);
    m.addSubMenu ("Glow (halo of the lights)", glow);
}

bool FreezeShimmerEditor::handleGlowResult (int r)
{
    const int pc = NineHandsWindow::handleGlow (r, JucePlugin_Name);
    if (pc == 0) return false;
    glowPct = pc;
    NineHandsGlow::setPercent (JucePlugin_Name, glowPct);
    flash ("Glow  " + String (glowPct) + " %");
    modeLamp.repaint(); freezeLamp.repaint(); footSwitch.repaint();
    return true;
}

String FreezeShimmerEditor::ccLabel (int i) const
{
    const int cc = proc.ccMap[jlimit (0, FreezeShimmerProcessor::kNumLearn - 1, i)].load();
    return cc >= 0 ? "CC " + String (cc) : String ("no CC");
}

void FreezeShimmerEditor::addLearnSection (PopupMenu& m, const String& header, int a, int b, int ico)
{
    const int lt = proc.learnTarget.load();
    const String sub = b >= 0 ? String() : (proc.ccMap[a].load() >= 0 ? "MIDI: " + ccLabel (a) : String ("MIDI: not assigned"));
    NineHandsMenu::addHeader (m, menuLnf.f, ico, kAccent, header, sub);
    for (int i : { a, b })
    {
        if (i < 0) continue;
        const String name = FreezeShimmerProcessor::learnDef (i).name;
        m.addItem (1000 + i, "MIDI Learn: " + name + " (" + ccLabel (i) + ")", true, lt == i);
        m.addItem (1100 + i, "Clear MIDI: " + name, proc.ccMap[i].load() >= 0);
    }
    if (lt >= 0) m.addItem (1200, "Cancel MIDI learn");
    m.addSeparator();
}

void FreezeShimmerEditor::addMidiLearnSubMenu (PopupMenu& m)
{
    PopupMenu midi;
    const int lt = proc.learnTarget.load();
    for (int i = 0; i < FreezeShimmerProcessor::kNumLearn; ++i)
        midi.addItem (1000 + i, "Learn: " + String (FreezeShimmerProcessor::learnDef (i).name) + " (" + ccLabel (i) + ")", true, lt == i);
    midi.addSeparator();
    if (lt >= 0) midi.addItem (1200, "Cancel MIDI learn");
    midi.addItem (1201, "Clear all MIDI assignments");
    m.addSubMenu ("MIDI Learn", midi);
}

bool FreezeShimmerEditor::handleLearnResult (int r)
{
    const int n = FreezeShimmerProcessor::kNumLearn;
    if (r >= 1000 && r < 1000 + n)      proc.learnTarget.store (proc.learnTarget.load() == r - 1000 ? -1 : r - 1000);   // re-cliquer annule
    else if (r >= 1100 && r < 1100 + n) proc.ccMap[r - 1100].store (-1);
    else if (r == 1200)                 proc.learnTarget.store (-1);
    else if (r == 1201)                 { proc.learnTarget.store (-1); proc.resetMidiMap(); }
    else return false;
    return true;
}

PopupMenu FreezeShimmerEditor::buildContextMenu (int learnIdx)
{
    using namespace NineHandsMenu;
    PopupMenu m;
    m.setLookAndFeel (&menuLnf);
    const int lt = proc.learnTarget.load();
    auto ccText = [this] (int i) { const int cc = proc.ccMap[i].load(); return cc >= 0 ? "CC " + String (cc) : String ("not assigned"); };
    if (learnIdx >= 0)
    {
        // menu d'une commande (tronc commun) : en-tete, MIDI Learn, Clear MIDI, Cancel MIDI learn
        const String name = FreezeShimmerProcessor::learnDef (learnIdx).name;
        addHeader (m, menuLnf.f, learnIdx < fsp::kNumKnobs ? icoKnob : learnIdx == FreezeShimmerProcessor::kLearnFreeze ? icoPedal : icoSwitch,
                   ::kAccent, name, "MIDI: " + ccText (learnIdx));
        m.addItem (1000 + learnIdx, "MIDI Learn: " + name, true, lt == learnIdx);
        m.addItem (1100 + learnIdx, "Clear MIDI: " + name, proc.ccMap[learnIdx].load() >= 0);
        m.addItem (1200, "Cancel MIDI learn", lt >= 0);
        return m;
    }

    addHeader (m, menuLnf.f, icoPedal, ::kAccent, "Freeze Shimmer", "Reverb  v" + String (JucePlugin_VersionString));
    PopupMenu presets, scenes, modes;
    for (int i = 0; i < fsp::kNumPresets; ++i)
        presets.addItem (200 + i, String (i + 1) + ". " + niceName (fsp::kPresets[i].name), true, proc.presetIndex.load() == i && userSlot == 0);
    m.addSubMenu ("Factory presets", presets);
    NineHandsUserPresets::addMenus (m, "Freeze Shimmer", 400, 500, userSlot);
    m.addSeparator();
    for (int i = 0; i < 3; ++i) scenes.addItem (1 + i, fsp::kSceneNames[i], true, choice ("scene") == i);
    for (int i = 0; i < 3; ++i) modes.addItem (11 + i, fsp::kModeNames[i], true, choice ("fmode") == i);
    m.addSubMenu ("Scene (shimmer)", scenes);
    m.addSubMenu ("Mode freeze", modes);
    m.addItem (21, "Knobs: page A (primary)", true, page() == 0);
    m.addItem (22, "Knobs: page B (secondary, blue)", true, page() == 1);
    m.addItem (30, "Effect on (bypass when unticked)", true, getBool ("engage"));
    m.addItem (31, "Stop the freeze (or double-click footswitch)");
    m.addSeparator();

    PopupMenu midi;
    midi.addSectionHeader ("MIDI Learn");
    for (int i = 0; i < FreezeShimmerProcessor::kNumLearn; ++i)
        midi.addItem (1000 + i, "Learn: " + String (FreezeShimmerProcessor::learnDef (i).name) + "  (" + ccText (i) + ")", true, lt == i);
    midi.addSeparator();
    midi.addItem (1200, "Cancel MIDI learn", lt >= 0);
    midi.addItem (1201, "Clear all MIDI assignments");
    midi.addSeparator();
    NineHandsWindow::addMidiFootswitchMode (midi, ! proc.midiFsMomentary.load());
    midi.addSeparator();
    NineHandsWindow::addProgramChangeInfo (midi);
    m.addSubMenu ("MIDI", midi);
    m.addSeparator();

    const char* names[numSizes] = { "60 %", "75 %", "100 %" };
    const int heights[numSizes] = { sizeHeight (0), sizeHeight (1), sizeHeight (2) };
    m.addSubMenu ("Plugin size", NineHandsWindow::sizeMenu (JucePlugin_Name, numSizes, names, heights, getHeight()));
    m.addSubMenu ("Glow intensity", NineHandsWindow::glowMenu (glowPct));
    return m;
}

void FreezeShimmerEditor::handleMenuResult (int r)
{
    if (r == 0 || r == 9001) return;
    if (handleLearnResult (r) || handleGlowResult (r) || handleSizeResult (r)) return;
    if (r == NineHandsWindow::idLatch || r == NineHandsWindow::idMomentary) proc.midiFsMomentary = r == NineHandsWindow::idMomentary;
    else if (r >= 1 && r <= 3)   setChoice ("scene", r - 1);
    else if (r >= 11 && r <= 13) setChoice ("fmode", r - 11);
    else if (r == 21)            setPage (0);
    else if (r == 22)            setPage (1);
    else if (r == 30)            setBool ("engage", ! getBool ("engage"));
    else if (r == 31)            proc.postCommand (FreezeShimmerProcessor::cmdRelease);
    else if (r >= 200 && r < 200 + fsp::kNumPresets) { loadPreset (r - 200); userSlot = 0; }
    else if (r > 400 && r < 410) { if (NineHandsUserPresets::load (proc, "Freeze Shimmer", r - 400)) { userSlot = r - 400; flash ("User " + String (userSlot)); } }
    else if (r > 500 && r < 510) { if (NineHandsUserPresets::save (proc, "Freeze Shimmer", r - 500, { "midichan" })) { userSlot = r - 500; flash ("Saved  User " + String (userSlot)); } }
}

void FreezeShimmerEditor::showMainMenu (int learnA, int learnB, const String& header)
{
    ignoreUnused (learnB, header);
    auto m = buildContextMenu (learnA);
    m.showMenuAsync (PopupMenu::Options().withMousePosition(),      // toujours là où l'on clique
        [safe = Component::SafePointer<FreezeShimmerEditor> (this)] (int r) { if (safe != nullptr) safe->handleMenuResult (r); });
}

void FreezeShimmerEditor::showKnobMenu (int k)
{
    auto m = buildContextMenu (knobParamIndex (k));
    m.showMenuAsync (PopupMenu::Options().withMousePosition(),
        [safe = Component::SafePointer<FreezeShimmerEditor> (this)] (int r) { if (safe != nullptr) safe->handleMenuResult (r); });
}

void FreezeShimmerEditor::showKnob7Menu()
{
    // tronc commun, plus le choix TONE / RATE / GLISS propre a ce bouton
    auto m = buildContextMenu (knobParamIndex (6));
    m.addSeparator();
    m.addItem (1, "TONE / RATE (follows the page)", true, ! knob7Gliss);
    m.addItem (2, "GLISS (freeze)", true, knob7Gliss);
    m.showMenuAsync (PopupMenu::Options().withMousePosition(),
        [safe = Component::SafePointer<FreezeShimmerEditor> (this)] (int r)
        {
            if (safe == nullptr || r == 0) return;
            auto& ed = *safe;
            if (r == 1 || r == 2) { ed.knob7Gliss = (r == 2); ed.bindKnobs(); return; }
            ed.handleMenuResult (r);
        });
}

void FreezeShimmerEditor::showPresetMenu()
{
    PopupMenu m;
    NineHandsMenu::addHeader (m, menuLnf.f, NineHandsMenu::icoPreset, kAccent, "Presets", niceName (fsp::kPresets[proc.presetIndex.load()].name));
    for (int i = 0; i < fsp::kNumPresets; ++i)
        m.addItem (200 + i, String (i + 1) + "  " + niceName (fsp::kPresets[i].name), true, proc.presetIndex.load() == i);
    m.setLookAndFeel (&menuLnf);
    m.showMenuAsync (PopupMenu::Options().withMousePosition(),
        [safe = Component::SafePointer<FreezeShimmerEditor> (this)] (int r)
        {
            if (safe != nullptr && r >= 200 && r < 200 + fsp::kNumPresets) safe->loadPreset (r - 200);
        });
}

void FreezeShimmerEditor::showMidiMap()
{
    // assignations actuelles (MIDI Learn : clic droit sur une commande)
    String t;
    for (int i = 0; i < fsp::kNumKnobs; ++i)
        t << ccLabel (i) << "  =  " << fsp::kKnobs[i].name << "\n";
    t << "\n" << ccLabel (FreezeShimmerProcessor::kLearnScene)   << "  =  Scene (0-42 / 43-85 / 86-127)"
      << "\n" << ccLabel (FreezeShimmerProcessor::kLearnFMode)   << "  =  Freeze mode LATCH / MOMENT / AUTO"
      << "\n" << ccLabel (FreezeShimmerProcessor::kLearnFreeze)  << "  =  Footswitch freeze (>= 64)"
      << "\n" << ccLabel (FreezeShimmerProcessor::kLearnEngage)  << "  =  Effect on (>= 64) / bypass"
      << "\n" << ccLabel (FreezeShimmerProcessor::kLearnRelease) << "  =  Release the freeze"
      << "\nProgram Change 0-9  =  Factory preset";
    AlertWindow::showMessageBoxAsync (MessageBoxIconType::InfoIcon, "Freeze Shimmer - MIDI map", t);
}

//==============================================================================
// Souris : barre de presets (flèches = précédent / suivant, nom = menu), clic droit = menu principal
static int presetZoneAt (Point<float> p)
{
    const auto r = layout::presetRect;
    if (! r.contains (p)) return 0;
    if (p.x < r.getX() + 34.0f) return 1;
    if (p.x > r.getRight() - 34.0f) return 3;
    return 2;
}

void FreezeShimmerEditor::mouseMove (const MouseEvent& e)
{
    hoverZone = presetZoneAt (e.position / ((float) getHeight() / baseH));
    setMouseCursor (hoverZone != 0 ? MouseCursor::PointingHandCursor : MouseCursor::NormalCursor);
}

void FreezeShimmerEditor::mouseExit (const MouseEvent&) { hoverZone = 0; }

void FreezeShimmerEditor::mouseDown (const MouseEvent& e)
{
    if (e.mods.isPopupMenu()) { showMainMenu(); return; }
    const auto p = e.position / ((float) getHeight() / baseH);
    if (layout::presetRect.contains (p) && statusAlpha > 0.0f) { statusUntil = 0.0; learnLineUntil = 0.0; flashUntil = 0.0; }   // la ligne d'état ne bloque pas
    switch (presetZoneAt (p))
    {
        case 1: stepPreset (-1); break;
        case 2: showPresetMenu(); break;
        case 3: stepPreset (1); break;
        default: break;
    }
}

//==============================================================================
void FreezeShimmerEditor::parameterChanged (const String& id, float v)
{
    const int k = fsp::findKnob (id);
    int idx = k;
    if (k < 0)
    {
        if (id == "scene") idx = 100;
        else if (id == "fmode") idx = 101;
        else if (id == "engage") idx = 102;
        else return;
    }
    lastIndex.store (idx);
    lastValue.store (v);
    lastFromMidi.store (proc.lastMidiStamp.load() != lastMidiStampSeen);
    changeCounter.fetch_add (1);
}

String FreezeShimmerEditor::buildStatusLine() const
{
    const double now = Time::getMillisecondCounterHiRes();
    if (flashText.isNotEmpty() && now < flashUntil) return flashText;
    if (learnLine.isNotEmpty()) return learnLine;
    const int idx = lastIndex.load();
    const float v = lastValue.load();
    String left, right;
    if (idx >= 0 && idx < fsp::kNumKnobs)
    {
        left = String (fsp::kKnobs[idx].name) + "  " + fsp::formatValue (idx, v);
        if (proc.ccMap[idx].load() >= 0) right = ccLabel (idx) + " = " + String (fsp::toMidi (v));
    }
    else if (idx == 100) { const int s = jlimit (0, 2, (int) v); left = "SCENE  " + fsp::kSceneNames[s]; if (proc.ccMap[FreezeShimmerProcessor::kLearnScene].load() >= 0) right = ccLabel (FreezeShimmerProcessor::kLearnScene) + " = " + String (s * 43); }
    else if (idx == 101) { const int s = jlimit (0, 2, (int) v); left = "MODE  " + fsp::kModeNames[s];   if (proc.ccMap[FreezeShimmerProcessor::kLearnFMode].load() >= 0) right = ccLabel (FreezeShimmerProcessor::kLearnFMode) + " = " + String (s * 43); }
    else if (idx == 102) { left = v > 0.5f ? "EFFECT ON" : "BYPASS"; }
    if (left.isEmpty()) return {};
    return right.isNotEmpty() ? left + String::fromUTF8 ("  \xc2\xb7  ") + right : left;
}

void FreezeShimmerEditor::timerCallback()
{
    const double now = Time::getMillisecondCounterHiRes();
    const int stamp = proc.lastMidiStamp.load();
    if (stamp != lastMidiStampSeen) { lastMidiStampSeen = stamp; midiFlashTicks = 24; }
    if (midiFlashTicks > 0) --midiFlashTicks; else lastFromMidi.store (false);
    const int pr = proc.presetIndex.load();
    if (pr != lastPresetSeen) { lastPresetSeen = pr; suppressUntil = now + 400.0; statusUntil = 0.0; lastIndex.store (104); lastValue.store ((float) pr); lastFromMidi.store (false); }

    // moteur logiciel : seulement si la fenêtre hôte a changé, ou au plus une fois par seconde
    if (getPeer() != lastPeer || now - lastRendererCheckMs > 1000.0) { lastRendererCheckMs = now; useSoftwareRenderer(); }
    hostLock.track (*this);

    // caches : reconstruits ici seulement (jamais dans paint)
    if (resizeSettle > 0 && --resizeSettle == 0) rebuildCaches();
    else if (resizeSettle == 0 && now - lastScaleCheckMs > 250.0)
    {
        lastScaleCheckMs = now;
        const float sc = physicalScale();
        if (std::abs (sc - cacheScale) > 0.01f) rebuildCaches (sc);
    }

    // chien de garde : un redessin demandé n'arrive pas -> on relance le moteur de rendu et on redessine tout
    if (repaintAskedMs > 0.0 && isShowing() && now - repaintAskedMs > 1500.0 && lastPaintMs < repaintAskedMs)
    {
        repaintAskedMs = 0.0;
        lastPeer = nullptr;
        useSoftwareRenderer();
        repaint();
    }

    // Glow choisi dans une autre fenêtre : relu toutes les 3 s
    if (now - lastGlowCheckMs > 3000.0)
    {
        lastGlowCheckMs = now;
        const int gp = NineHandsGlow::percent (JucePlugin_Name);
        if (gp != glowPct) { glowPct = gp; modeLamp.repaint(); freezeLamp.repaint(); footSwitch.repaint(); }
    }

    // lampes : MODE = toujours allumée, blanche en page A, bleue en page B ; LED centrale = effet actif (engage, éteinte = bypass) ; halo du footswitch = freeze actif
    const bool frozen = proc.frozenState.load();
    if (modeLamp.step (1.0f, page() == 1 ? 1.0f : 0.0f)) askRepaint (modeLamp);
    if (freezeLamp.step (getBool ("engage") ? 1.0f : 0.0f)) askRepaint (freezeLamp);
    // halo du footswitch : il pulse doucement tant que le freeze est actif (comme l'ancienne pédale)
    const float pulse = frozen ? 0.72f + 0.28f * std::sin ((float) Time::getMillisecondCounter() * 0.004f) : 0.0f;
    if (footSwitch.step (pulse))                     askRepaint (footSwitch);

    // MIDI Learn : attente puis confirmation 2 s dans la ligne d'état
    {
        const int learned = proc.lastLearned.exchange (-1);
        const int lt = proc.learnTarget.load();
        if (learned >= 0)
        {
            learnLine = String (FreezeShimmerProcessor::learnDef (learned).name) + " = " + ccLabel (learned);
            learnLineUntil = now + 2000.0;
            statusUntil = jmax (statusUntil, learnLineUntil);
        }
        else if (lt >= 0)
        {
            learnLine = "MIDI LEARN: move a control for " + String (FreezeShimmerProcessor::learnDef (lt).name);
            learnLineUntil = now + 200.0;
            statusUntil = jmax (statusUntil, now + 200.0);
        }
        else if (now >= learnLineUntil)
            learnLine.clear();
    }

    // un réglage a bougé : la ligne d'état prend la place de la barre de presets (~2,5 s après le dernier mouvement)
    const int cc = changeCounter.load();
    if (cc != changeSeen) { changeSeen = cc; if (now > suppressUntil) { statusUntil = now + 2500.0; flashText.clear(); } }
    for (auto& k : knob) if (k->isMouseButtonDown()) { statusUntil = now + 2500.0; }

    const float target = now < statusUntil ? 1.0f : 0.0f;
    statusAlpha += (target - statusAlpha) * (target > statusAlpha ? 0.45f : 0.25f);   // ~120 ms à l'apparition, ~300 ms au retour
    if (statusAlpha < 0.005f) statusAlpha = 0.0f;
    if (statusAlpha > 0.995f) statusAlpha = 1.0f;

    const String st = buildStatusLine(), pn = niceName (fsp::kPresets[jlimit (0, fsp::kNumPresets - 1, pr)].name);
    const bool textChanged = st != lastStatusText || pn != lastPresetText;
    lastStatusText = st; lastPresetText = pn;
    if (std::abs (statusAlpha - drawnStatusAlpha) > 0.003f || textChanged || hoverZone != drawnHover || midiFlashTicks > 0)
    {
        drawnStatusAlpha = statusAlpha; drawnHover = hoverZone;
        askRepaint (layout::presetRect.expanded (3.0f));
    }
}

// pastille : barre de presets au repos ; la ligne d'état prend sa place en fondu croisé (même pastille, même police)
void FreezeShimmerEditor::drawPresetBar (Graphics& g)
{
    const auto r = layout::presetRect;
    const float a = statusAlpha, pa = 1.0f - a;
    const Font f (FontOptions (medFace).withHeight (layout::presetFont));
    const float aw = 34.0f;
    const bool midiFlash = midiFlashTicks > 0;
    if (pa > 0.0f)
    {
        auto arrow = [&] (Rectangle<float> ar, bool left, bool hot)
        {
            Path p; const auto c = ar.getCentre(); const float sz = 5.5f;
            if (left) p.addTriangle (c.x + sz * 0.6f, c.y - sz, c.x + sz * 0.6f, c.y + sz, c.x - sz * 0.8f, c.y);
            else      p.addTriangle (c.x - sz * 0.6f, c.y - sz, c.x - sz * 0.6f, c.y + sz, c.x + sz * 0.8f, c.y);
            g.setColour (Colour (150, 160, 172).interpolatedWith (Colours::white, hot ? 1.0f : 0.0f).withAlpha (pa));
            g.fillPath (p);
        };
        arrow (r.withWidth (aw), true, hoverZone == 1);
        arrow (r.withTrimmedLeft (r.getWidth() - aw), false, hoverZone == 3);
        g.setFont (f);
        g.setColour (kInk.withAlpha ((hoverZone == 2 ? 1.0f : 0.92f) * pa));
        g.drawFittedText (lastPresetText, r.reduced (aw, 0.0f).toNearestInt(), Justification::centred, 1, 0.7f);
    }
    if (a > 0.0f)
    {
        g.setFont (f);
        g.setColour ((midiFlash ? Colour (0xffa7f3a0) : kInk).withAlpha (a));
        g.drawFittedText (lastStatusText.toUpperCase(), r.reduced (r.getHeight() * 0.5f, 0.0f).toNearestInt(), Justification::centred, 1, 0.6f);
    }
}

void FreezeShimmerEditor::paint (Graphics& g)
{
    lastPaintMs = Time::getMillisecondCounterHiRes();
    repaintAskedMs = 0.0;
    g.fillAll (Colour (0xff111112));          // autour des jacks : le fond de l'image est transparent
    // anti-gel : aucun rescale ici, on dessine le cache existant (ou l'original en attendant le timer)
    const Image& bg = bgScaled.isValid() ? bgScaled : background;
    g.setImageResamplingQuality (&bg == &background ? Graphics::highResamplingQuality : Graphics::lowResamplingQuality);
    if (bg.isValid()) g.drawImage (bg, getLocalBounds().toFloat());
    g.addTransform (AffineTransform::scale ((float) getHeight() / baseH));
    drawPresetBar (g);
}

//==============================================================================
// Sérigraphie vectorielle (textes, titre, logo, pastille) dessinée dans le fond à la taille réelle en pixels
void FreezeShimmerEditor::drawPrint (Graphics& g, int pw, int ph)
{
    const float ppu = (float) pw / baseW;                               // pixels par unité
    g.addTransform (AffineTransform::scale ((float) pw / baseW, (float) ph / baseH));
    g.setImageResamplingQuality (Graphics::highResamplingQuality);

    // pastille (fond sombre, contour fin) : le texte est dessiné par l'éditeur
    {
        const auto r = layout::presetRect;
        g.setColour (Colour (5, 8, 13));
        g.fillRoundedRectangle (r, r.getHeight() * 0.5f);
        g.setColour (Colour (150, 170, 190));
        g.drawRoundedRectangle (r.reduced (0.5f), r.getHeight() * 0.5f, 1.0f);
    }

    // chemins : étiquettes, titre
    Path labels[2], title[2];
    for (const auto& t : layout::texts)
        labels[t.col].addPath (textPath (t.font == 1 ? boldFace : medFace, t.em, t.track, t.x, t.y, t.rot, t.s));
    {
        const Font tf (FontOptions (boldFace).withPointHeight (layout::titleEm));
        auto adv = [&] (const String& str) { float w = 0; for (int i = 0; i < str.length(); ++i) w += GlyphArrangement::getStringWidth (tf, String::charToString (str[i])); return w; };
        const float tr = layout::titleTrack;
        const float wF = adv ("FREEZE") + 5.0f * tr, wS = adv ("SHIMMER") + 6.0f * tr;
        const float total = adv ("FREEZE SHIMMER") + 13.0f * tr;
        const float x0 = layout::titleX - total * 0.5f;
        const float sStart = x0 + adv ("FREEZE ") + 7.0f * tr;
        title[0] = textPath (boldFace, layout::titleEm, tr, x0 + wF * 0.5f, layout::titleY, 0.0f, "FREEZE");
        title[1] = textPath (boldFace, layout::titleEm, tr, sStart + wS * 0.5f, layout::titleY, 0.0f, "SHIMMER");
    }

    // ombre douce (bleu nuit) sous les étiquettes (décalage 1) et le titre (décalage 2) : masque flou à résolution réduite
    {
        const int div = jlimit (1, 4, (int) std::floor (2.0f * ppu / 1.5f));
        const int mw = pw / div + 2, mh = ph / div + 2;
        Image mask (Image::ARGB, mw, mh, true);
        {
            Graphics gm (mask);
            gm.addTransform (AffineTransform::scale (ppu / (float) div));
            gm.setColour (Colour (6, 28, 60));
            gm.fillPath (labels[0], AffineTransform::translation (1.0f, 1.0f));
            gm.fillPath (labels[1], AffineTransform::translation (1.0f, 1.0f));
            gm.fillPath (title[0], AffineTransform::translation (2.0f, 2.0f));
            gm.fillPath (title[1], AffineTransform::translation (2.0f, 2.0f));
        }
        const int rad = jmax (1, roundToInt (2.0f * ppu / (float) div));
        ImageConvolutionKernel k ((size_t) (rad * 2 + 1));
        k.createGaussianBlur ((float) rad);
        Image blurred (Image::ARGB, mw, mh, true);
        k.applyToImage (blurred, mask, mask.getBounds());
        const Rectangle<float> dest (0.0f, 0.0f, (float) mw * (float) div / ppu, (float) mh * (float) div / ppu);
        g.setImageResamplingQuality (Graphics::mediumResamplingQuality);
        for (int pass = 0; pass < 2; ++pass) { g.setOpacity (0.9f); g.drawImage (blurred, dest); }
        g.setOpacity (1.0f);
        g.setImageResamplingQuality (Graphics::highResamplingQuality);
    }

    g.setColour (Colour (232, 238, 245)); g.fillPath (labels[0]);
    g.setColour (Colour (150, 222, 255)); g.fillPath (labels[1]);
    // titre givré : dégradé vertical (haut clair), « FREEZE » blanc glacé, « SHIMMER » bleu glace
    const float ty0 = layout::titleY - layout::titleEm * 0.5f, ty1 = layout::titleY + layout::titleEm * 0.5f;
    auto fillTitle = [&] (const Path& p, Colour c)
    {
        g.setGradientFill (ColourGradient (c, 0.0f, ty0, c.withMultipliedBrightness (0.86f), 0.0f, ty1, false));
        g.fillPath (p);
    };
    fillTitle (title[0], Colour (236, 242, 248));
    fillTitle (title[1], Colour (96, 190, 240));

    // logo NINE HANDS | DSP (SVG officiel blanc, sans recoloration)
    if (logo != nullptr)
    {
        const auto vb = logo->getDrawableBounds();
        const float w = layout::logoW, h = w * vb.getHeight() / jmax (1.0f, vb.getWidth());
        logo->drawWithin (g, { layout::logoPos.x - w * 0.5f, layout::logoPos.y - h * 0.5f, w, h }, RectanglePlacement::centred, 1.0f);
    }
}

// fond déjà à la taille de la fenêtre en pixels physiques : constructeur et timer, jamais paint()
void FreezeShimmerEditor::rebuildCaches (float sc)
{
    if (sc <= 0.0f) sc = cacheScale > 0.0f ? cacheScale : physicalScale();
    const int w = getWidth(), h = getHeight();
    if (w <= 0 || h <= 0) return;
    if (w == cacheW && h == cacheH && std::abs (sc - cacheScale) < 0.01f && bgScaled.isValid()) return;

    cacheW = w; cacheH = h; cacheScale = sc;
    const int pw = roundToInt ((float) w * sc), ph = roundToInt ((float) h * sc);
    Image img = (pw >= background.getWidth()) ? background.createCopy() : background.rescaled (pw, ph, Graphics::highResamplingQuality);
    {
        Graphics g (img);
        drawPrint (g, img.getWidth(), img.getHeight());
    }
    bgScaled = img;
    repaint();
}

float FreezeShimmerEditor::physicalScale() const
{
    return jlimit (1.0f, 4.0f, (float) Component::getApproximateScaleFactorForComponent (this));
}

void FreezeShimmerEditor::askRepaint (Component& c)
{
    if (repaintAskedMs <= 0.0) repaintAskedMs = Time::getMillisecondCounterHiRes();
    repaint (c.getBounds());
}

void FreezeShimmerEditor::askRepaint (Rectangle<float> r)
{
    if (repaintAskedMs <= 0.0) repaintAskedMs = Time::getMillisecondCounterHiRes();
    repaint (r.transformedBy (AffineTransform::scale ((float) getHeight() / baseH)).getSmallestIntegerContainer());
}

//==============================================================================
// Anti-gel de la fenêtre (Windows) : JUCE 8 dessine par défaut avec Direct2D (carte graphique).
// Avec certains pilotes (Intel notamment) la fenêtre du plugin cesse de se rafraîchir alors que
// le DAW continue de tourner. Le moteur logiciel est stable partout et largement assez rapide ici.
//
// Anti-gel v2 (NINE HANDS | DSP) :
//  1. moteur de rendu logiciel forcé sur Windows, appliqué à chaque nouvelle fenêtre hôte (peer)
//     et revérifié toutes les secondes, jamais en boucle ;
//  2. aucun calcul lourd dans paint() : le fond mis à l'échelle est refait par le timer seulement,
//     après stabilisation de la taille ou quand l'échelle d'affichage change (au plus toutes les 250 ms) ;
//  3. chien de garde : si un redessin demandé n'est pas arrivé au bout de 1,5 s alors que la fenêtre
//     est visible, le moteur de rendu est réappliqué et toute la fenêtre est redessinée ;
//  4. côté audio : aucun appel à l'hôte depuis le thread audio (voir PluginProcessor).
void FreezeShimmerEditor::useSoftwareRenderer()
{
    auto* peer = getPeer();
    if (peer != lastPeer) { lastPeer = peer; repaint(); }
   #if JUCE_WINDOWS
    if (peer != nullptr)
    {
        int sw = peer->getAvailableRenderingEngines().indexOf ("Software Renderer");
        if (sw < 0) sw = 0;
        if (peer->getCurrentRenderingEngine() != sw)
            peer->setCurrentRenderingEngine (sw);
    }
   #endif
}

void FreezeShimmerEditor::parentHierarchyChanged() { useSoftwareRenderer(); hostLock.track (*this); }
void FreezeShimmerEditor::visibilityChanged()      { useSoftwareRenderer(); if (isShowing()) repaint(); }

void FreezeShimmerEditor::resized()
{
    // anti-gel : jamais de setSize ici (mise à l'échelle Windows 125 / 150 % : l'hôte arrondit les tailles) ;
    // les limites du constrainer (jamais plus petit que la taille par défaut) suffisent
    // seules les tailles choisies au menu sont enregistrees (pas celles tirees au coin)
    resizeSettle = 4;              // le fond sera refait par le timer quand la taille ne bouge plus
    const float s = (float) getHeight() / baseH;
    auto place = [s] (Component& c, Point<float> centre, float size)
    {
        c.setBounds (Rectangle<float> (size * s, size * s).withCentre ({ centre.x * s, centre.y * s }).toNearestInt());
    };
    for (int i = 0; i < 7; ++i) place (*knob[(size_t) i], layout::knobPos[i], layout::knobComp);
    place (modeLamp,   layout::modeLedPos,   layout::ledS * Lamp::kPad);
    place (freezeLamp, layout::freezeLedPos, layout::ledS * Lamp::kPad);
    place (footSwitch, layout::fsPos,        layout::fsS);
}
