type ChatbotContext = {
  greeting: string[];
  suggestions: string[];
};

export const chatbotContexts: Record<string, ChatbotContext> = {
  default: {
    greeting: [
      `👋 Hallo! Ich bin **KIM**, dein KI-Assistent im **Fachbereich Medien**.

Ich bin eine künstliche Intelligenz, die entwickelt wurde, um deine Fragen zu beantworten. Von dieser Startseite aus kannst du allgemeine Informationen zu allen Studiengängen des Fachbereichs Medien erhalten.`,
      `Wenn du Informationen zu einem bestimmten Studiengang suchst, besuche bitte die jeweilige Studiengangsseite:
- [Bachelor Ton und Bild (BTB)](/2026-FBM-Web-KI-Chatbot/navigation/btb.html)
- [Bachelor Medientechnik (BMT)](/2026-FBM-Web-KI-Chatbot/navigation/bmt.html)
- [Bachelor Creative, Synthetic and Interactive Media (BCSIM)](/2026-FBM-Web-KI-Chatbot/navigation/bcsim.html)
- [Bachelor Data Science, AI und Intelligente Systeme (BDAISY)](/2026-FBM-Web-KI-Chatbot/navigation/bdaisy.html)
- [Bachelor Medieninformatik (BMI)](/2026-FBM-Web-KI-Chatbot/navigation/bmi.html)
- [Master Medieninformatik (MMI)](/2026-FBM-Web-KI-Chatbot/navigation/mmi.html)
- [Master Applied Research in Digital Media Technologies (MAR)](/2026-FBM-Web-KI-Chatbot/navigation/mar.html)`
    ],
    suggestions: [
      'Welche Bachelorstudiengänge gibt es?',
      'Wo kann ich Erstsemesterinfos finden?',
      'Wo finde ich den Kontakt zum Studienbüro?',
    ],
  },
  MMI: {
    greeting: [
      `👋 Willkommen! Du befindest dich auf der Seite des **Masterstudiengangs Medieninformatik (MMI)**.

Von dieser Seite helfe ich dir gern bei Fragen zu Modulen, Projekten oder allgemeine Informationen zum Studiengang MMI.`,
      `Wenn du Informationen zu anderen Studiengängen suchst, besuche bitte die jeweilige Studiengangsseite:
- [Bachelor Ton und Bild (BTB)](/2026-FBM-Web-KI-Chatbot/navigation/btb.html)
- [Bachelor Medientechnik (BMT)](/2026-FBM-Web-KI-Chatbot/navigation/bmt.html)
- [Bachelor Creative, Synthetic and Interactive Media (BCSIM)](/2026-FBM-Web-KI-Chatbot/navigation/bcsim.html)
- [Bachelor Data Science, AI und Intelligente Systeme (BDAISY)](/2026-FBM-Web-KI-Chatbot/navigation/bdaisy.html)
- [Bachelor Medieninformatik (BMI)](/2026-FBM-Web-KI-Chatbot/navigation/bmi.html)
- [Master Applied Research in Digital Media Technologies (MAR)](/2026-FBM-Web-KI-Chatbot/navigation/mar.html)`,
  `Für allgemeine Informationen zum Fachbereich Medien besuche die **[Hauptseite des Fachbereichs Medien](https://marmann.hosting.medien.hs-duesseldorf.de/2026-FBM-Web-KI-Chatbot/)**.`
    ],
    suggestions: [
      'Welche Vertiefungen gibt es im MMI?',
      'Wie lange dauert der Master Medieninformatik?',
      'Wie läuft die Bewerbung für den MMI ab?',
    ],
  },
  BMI: {
    greeting: [
      `👋 Willkommen! Du befindest dich auf der Seite des **Bachelorstudiengangs Medieninformatik (BMI)**.

Von dieser Seite helfe ich dir gern bei Fragen zu Modulen, Projekten oder allgemeine Informationen zum Studiengang BMI.`,
      `Wenn du Informationen zu anderen Studiengängen suchst, besuche bitte die jeweilige Studiengangsseite:
- [Bachelor Ton und Bild (BTB)](/2026-FBM-Web-KI-Chatbot/navigation/btb.html)
- [Bachelor Medientechnik (BMT)](/2026-FBM-Web-KI-Chatbot/navigation/bmt.html)
- [Bachelor Creative, Synthetic and Interactive Media (BCSIM)](/2026-FBM-Web-KI-Chatbot/navigation/bcsim.html)
- [Bachelor Data Science, AI und Intelligente Systeme (BDAISY)](/2026-FBM-Web-KI-Chatbot/navigation/bdaisy.html)
- [Master Medieninformatik (MMI)](/2026-FBM-Web-KI-Chatbot/navigation/mmi.html)
- [Master Applied Research in Digital Media Technologies (MAR)](/2026-FBM-Web-KI-Chatbot/navigation/mar.html)`,
  `Für allgemeine Informationen zum Fachbereich Medien besuche die **[Hauptseite des Fachbereichs Medien](https://marmann.hosting.medien.hs-duesseldorf.de/2026-FBM-Web-KI-Chatbot/)**.`
    ],
    suggestions: [
      'Welche Module sollen im 1. Semester BMI belegt werden?',
      'Wer betreut die Bachelorarbeit im BMI?',
      'Wie sieht der Studienverlaufsplan aus?',
    ],
  },
  BTB: {
    greeting: [
      `👋 Willkommen! Du befindest dich auf der Seite des **Bachelorstudiengangs Ton und Bild (BTB)**.

Von dieser Seite helfe ich dir gern bei Fragen zu Modulen, Projekten oder allgemeine Informationen zum Studiengang BTB.`,
      `Wenn du Informationen zu anderen Studiengängen suchst, besuche bitte die jeweilige Studiengangsseite:
- [Bachelor Medientechnik (BMT)](/2026-FBM-Web-KI-Chatbot/navigation/bmt.html)
- [Bachelor Creative, Synthetic and Interactive Media (BCSIM)](/2026-FBM-Web-KI-Chatbot/navigation/bcsim.html)
- [Bachelor Data Science, AI und Intelligente Systeme (BDAISY)](/2026-FBM-Web-KI-Chatbot/navigation/bdaisy.html)
- [Bachelor Medieninformatik (BMI)](/2026-FBM-Web-KI-Chatbot/navigation/bmi.html)
- [Master Medieninformatik (MMI)](/2026-FBM-Web-KI-Chatbot/navigation/mmi.html)
- [Master Applied Research in Digital Media Technologies (MAR)](/2026-FBM-Web-KI-Chatbot/navigation/mar.html)`,
  `Für allgemeine Informationen zum Fachbereich Medien besuche die **[Hauptseite des Fachbereichs Medien](https://marmann.hosting.medien.hs-duesseldorf.de/2026-FBM-Web-KI-Chatbot/)**.`
    ],
    suggestions: [
      'Was sind die technischen Schwerpunkte im BTB?',
      'Wie läuft das Praxissemester im BTB ab?',
      'Wie sieht der Studienverlaufsplan aus?',
    ],
  },
  BMT: {
    greeting: [
      `👋 Willkommen! Du befindest dich auf der Seite des **Bachelorstudiengangs Medientechnik (BMT)**.

Von dieser Seite helfe ich dir gern bei Fragen zu Modulen, Projekten oder allgemeine Informationen zum Studiengang BMT.`,
      `Wenn du Informationen zu anderen Studiengängen suchst, besuche bitte die jeweilige Studiengangsseite:
- [Bachelor Ton und Bild (BTB)](/2026-FBM-Web-KI-Chatbot/navigation/btb.html)
- [Bachelor Creative, Synthetic and Interactive Media (BCSIM)](/2026-FBM-Web-KI-Chatbot/navigation/bcsim.html)
- [Bachelor Data Science, AI und Intelligente Systeme (BDAISY)](/2026-FBM-Web-KI-Chatbot/navigation/bdaisy.html)
- [Bachelor Medieninformatik (BMI)](/2026-FBM-Web-KI-Chatbot/navigation/bmi.html)
- [Master Medieninformatik (MMI)](/2026-FBM-Web-KI-Chatbot/navigation/mmi.html)
- [Master Applied Research in Digital Media Technologies (MAR)](/2026-FBM-Web-KI-Chatbot/navigation/mar.html)`,
  `Für allgemeine Informationen zum Fachbereich Medien besuche die **[Hauptseite des Fachbereichs Medien](https://marmann.hosting.medien.hs-duesseldorf.de/2026-FBM-Web-KI-Chatbot/)**.`
    ],
    suggestions: [
      'Was sind die Grundlagen des Studiengangs BMT?',
      'Welche Module soll ich im 3. Semester belegen?',
      'Wie sieht der Studienverlaufsplan aus?',
    ],
  },
  BDAISY: {
    greeting: [
      `👋 Willkommen! Du befindest dich auf der Seite des **Bachelorstudiengangs Data Science, AI und Intelligente Systeme (BDAISY)**.

Von dieser Seite helfe ich dir gern bei Fragen zu Modulen, Projekten oder allgemeine Informationen zum Studiengang BDAISY.`,
      `Wenn du Informationen zu anderen Studiengängen suchst, besuche bitte die jeweilige Studiengangsseite:
- [Bachelor Ton und Bild (BTB)](/2026-FBM-Web-KI-Chatbot/navigation/btb.html)
- [Bachelor Medientechnik (BMT)](/2026-FBM-Web-KI-Chatbot/navigation/bmt.html)
- [Bachelor Creative, Synthetic and Interactive Media (BCSIM)](/2026-FBM-Web-KI-Chatbot/navigation/bcsim.html)
- [Bachelor Medieninformatik (BMI)](/2026-FBM-Web-KI-Chatbot/navigation/bmi.html)
- [Master Medieninformatik (MMI)](/2026-FBM-Web-KI-Chatbot/navigation/mmi.html)
- [Master Applied Research in Digital Media Technologies (MAR)](/2026-FBM-Web-KI-Chatbot/navigation/mar.html)`,
  `Für allgemeine Informationen zum Fachbereich Medien besuche die **[Hauptseite des Fachbereichs Medien](https://marmann.hosting.medien.hs-duesseldorf.de/2026-FBM-Web-KI-Chatbot/)**.`
    ],
    suggestions: [
      'Welche Module decken Machine Learning ab?',
      'Wie sieht der Studienverlauf aus?',
      'Gibt es Praxisprojekte im Studium BDAISY?',
    ],
  },
  BCSIM: {
    greeting: [
      `👋 Willkommen! Du befindest dich auf der Seite des **Bachelorstudiengangs Creative, Synthetic and Interactive Media (BCSIM)**.

Von dieser Seite helfe ich dir gern bei Fragen zu Modulen, Projekten oder allgemeine Informationen zum Studiengang BCSIM.`,
      `Wenn du Informationen zu anderen Studiengängen suchst, besuche bitte die jeweilige Studiengangsseite:
- [Bachelor Ton und Bild (BTB)](/2026-FBM-Web-KI-Chatbot/navigation/btb.html)
- [Bachelor Medientechnik (BMT)](/2026-FBM-Web-KI-Chatbot/navigation/bmt.html)
- [Bachelor Data Science, AI und Intelligente Systeme (BDAISY)](/2026-FBM-Web-KI-Chatbot/navigation/bdaisy.html)
- [Bachelor Medieninformatik (BMI)](/2026-FBM-Web-KI-Chatbot/navigation/bmi.html)
- [Master Medieninformatik (MMI)](/2026-FBM-Web-KI-Chatbot/navigation/mmi.html)
- [Master Applied Research in Digital Media Technologies (MAR)](/2026-FBM-Web-KI-Chatbot/navigation/mar.html)`,
  `Für allgemeine Informationen zum Fachbereich Medien besuche die **[Hauptseite des Fachbereichs Medien](https://marmann.hosting.medien.hs-duesseldorf.de/2026-FBM-Web-KI-Chatbot/)**.`
    ],
    suggestions: [
      'Was ist das Ziel des BCSIM Studiengangs?',
      'Welche Module werden im BCSIM angeboten?',
      'Wie kreativ ist das Studium BCSIM?',
    ],
  },
  MAR: {
    greeting: [
      `👋 Willkommen! Du befindest dich auf der Seite des **Masterstudiengangs Applied Research in Digital Media Technologies (MAR)**.

Von dieser Seite helfe ich dir gern bei Fragen zu Modulen, Projekten oder allgemeine Informationen zum Studiengang MAR.`,
      `Wenn du Informationen zu anderen Studiengängen suchst, besuche bitte die jeweilige Studiengangsseite:
- [Bachelor Ton und Bild (BTB)](/2026-FBM-Web-KI-Chatbot/navigation/btb.html)
- [Bachelor Medientechnik (BMT)](/2026-FBM-Web-KI-Chatbot/navigation/bmt.html)
- [Bachelor Creative, Synthetic and Interactive Media (BCSIM)](/2026-FBM-Web-KI-Chatbot/navigation/bcsim.html)
- [Bachelor Data Science, AI und Intelligente Systeme (BDAISY)](/2026-FBM-Web-KI-Chatbot/navigation/bdaisy.html)
- [Bachelor Medieninformatik (BMI)](/2026-FBM-Web-KI-Chatbot/navigation/bmi.html)
- [Master Medieninformatik (MMI)](/2026-FBM-Web-KI-Chatbot/navigation/mmi.html)`,
  `Für allgemeine Informationen zum Fachbereich Medien besuche die **[Hauptseite des Fachbereichs Medien](https://marmann.hosting.medien.hs-duesseldorf.de/2026-FBM-Web-KI-Chatbot/)**.`
    ],
    suggestions: [
      'Welche Voraussetzungen gelten für den MAR Studiengang?',
      'Welche Themen kann man erforschen?',
      'Wann startet der MAR-Studiengang?',
    ],
  },
};
