import Chatbot from "@/app/components/Chatbot";

export default function BMTPage() {
  return (
    <main className='p-6 space-y-6'>
      <h1 className='text-2xl font-bold'>B.Eng. Medientechnik</h1>
      <p>
        Willkommen auf der Informationsseite zum Bachelorstudiengang Medientechnik (BMT) am
        Fachbereich Medien der Hochschule Düsseldorf. Hier finden Sie alle wichtigen
        Informationen zu diesem Studiengang.
      </p>
      <Chatbot program="BMT" />
    </main>
  );
}