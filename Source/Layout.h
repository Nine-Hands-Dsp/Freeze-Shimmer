// genere depuis l apercu valide (tools/make_layout.py) : repere 658 x 900 = fond 1316 x 1800 px / 2 - ne pas modifier a la main
#pragma once
#include <juce_graphics/juce_graphics.h>
namespace layout
{
    constexpr float frameW = 658.00f, frameH = 900.00f;   // pedale plein cadre (jacks aux bords gauche / droit)
    constexpr float bodyX = 22.00f, bodyW = 614.00f;       // boitier (entre les saillies des jacks)
    // ordre : dry, effect, blend, time, speed, voice, tone
    const juce::Point<float> knobPos[7] = { { 154.01f, 97.20f }, { 503.99f, 97.20f }, { 154.01f, 253.80f }, { 329.00f, 253.80f }, { 503.99f, 253.80f }, { 154.01f, 422.10f }, { 503.99f, 422.10f } };
    constexpr float knobComp = 143.00f;   // composant du potard (calques 1024 px), couronne = 0,742 de ce cote
    constexpr float knobCrownR = 53.05f;
    const juce::Point<float> modeLedPos { 329.49f, 55.26f }, freezeLedPos { 329.49f, 468.45f }; constexpr float ledS = 42.50f;
    const juce::Point<float> fsPos { 329.43f, 814.50f }; constexpr float footR = 39.40f, fsS = 197.60f;
    const juce::Rectangle<float> presetRect { 129.00f, 569.60f, 400.0f, 38.0f };
    constexpr float presetFont = 23.0f;
    constexpr float jackY = 526.50f;
    // serigraphie vectorielle : texte, police (0 medium, 1 bold), taille em, espacement, centre, rotation (degres), couleur (0 blanc, 1 bleu clair)
    struct Txt { const char* s; int font; float em, track, x, y, rot; int col; };
    const Txt texts[] = {
        { "DRY", 0, 22.0f, 3.5f, 154.01f, 167.20f, 0.0f, 0 },
        { "EFFECT", 0, 22.0f, 3.5f, 503.99f, 167.20f, 0.0f, 0 },
        { "BLEND", 0, 22.0f, 3.5f, 154.01f, 323.80f, 0.0f, 0 },
        { "RVB MIX", 0, 20.0f, 2.5f, 154.01f, 345.80f, 0.0f, 1 },
        { "TIME", 0, 22.0f, 3.5f, 329.00f, 323.80f, 0.0f, 0 },
        { "DELAY", 0, 20.0f, 2.5f, 329.00f, 345.80f, 0.0f, 1 },
        { "SPEED", 0, 22.0f, 3.5f, 503.99f, 323.80f, 0.0f, 0 },
        { "LAYER", 0, 20.0f, 2.5f, 503.99f, 345.80f, 0.0f, 1 },
        { "VOICE", 0, 22.0f, 3.5f, 154.01f, 492.10f, 0.0f, 0 },
        { "DEPTH", 0, 20.0f, 2.5f, 154.01f, 514.10f, 0.0f, 1 },
        { "TONE", 0, 22.0f, 3.5f, 503.99f, 492.10f, 0.0f, 0 },
        { "RATE", 0, 20.0f, 2.5f, 503.99f, 514.10f, 0.0f, 1 },
        { "GLISS", 0, 20.0f, 2.5f, 503.99f, 536.10f, 0.0f, 1 },
        { "MODE", 0, 22.0f, 3.5f, 329.49f, 93.26f, 0.0f, 0 },
        { "OUT", 0, 17.0f, 2.0f, 60.00f, 526.50f, 90.0f, 0 },
        { "IN", 0, 17.0f, 2.0f, 598.00f, 526.50f, 90.0f, 0 }
    };
    // titre « FREEZE SHIMMER » (Poppins Bold, deux couleurs) et logo NINE HANDS | DSP
    constexpr float titleEm = 42.0f, titleTrack = 2.8f, titleX = 329.0f, titleY = 651.60f;
    const juce::Point<float> logoPos { 329.0f, 686.25f }; constexpr float logoW = 190.0f;
}
