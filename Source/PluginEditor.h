#pragma once
#include <juce_audio_processors/juce_audio_processors.h>
#include "PluginProcessor.h"
#include "Layout.h"
#include "NHKnob.h"
#include "NineHandsMenu.h"
#include "NineHandsGlow.h"
#include "NineHandsWindow.h"

class FreezeShimmerEditor;

//==============================================================================
// Lampe (LED du kit photo) : la LED éteinte est dans le fond ; allumée = lentille + halo sur la façade (halo dosé par Glow).
// MODE : lampe cliquable (page B allumée). Lampe centrale : effet actif (éteinte = bypass).
class Lamp : public juce::Component, private juce::Timer
{
public:
    Lamp (FreezeShimmerEditor& e, juce::Image lens, bool interactive) : owner (e), lensOn (std::move (lens)), clickable (interactive) {}
    void paint (juce::Graphics&) override;
    bool hitTest (int x, int y) override;
    void mouseDown (const juce::MouseEvent&) override;
    void mouseUp (const juce::MouseEvent&) override;
    void mouseWheelMove (const juce::MouseEvent&, const juce::MouseWheelDetails&) override;
    bool step (float target);       // fondu vers la cible ; vrai si l'affichage doit changer
    static constexpr float kPad = 3.5f;   // composant = kPad x la LED (place du halo)
private:
    void timerCallback() override { stopTimer(); longFired = true; owner_togglePage(); }
    void owner_togglePage();
    FreezeShimmerEditor& owner;
    juce::Image lensOn;
    bool clickable, longFired = false;
    float level = 0.0f, drawnLevel = -1.0f;
};

//==============================================================================
// Footswitch (photo du kit dans le fond) + anneau lumineux façon Octopus quand le freeze est actif
class FootSwitch : public juce::Component
{
public:
    explicit FootSwitch (FreezeShimmerEditor& e) : owner (e) {}
    void paint (juce::Graphics&) override;
    bool hitTest (int x, int y) override;
    void mouseDown (const juce::MouseEvent&) override;
    void mouseUp (const juce::MouseEvent&) override;
    bool step (float target);
private:
    FreezeShimmerEditor& owner;
    float drawnLevel = -1.0f;
    bool pressed = false, ignoreUp = false;
    juce::uint32 lastDownMs = 0;
    float level = 0.0f;
};

