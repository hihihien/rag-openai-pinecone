import Chatbot from "@/app/components/Chatbot";

export default function MMIPage() {
  return (
    <main className='p-6 space-y-6'>
      <h1 className='text-2xl font-bold'>M.Sc. Medieninformatik</h1>
      <p>
        Willkommen auf der Informationsseite zum Masterstudiengang Medieninformatik (MMI) am
        Fachbereich Medien der Hochschule Düsseldorf. Hier finden Sie alle wichtigen
        Informationen zu diesem Studiengang.
      </p>
      <Chatbot program="MMI" />
    </main>
  );
}