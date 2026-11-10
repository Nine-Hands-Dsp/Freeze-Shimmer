#pragma once
#include <juce_core/juce_core.h>
#include "../NineHandsFolder.h"

// NINE HANDS | DSP : reglage « Glow » (intensite du halo des lumieres : LED, anneau du footswitch), commun a toutes
// les fenetres du plugin. Quatre valeurs seulement : 25 / 50 / 75 / 100 % (defaut 100). Enregistre dans le meme
// settings.xml que la taille de fenetre (attribut glowPercent), relu par chaque fenetre ouverte toutes les quelques
// secondes (jamais dans paint).
namespace NineHandsGlow
{
    inline juce::File file (const juce::String& plugin)
    {
        return juce::File::getSpecialLocation (juce::File::userApplicationDataDirectory)
                   .getChildFile (nhd::folderName()).getChildFile (plugin).getChildFile ("settings.xml");
    }
    inline int snap (int p) { return p <= 37 ? 25 : (p <= 62 ? 50 : (p <= 87 ? 75 : 100)); }

    inline int read (const juce::String& plugin)
    {
        const auto f = file (plugin);
        if (f.existsAsFile())
            if (auto x = juce::XmlDocument::parse (f))
                return snap (x->getIntAttribute ("glowPercent", 100));
        return 100;
    }

    inline void write (const juce::String& plugin, int percent)
    {
        const auto f = file (plugin);
        juce::XmlElement x ("StudioWigaSettings");
        if (f.existsAsFile())
            if (auto old = juce::XmlDocument::parse (f))
                x = *old;
        x.setAttribute ("glowPercent", snap (percent));
        f.getParentDirectory().createDirectory();
        x.writeTo (f);
    }
}
