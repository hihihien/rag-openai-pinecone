import Chatbot from "@/app/components/Chatbot";

export default function BTBPage() {
  return (
    <main className='p-6 space-y-6'>
      <h1 className='text-2xl font-bold'>B.Eng. Ton und Bild</h1>
      <p>
        Willkommen auf der Informationsseite zum B.Eng. Ton und Bild am
        Fachbereich Medien der Hochschule Düsseldorf. Hier finden Sie alle wichtigen
        Informationen zu diesem Studiengang.
      </p>
      <Chatbot program="BTB" />
    </main>
  );
}