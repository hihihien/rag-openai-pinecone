type ChatbotContext = {
  greeting: string;
  suggestions: string[];
};

export const chatbotContexts: Record<string, ChatbotContext> = {
  default: {
    greeting: `👋 Hallo! Ich bin **MeDi**, dein KI-Assistent der **Fachbereich Medien** an der Hochschule Düsseldorf.

Frag mich alles rund ums Studium, Studiengänge, Bewerbungen oder Module.`,
    suggestions: [
      'Welche Bachelorstudiengänge gibt es?',
      'Wie kann ich mich für ein Studium bewerben?',
      'Wo finde ich den Modulhandbuch-Link?',
    ],
  },
  MMI: {
    greeting: `👋 Willkommen! Du befindest dich auf der Seite des **Masterstudiengangs Medieninformatik (MMI)**.

Ich helfe dir gern bei Fragen zu Modulen, Projekten oder dem Ablauf des Studiums.`,
    suggestions: [
      'Welche Vertiefungen gibt es im MMI?',
      'Wie lange dauert der Master Medieninformatik?',
      'Wie läuft die Bewerbung für den MMI ab?',
    ],
  },
  BMI: {
    greeting: `👋 Willkommen im **Bachelorstudiengang Medieninformatik (BMI)**!

Ich beantworte dir Fragen zu Modulen, Prüfungen, Praktika und mehr.`,
    suggestions: [
      'Welche Module sind im 1. Semester BMI?',
      'Wer betreut die Bachelorarbeit im BMI?',
      'Wie viele CP hat das Modul "Database Systems 1"?',
    ],
  },
  BTB: {
    greeting: `👋 Willkommen im **Bachelorstudiengang Ton und Bild (BTB)**!

Frag mich gerne zu Studiotechnik, Modulen oder Praxisprojekten.`,
    suggestions: [
      'Was sind die technischen Schwerpunkte im BTB?',
      'Wie läuft das Praxissemester im BTB ab?',
      'Wer unterrichtet im Modul "Audio Produktion"?',
    ],
  },
  BMT: {
    greeting: `👋 Willkommen im **Bachelorstudiengang Medientechnik (BMT)**!

Ich kann dir bei Fragen zu den Modulinhalten, Praktika und Studienablauf helfen.`,
    suggestions: [
      'Wie viele CP hat das Modul "Video Technology"?',
      'Welche Wahlfächer gibt es im BMT?',
      'Wie sieht das 3. Semester aus?',
    ],
  },
  BDAISY: {
    greeting: `👋 Willkommen im **Bachelorstudiengang Data Science, AI und Intelligente Systeme (BDAISY)**!

Frag mich zu KI-Methoden, Data Engineering oder Modulen im Studium.`,
    suggestions: [
      'Welche Module decken Machine Learning ab?',
      'Wie funktioniert die Eignungsprüfung bei BDAISY?',
      'Gibt es Praxisprojekte im Studium?',
    ],
  },
  BCSIM: {
    greeting: `👋 Willkommen im **Bachelorstudiengang Creative, Synthetic and Interactive Media (BCSIM)**!

Ich helfe dir mit Infos über Inhalte, Ablauf und Zugangsvoraussetzungen.`,
    suggestions: [
      'Was ist das Ziel des BCSIM-Studiengangs?',
      'Welche Module werden im BCSIM angeboten?',
      'Wie kreativ ist das Studium?',
    ],
  },
  MAR: {
    greeting: `👋 Willkommen im **Masterstudiengang Applied Research in Digital Media Technologies (MAR)**!

Ich unterstütze dich bei Fragen zu Forschungsschwerpunkten und Studienablauf.`,
    suggestions: [
      'Welche Voraussetzungen gelten für den MAR Master?',
      'Welche Themen kann man erforschen?',
      'Wann startet der MAR-Studiengang?',
    ],
  },
};