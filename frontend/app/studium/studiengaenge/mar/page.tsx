import Chatbot from "@/app/components/Chatbot";

export default function MARPage() {
  return (
    <main className='p-6 space-y-6'>
      <h1 className='text-2xl font-bold'>Master (M.Sc.)​​ Applied Research in Digital Media Technologies</h1>
      <p>
        Willkommen auf der Informationsseite zum M.Sc. Applied Research in Digital Media Technologies am
        Fachbereich Medien der Hochschule Düsseldorf. Hier finden Sie alle wichtigen
        Informationen zu diesem Studiengang.
      </p>
      <Chatbot program="MAR" />
    </main>
  );
}