//==============================================================================
class FreezeShimmerEditor : public juce::AudioProcessorEditor,
                            private juce::AudioProcessorValueTreeState::Listener,
                            private juce::Timer
{
public:
    explicit FreezeShimmerEditor (FreezeShimmerProcessor&);
    ~FreezeShimmerEditor() override;

    void paint (juce::Graphics&) override;
    void resized() override;
    void parentHierarchyChanged() override;
    void mouseDown (const juce::MouseEvent&) override;
    void mouseMove (const juce::MouseEvent&) override;
    void mouseExit (const juce::MouseEvent&) override;

    FreezeShimmerProcessor& proc;

    // repère du fond (pédale plein cadre, image 1316 x 1800 px / 2) ; fenêtre par défaut = minimale = 493 px (« 60 % »), 100 % = 958 px, jusqu'à 150 %
    static constexpr float baseW = layout::frameW, baseH = layout::frameH;
    static constexpr int defaultH = 493, refH = 958, maxH = refH * 3 / 2;

    // utilisé par les sous-composants
    int  page() const { return proc.uiPage.load(); }
    void setPage (int p);
    void togglePage() { setPage (1 - page()); }
    int  choice (const char* id) const;
    void setChoice (const char* id, int index);
    void setBool (const char* id, bool v);
    bool getBool (const char* id) const;
    void cycleScene();
    void cycleMode();
    void stepPreset (int delta);
    void loadPreset (int index);
    void setWindowHeight (int h);
    static constexpr int numSizes = 3;             // 60 % (défaut d'origine) / 75 % / 100 %
    static int sizeHeight (int idx);
    float glowK() const { return (float) glowPct / 100.0f; }
    void showMainMenu (int learnA = -1, int learnB = -1, const juce::String& header = {});
    juce::PopupMenu buildContextMenu (int learnIdx = -1);   // menu clic droit (aussi pour l'outil de controle des menus)
    void handleMenuResult (int r);
    juce::String ccLabel (int learnIdx) const;     // « CC n » de l'assignation actuelle (ou « no CC »)
    int  knobParamIndex (int knob) const;          // indice dans fsp::kKnobs du paramètre actuellement lié
    juce::Colour sceneColour() const;
    juce::String learnLine;                        // message MIDI Learn de la ligne d'état (vide = aucun)

    // dernier paramètre touché (pour la ligne d'état)
    std::atomic<int>   lastIndex { -1 };
    std::atomic<float> lastValue { 0.0f };
    std::atomic<bool>  lastFromMidi { false };

private:
    void parameterChanged (const juce::String&, float) override;
    void timerCallback() override;
    void visibilityChanged() override;
    void useSoftwareRenderer();
    void bindKnobs();
    void showKnobMenu (int knobIdx);
    void showKnob7Menu();
    void showPresetMenu();
    void showMidiMap();
    void addLearnSection (juce::PopupMenu&, const juce::String& header, int learnA, int learnB = -1, int ico = NineHandsMenu::icoKnob);
    void addMidiLearnSubMenu (juce::PopupMenu&);
    void addSizeItems (juce::PopupMenu&);
    void addGlowItems (juce::PopupMenu&);
    bool handleLearnResult (int r);
    bool handleSizeResult (int r);
    bool handleGlowResult (int r);
    void flash (const juce::String& s);
    juce::String buildStatusLine() const;
    void drawPresetBar (juce::Graphics&);

    // anti-gel v2 : fond (avec la sérigraphie vectorielle) à la taille réelle en pixels, refait par le timer seulement,
    // suivi de la fenêtre hôte, de l'échelle et des redessins demandés (chien de garde)
    void rebuildCaches (float scale = 0.0f);
    void drawPrint (juce::Graphics&, int pw, int ph);
    float physicalScale() const;
    void askRepaint (juce::Component& c);
    void askRepaint (juce::Rectangle<float> unitRect);
    juce::Image background, bgScaled, ledOnImg;
    int cacheW = 0, cacheH = 0;
    float cacheScale = 0.0f;
    int resizeSettle = 0;
    void* lastPeer = nullptr;
    double lastPaintMs = 0.0, repaintAskedMs = 0.0, lastScaleCheckMs = 0.0, lastRendererCheckMs = 0.0, lastGlowCheckMs = 0.0;

    juce::Typeface::Ptr regFace, medFace, boldFace;
    NineHandsMenu::MenuLnf menuLnf;
    NineHandsWindow::HostLock hostLock;    // fenetre du DAW : jamais sous 60 %, jamais au-dela de 150 %
    int userSlot = 0;                      // preset utilisateur charge (1..9), 0 = aucun
    std::unique_ptr<juce::Drawable> logo;

    std::unique_ptr<nh::Knob> knob[7];
    Lamp modeLamp, freezeLamp;
    FootSwitch footSwitch { *this };
    bool knob7Gliss = false;
    int glowPct = 100;
    int lastMidiStampSeen = 0, lastPresetSeen = -1;
    int midiFlashTicks = 0;
    double learnLineUntil = 0.0;

    // pastille unique : barre de presets au repos, ligne d'état dès qu'un réglage bouge (fondu croisé)
    std::atomic<int> changeCounter { 0 };
    int changeSeen = 0;
    double statusUntil = 0.0, suppressUntil = 0.0, flashUntil = 0.0;
    float statusAlpha = 0.0f, drawnStatusAlpha = -1.0f;
    juce::String flashText, lastStatusText, lastPresetText;
    int hoverZone = 0, drawnHover = -1;
    bool drawnFreezeLamp = false;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (FreezeShimmerEditor)
};
