import Chatbot from "./components/Chatbot";
import Link from "next/link";

export default function HomePage() {
  return (
    <main className="p-6 space-y-8">
      <h1 className="text-2xl font-bold">Willkommen im Fachbereich Medien</h1>
      <p>
        Hier findest du allgemeine Informationen über alle Studiengänge,
        Bewerbung, Studienstart und mehr.
      </p>

      {/* Study program links */}
      <section className="space-y-6">
        <div>
          <h2 className="text-lg font-semibold mb-2">Bachelorstudium</h2>
          <ul className="list-disc list-inside space-y-1">
            <li>
              <Link href="/studium/studiengaenge/btb" target="_blank" className="text-red-600 underline hover:text-red-800">
                B. Eng. Ton und Bild
              </Link>
            </li>
            <li>
              <Link href="/studium/studiengaenge/bmt" target="_blank" className="text-red-600 underline hover:text-red-800">
                B. Eng. Medientechnik
              </Link>
            </li>
            <li>
              <Link href="/studium/studiengaenge/bcsim" target="_blank" className="text-red-600 underline hover:text-red-800">
                B. A. CSIM (ab WS 27/28)
              </Link>
            </li>
            <li>
              <Link href="/studium/studiengaenge/bmi" target="_blank" className="text-red-600 underline hover:text-red-800">
                B. Sc. Medieninformatik
              </Link>
            </li>
            <li>
              <Link href="/studium/studiengaenge/bdaisy" target="_blank" className="text-red-600 underline hover:text-red-800">
                B. Sc. DAISY (ZDD)
              </Link>
            </li>
          </ul>
        </div>

        <div>
          <h2 className="text-lg font-semibold mb-2">Masterstudium</h2>
          <ul className="list-disc list-inside space-y-1">
            <li>
              <Link href="/studium/studiengaenge/mmi" target="_blank" className="text-red-600 underline hover:text-red-800">
                M. Sc. Medieninformatik
              </Link>
            </li>
            <li>
              <Link href="/studium/studiengaenge/mar" target="_blank" className="text-red-600 underline hover:text-red-800">
                M. Sc. Applied Research (ab WS 27/28)
              </Link>
            </li>
          </ul>
        </div>
      </section>

      {/* Chatbot */}
      <Chatbot program="default" />
    </main>
  );
}