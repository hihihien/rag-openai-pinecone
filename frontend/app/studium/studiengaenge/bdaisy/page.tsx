import Chatbot from "@/app/components/Chatbot";

export default function BDAISYPage() {
  return (
    <main className='p-6 space-y-6'>
      <h1 className='text-2xl font-bold'>B. Sc. DAISY (ZDD)</h1>
      <p>
        Willkommen auf der Informationsseite zum B. Sc. DAISY (ZDD) am
        Fachbereich Medien der Hochschule Düsseldorf. Hier finden Sie alle wichtigen
        Informationen zu diesem Studiengang.
      </p>
      <Chatbot program="BDAISY" />
    </main>
  );
}